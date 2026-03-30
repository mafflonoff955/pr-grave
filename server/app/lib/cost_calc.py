from typing import Any

DEFAULT_HOURLY_RATE = 75  # USD, conservative senior dev rate
DEFAULT_TEAM_SIZE = 8


def calculate_wasted_hours(
    *,
    avg_time_to_first_review: float,   # hours
    avg_time_to_merge: float,           # hours (unused in current model but kept for future)
    avg_ci_duration_minutes: float,    # minutes
    ci_failure_rate: float,             # 0-100 percentage
    total_prs_per_month: int,
    team_size: int = DEFAULT_TEAM_SIZE,
    hourly_rate: float = DEFAULT_HOURLY_RATE,
) -> dict[str, Any]:
    """
    Turn metrics into human cost.

    Cost components:
    - Context switch cost: ~23 min to regain deep focus after interruption (Research: Gloria Mark et al.)
    - Blocked wait time: assume 30% of review wait is non-parallelizable blocking
    - CI failure waste: failed run duration wasted
    - CI wait time: every PR author waits for CI to pass
    """
    context_switch_cost_per_pr = 23 / 60  # hours
    monthly_context_switch_hours = total_prs_per_month * context_switch_cost_per_pr

    blocked_time_per_pr = avg_time_to_first_review * 0.3
    monthly_blocked_hours = total_prs_per_month * blocked_time_per_pr

    # Assume each PR triggers ~2 CI runs (push + merge attempt)
    monthly_failed_run_hours = (total_prs_per_month * 2) * (ci_failure_rate / 100) * (avg_ci_duration_minutes / 60)

    monthly_ci_wait_hours = total_prs_per_month * (avg_ci_duration_minutes / 60)

    total_wasted_hours = (
        monthly_context_switch_hours
        + monthly_blocked_hours
        + monthly_failed_run_hours
        + monthly_ci_wait_hours
    )

    total_wasted_dollars = total_wasted_hours * hourly_rate

    return {
        "breakdown": {
            "contextSwitchHours": round(monthly_context_switch_hours, 1),
            "blockedWaitHours": round(monthly_blocked_hours, 1),
            "ciFailureWasteHours": round(monthly_failed_run_hours, 1),
            "ciWaitHours": round(monthly_ci_wait_hours, 1),
        },
        "totalWastedHoursPerMonth": round(total_wasted_hours),
        "totalWastedDollarsPerMonth": round(total_wasted_dollars),
    }


def simulate_improvement(
    *,
    current_avg_review_hours: float,
    target_avg_review_hours: float,
    current_ci_duration_minutes: float,
    target_ci_duration_minutes: float,
    total_prs_per_month: int,
    hourly_rate: float = DEFAULT_HOURLY_RATE,
) -> dict[str, Any]:
    """
    What-If calculation: how much would we recover if we improved review and CI times?
    """
    baseline_ci_failure_rate = 20.0  # assume 20% as a baseline when actual not available

    current_cost = calculate_wasted_hours(
        avg_time_to_first_review=current_avg_review_hours,
        avg_time_to_merge=0,  # not used in current model
        avg_ci_duration_minutes=current_ci_duration_minutes,
        ci_failure_rate=baseline_ci_failure_rate,
        total_prs_per_month=total_prs_per_month,
        hourly_rate=hourly_rate,
    )

    improved_cost = calculate_wasted_hours(
        avg_time_to_first_review=target_avg_review_hours,
        avg_time_to_merge=0,
        avg_ci_duration_minutes=target_ci_duration_minutes,
        ci_failure_rate=baseline_ci_failure_rate,
        total_prs_per_month=total_prs_per_month,
        hourly_rate=hourly_rate,
    )

    return {
        "currentCost": current_cost["totalWastedDollarsPerMonth"],
        "improvedCost": improved_cost["totalWastedDollarsPerMonth"],
        "savedHoursPerMonth": (
            current_cost["totalWastedHoursPerMonth"]
            - improved_cost["totalWastedHoursPerMonth"]
        ),
        "savedDollarsPerMonth": (
            current_cost["totalWastedDollarsPerMonth"]
            - improved_cost["totalWastedDollarsPerMonth"]
        ),
    }