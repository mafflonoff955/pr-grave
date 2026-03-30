import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from cachetools import TTLCache

from app.routes.github import fetch_all_prs, fetch_pr_reviews, fetch_workflow_runs
from app.lib.pr_analyzer import aggregate_pr_metrics
from app.lib.ci_analyzer import analyze_ci_runs
from app.lib.cost_calc import calculate_wasted_hours

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])

cache: TTLCache = TTLCache(maxsize=128, ttl=300)


class AnalyzeRequest(BaseModel):
    repoUrl: str = Field(..., description="GitHub repo URL or 'owner/repo' string")
    teamSize: int = Field(default=8, ge=1, le=100)
    hourlyRate: float = Field(default=75.0, ge=1)


def parse_repo(repo_url: str) -> tuple[str, str]:
    """
    Parse owner and repo from:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - owner/repo
    """
    repo_url = repo_url.strip()

    # First try simple owner/repo format (no URL prefix)
    parts = repo_url.split("/")
    if len(parts) == 2 and "." not in parts[0] and "." not in parts[1]:
        return parts[0], parts[1]

    # Then try full GitHub URL
    match = re.search(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?$", repo_url)
    if match:
        return match.group(1), match.group(2)

    raise ValueError(f"Invalid repository URL or format: {repo_url}")


def _parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _fetch_reviews_for_pr(owner: str, repo: str, pr: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    try:
        reviews = fetch_pr_reviews(owner, repo, pr["number"])
        return pr["number"], reviews
    except Exception as e:
        logger.warning("Failed to fetch reviews for PR #%d: %s", pr["number"], e)
        return pr["number"], []  # noqa: RUF006


@router.post("/analyze")
async def analyze_repo(body: AnalyzeRequest) -> dict[str, Any]:
    """
    Main entry point. Fetches PRs, reviews, CI runs; computes all metrics; returns analysis.
    Results are cached for 5 minutes per repository.
    """
    try:
        owner, repo = parse_repo(body.repoUrl)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    cache_key = f"{owner}/{repo}"
    if cache_key in cache:
        cached = cache[cache_key].copy()
        cached["fromCache"] = True
        return cached

    logger.info("Analyzing %s/%s...", owner, repo)

    try:
        all_prs = fetch_all_prs(owner, repo)
        recent_prs = all_prs[:200]

        sample_prs = recent_prs[:50]
        all_reviews: list[list[dict[str, Any]]] = [[] for _ in sample_prs]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(_fetch_reviews_for_pr, owner, repo, pr): i
                for i, pr in enumerate(sample_prs)
            }
            for future in as_completed(futures):
                i = futures[future]
                try:
                    pr_number, reviews = future.result()
                    all_reviews[i] = reviews
                except Exception as e:
                    logger.error("Error fetching reviews for index %d: %s", i, e)

        try:
            ci_runs = fetch_workflow_runs(owner, repo)
        except Exception as e:
            logger.warning("Failed to fetch CI runs for %s/%s: %s", owner, repo, e)
            ci_runs = []

        pr_metrics = aggregate_pr_metrics(sample_prs, all_reviews)
        ci_metrics = analyze_ci_runs(ci_runs)

        ci_metrics_fallback = ci_metrics is None
        if ci_metrics is None:
            ci_metrics = {
                "failureRate": 20,
                "avgDurationMinutes": 10,
                "totalRuns": 0,
                "workflows": [],
            }

        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        prs_last_month = sum(
            1 for pr in all_prs
            if (merged_at := _parse_date(pr.get("merged_at"))) is not None
            and merged_at > thirty_days_ago
        )

        cost_analysis = calculate_wasted_hours(
            avg_time_to_first_review=pr_metrics["avgTimeToFirstReview"],
            avg_time_to_merge=pr_metrics["avgTimeToMerge"],
            avg_ci_duration_minutes=ci_metrics["avgDurationMinutes"],
            ci_failure_rate=ci_metrics["failureRate"],
            total_prs_per_month=max(prs_last_month, 1),
            team_size=body.teamSize,
            hourly_rate=body.hourlyRate,
        )

        result = {
            "repo": f"{owner}/{repo}",
            "scannedAt": datetime.now(timezone.utc).isoformat(),
            "prMetrics": pr_metrics,
            "ciMetrics": ci_metrics,
            "costAnalysis": cost_analysis,
            "prsAnalyzed": len(sample_prs),
            "totalPRsFetched": len(all_prs),
            "prsLastMonth": prs_last_month,
            "fromCache": False,
            "ciMetricsFallback": ci_metrics_fallback,
        }

        cache[cache_key] = result
        logger.info("Analysis complete for %s/%s", owner, repo)
        return result

    except Exception as e:
        logger.error("Error analyzing %s/%s: %s", owner, repo, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )