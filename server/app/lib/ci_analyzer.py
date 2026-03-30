from typing import Any

from app.routes.github import _extract_date


def analyze_ci_runs(runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Compute failure rates, avg duration, and per-workflow breakdown.
    Returns None if runs is empty.
    """
    if not runs:
        return None

    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in completed if r.get("conclusion") == "failure"]
    successful = [r for r in completed if r.get("conclusion") == "success"]

    # Duration in minutes
    durations: list[float] = []
    for r in completed:
        started = _extract_date(r, "created_at")
        finished = _extract_date(r, "updated_at")
        if started and finished:
            durations.append((finished - started).total_seconds() / 60)

    def mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    # Group by workflow name
    by_workflow: dict[str, dict[str, Any]] = {}
    for r in completed:
        name = r.get("name") or "unknown"
        if name not in by_workflow:
            by_workflow[name] = {"runs": 0, "failures": 0, "totalDuration": 0.0}

        by_workflow[name]["runs"] += 1
        if r.get("conclusion") == "failure":
            by_workflow[name]["failures"] += 1

        started = _extract_date(r, "created_at")
        finished = _extract_date(r, "updated_at")
        if started and finished:
            by_workflow[name]["totalDuration"] += (finished - started).total_seconds() / 60

    workflow_stats = [
        {
            "name": name,
            "runs": stats["runs"],
            "failureRate": round((stats["failures"] / stats["runs"]) * 100, 2) if stats["runs"] else 0,
            "avgDurationMinutes": round(stats["totalDuration"] / stats["runs"], 2) if stats["runs"] else 0,
        }
        for name, stats in by_workflow.items()
    ]
    workflow_stats.sort(key=lambda w: w["avgDurationMinutes"], reverse=True)

    return {
        "totalRuns": len(completed),
        "failureRate": round((len(failed) / len(completed)) * 100, 2) if completed else 0,
        "avgDurationMinutes": round(mean(durations), 2),
        "workflows": workflow_stats,
    }