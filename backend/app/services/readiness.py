import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

def get_day_name(dt: date) -> str:
    return dt.strftime("%A").lower()

def calculate_exam_readiness(
    exam_id: str,
    exam_title: str,
    exam_date: date,
    topics: List[Dict[str, Any]],
    availability: Dict[str, float],
    completed_sessions: List[Dict[str, Any]],
    today: date,
    buffer_ratio: float = 0.20,
    simulations_count: int = 1000,
    random_seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Monte Carlo simulation for Exam Readiness Probability (1000 runs).
    Returns readiness percentage, remaining hours, available capacity, and status.
    """
    if random_seed is not None:
        random.seed(random_seed)

    # Calculate base unadjusted remaining workload hours for topics of this subject
    unadjusted_remaining_hours = 0.0
    for t in topics:
        if t.get("status") != "completed":
            est = float(t.get("est_hours", 1.0))
            mastery = max(0.0, min(1.0, float(t.get("mastery", 0.0))))
            unadjusted_remaining_hours += est * (1.0 - mastery)

    # Calculate usable available study hours between today and exam_date
    available_usable_hours = 0.0
    curr = today
    while curr <= exam_date:
        day_name = get_day_name(curr)
        raw_hours = float(availability.get(day_name, 2.0))
        available_usable_hours += raw_hours * (1.0 - buffer_ratio)
        curr += timedelta(days=1)

    # Compute mean velocity and std-dev from student history
    ratios = []
    for sess in completed_sessions:
        if sess.get("status") == "done":
            act = sess.get("actual_minutes")
            pln = sess.get("planned_minutes")
            if act and pln and act > 0 and pln > 0:
                ratios.append(act / pln)

    if len(ratios) >= 2:
        mean_vel = sum(ratios) / len(ratios)
        variance = sum((r - mean_vel) ** 2 for r in ratios) / (len(ratios) - 1)
        std_dev = max(0.05, variance ** 0.5)
    elif len(ratios) == 1:
        mean_vel = ratios[0]
        std_dev = 0.20
    else:
        mean_vel = 1.0
        std_dev = 0.20

    # Clamp mean velocity
    mean_vel = max(0.5, min(2.5, mean_vel))

    # Run Monte Carlo simulations
    successes = 0
    for _ in range(simulations_count):
        # Sample velocity from normal distribution
        sample_vel = random.gauss(mean_vel, std_dev)
        sample_vel = max(0.5, min(2.5, sample_vel))

        simulated_workload = unadjusted_remaining_hours * sample_vel
        if simulated_workload <= available_usable_hours:
            successes += 1

    probability_pct = round((successes / simulations_count) * 100.0, 1)

    is_feasible = available_usable_hours >= (unadjusted_remaining_hours * mean_vel)
    
    if probability_pct >= 75.0:
        readiness_status = "Ready"
    elif probability_pct >= 40.0:
        readiness_status = "At Risk"
    else:
        readiness_status = "Infeasible"

    return {
        "exam_id": exam_id,
        "exam_title": exam_title,
        "exam_date": exam_date.isoformat(),
        "remaining_hours": round(unadjusted_remaining_hours * mean_vel, 1),
        "available_hours": round(available_usable_hours, 1),
        "readiness_probability": probability_pct,
        "feasible": is_feasible,
        "status": readiness_status
    }
