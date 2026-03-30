import logging
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# GitHub API client
github = requests.Session()
github.headers.update({
    "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": settings.API_VERSION,
})

NINETY_DAYS_CUTOFF = timedelta(days=90)
MAX_RETRIES = 3


def _is_rate_limited(resp: requests.Response) -> bool:
    return resp.status_code == 403 and "rate limit" in resp.text.lower()


def _wait_for_rate_limit_reset(resp: requests.Response) -> None:
    reset_timestamp = resp.headers.get("X-RateLimit-Reset")
    if reset_timestamp:
        sleep_seconds = int(reset_timestamp) - time.time() + 1
        if sleep_seconds > 0:
            logger.warning("Rate limited. Waiting %d seconds.", sleep_seconds)
            time.sleep(sleep_seconds)
    else:
        time.sleep(60)


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    for attempt in range(MAX_RETRIES):
        resp = github.request(method, url, **kwargs)
        if not _is_rate_limited(resp):
            return resp
        if attempt < MAX_RETRIES - 1:
            _wait_for_rate_limit_reset(resp)
    return resp


def _is_too_old(item_date: datetime) -> bool:
    """Return True if the item is older than 90 days."""
    return item_date < (datetime.now(timezone.utc) - NINETY_DAYS_CUTOFF)


def _extract_date(item: dict[str, Any], key: str = "created_at") -> datetime | None:
    """Safely parse an ISO date from a dict."""
    val = item.get(key)
    if val is None:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def fetch_all_prs(owner: str, repo: str, max_pages: int = 10) -> list[dict[str, Any]]:
    """
    Paginated PR fetch with 90-day cutoff.
    Returns closed PRs sorted by updatedAt, most recent first.
    """
    all_prs = []
    for page in range(1, max_pages + 1):
        resp = _request_with_retry(
            "GET",
            f"{settings.BASE_URL}/repos/{owner}/{repo}/pulls",
            params={"state": "closed", "per_page": 100, "page": page, "sort": "updated", "direction": "desc"},
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info("Fetched PRs page %d for %s/%s", page, owner, repo)

        if not data:
            break

        all_prs.extend(data)

        oldest = _extract_date(data[-1], "created_at")
        if oldest is None or _is_too_old(oldest):
            break

    return all_prs


def fetch_pr_reviews(owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
    """
    Fetch all reviews for a single PR.
    """
    resp = _request_with_retry(
        "GET",
        f"{settings.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/reviews",
    )
    resp.raise_for_status()
    return resp.json()


def fetch_workflow_runs(owner: str, repo: str, max_pages: int = 5) -> list[dict[str, Any]]:
    """
    Paginated workflow runs fetch with 90-day cutoff.
    """
    all_runs = []
    for page in range(1, max_pages + 1):
        resp = _request_with_retry(
            "GET",
            f"{settings.BASE_URL}/repos/{owner}/{repo}/actions/runs",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        payload = resp.json()
        runs = payload.get("workflow_runs", [])
        logger.info("Fetched %d workflow runs page %d for %s/%s", len(runs), page, owner, repo)

        if not runs:
            break

        all_runs.extend(runs)

        oldest = _extract_date(runs[-1], "created_at")
        if oldest is None or _is_too_old(oldest):
            break

    return all_runs


def fetch_run_jobs(owner: str, repo: str, run_id: int) -> list[dict[str, Any]]:
    """
    Fetch individual jobs (steps) for a specific workflow run.
    """
    resp = _request_with_retry(
        "GET",
        f"{settings.BASE_URL}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
    )
    resp.raise_for_status()
    return resp.json().get("jobs", [])