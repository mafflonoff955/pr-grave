from datetime import datetime, timezone
from typing import Any

from app.routes.github import _extract_date


def calc_time_to_first_review(pr: dict[str, Any], reviews: list[dict[str, Any]]) -> float | None:
    """
    Hours from PR open to first non-pending review.
    Returns None if no reviews found.
    """
    if not reviews:
        return None

    pr_opened_at = _extract_date(pr, "created_at")
    if pr_opened_at is None:
        return None

    # Filter out PENDING and COMMENTED reviews (only APPROVED or CHANGES_REQUESTED count)
    actionable_reviews = [
        r for r in reviews
        if r.get("state") in ("APPROVED", "CHANGES_REQUESTED")
    ]

    if not actionable_reviews:
        return None

    first = min(
        actionable_reviews,
        key=lambda r: _extract_date(r, "submitted_at") or datetime.max.replace(tzinfo=timezone.utc)
    )

    first_at = _extract_date(first, "submitted_at")
    if first_at is None:
        return None

    return (first_at - pr_opened_at).total_seconds() / 3600  # hours


def calc_time_to_merge(pr: dict[str, Any]) -> float | None:
    """
    Hours from PR open to merge. Returns None if PR was not merged.
    """
    if not pr.get("merged_at"):
        return None

    opened = _extract_date(pr, "created_at")
    merged = _extract_date(pr, "merged_at")

    if opened is None or merged is None:
        return None

    return (merged - opened).total_seconds() / 3600  # hours


def calc_pr_size(pr: dict[str, Any]) -> int:
    """Total lines changed (additions + deletions)."""
    return (pr.get("additions") or 0) + (pr.get("deletions") or 0)


def build_reviewer_load_map(
    prs: list[dict[str, Any]],
    all_reviews: list[list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """
    Build reviewer load map: { username: { reviewed: N, approved: N, changeRequested: N, totalWaitHours: float } }
    """
    load_map: dict[str, dict[str, Any]] = {}

    for pr, reviews in zip(prs, all_reviews):
        pr_opened = _extract_date(pr, "created_at")

        for review in reviews:
            user = review.get("user", {})
            username = user.get("login")
            if not username:
                continue

            if username not in load_map:
                load_map[username] = {
                    "reviewed": 0,
                    "approved": 0,
                    "changeRequested": 0,
                    "totalWaitHours": 0.0,
                }

            state = review.get("state")
            if state in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED"):
                load_map[username]["reviewed"] += 1

                if state == "APPROVED":
                    load_map[username]["approved"] += 1
                elif state == "CHANGES_REQUESTED":
                    load_map[username]["changeRequested"] += 1

                # Track wait time for this review
                if pr_opened:
                    submitted = _extract_date(review, "submitted_at")
                    if submitted:
                        load_map[username]["totalWaitHours"] += (
                            submitted - pr_opened
                        ).total_seconds() / 3600

        # Track requested reviewers (who was asked to review but may not have responded)
        for rr in pr.get("requested_reviewers", []):
            username = rr.get("login")
            if username and username not in load_map:
                load_map[username] = {
                    "reviewed": 0,
                    "approved": 0,
                    "changeRequested": 0,
                    "totalWaitHours": 0.0,
                }

    return load_map


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    return sorted_vals[mid] if n % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2


def aggregate_pr_metrics(
    prs: list[dict[str, Any]],
    all_reviews: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    """
    Aggregate all PR metrics into a summary dict.
    Ignores outliers beyond 720 hours (30 days).
    """
    ttfr: list[float] = []  # time to first review
    ttm: list[float] = []   # time to merge
    sizes: list[int] = []

    for pr, reviews in zip(prs, all_reviews):
        first_review_time = calc_time_to_first_review(pr, reviews)
        merge_time = calc_time_to_merge(pr)
        size = calc_pr_size(pr)

        if first_review_time is not None and first_review_time < 720:
            ttfr.append(first_review_time)
        if merge_time is not None and merge_time < 720:
            ttm.append(merge_time)
        sizes.append(size)

    return {
        "totalPRs": len(prs),
        "avgTimeToFirstReview": round(_mean(ttfr), 2),
        "medianTimeToFirstReview": round(_median(ttfr), 2),
        "avgTimeToMerge": round(_mean(ttm), 2),
        "medianTimeToMerge": round(_median(ttm), 2),
        "avgPRSize": round(_mean(sizes), 2),
        "largePRs": sum(1 for s in sizes if s > 500),
        "reviewerLoad": build_reviewer_load_map(prs, all_reviews),
    }