from typing import List, Dict, Any

def run_triage_analysis(
    topics: List[Dict[str, Any]],
    deficit_hours: float,
    subject_name: str = ""
) -> Dict[str, Any]:
    """
    Analyzes topics for triage when workload is infeasible (deficit_hours > 0).
    Ranks topics by value density ratio = (weight / estimated_hours).
    Lowest ratio topics are recommended first for compression or deprioritization.
    """
    if deficit_hours <= 0:
        return {
            "deficit_hours": 0.0,
            "status": "FEASIBLE",
            "recommendations": [],
            "message": "Workload is feasible. No triage needed."
        }

    active_topics = [
        t for t in topics
        if t.get("status") != "completed" and float(t.get("mastery", 0.0)) < 1.0
    ]

    scored = []
    for t in active_topics:
        est = float(t.get("est_hours", 1.0))
        weight = float(t.get("weight", 1))
        mastery = float(t.get("mastery", 0.0))
        rem_hours = est * (1.0 - mastery)
        ratio = weight / max(est, 0.1)

        scored.append({
            "topic_id": str(t.get("id", t.get("_id", ""))),
            "name": t.get("name", "Untitled Topic"),
            "weight": weight,
            "est_hours": est,
            "remaining_hours": round(rem_hours, 1),
            "ratio": round(ratio, 4)
        })

    # Sort lowest ratio first (lowest return on investment of study time)
    scored.sort(key=lambda x: (x["ratio"], -x["remaining_hours"]))

    recommendations = []
    accumulated_reduction = 0.0

    for item in scored:
        if accumulated_reduction >= deficit_hours:
            break

        rem_h = item["remaining_hours"]
        # Options: Compress (50% reduction) or Drop (100% reduction)
        compress_savings = round(rem_h * 0.5, 1)
        drop_savings = rem_h

        if item["ratio"] <= 0.8:
            action = "drop"
            savings = drop_savings
            reason = f"Low exam weight ({item['weight']}) compared to high effort ({item['est_hours']}h). Value ratio: {item['ratio']}."
        else:
            action = "compress"
            savings = compress_savings
            reason = f"Moderate value ratio ({item['ratio']}). Compressing target study time by 50% frees up {savings}h."

        accumulated_reduction += savings
        recommendations.append({
            "topic_id": item["topic_id"],
            "topic_name": item["name"],
            "weight": item["weight"],
            "est_hours": item["est_hours"],
            "remaining_hours": item["remaining_hours"],
            "value_ratio": item["ratio"],
            "recommended_action": action,
            "potential_savings_hours": savings,
            "reason": reason
        })

    return {
        "subject_name": subject_name,
        "deficit_hours": round(deficit_hours, 1),
        "status": "INFEASIBLE",
        "total_potential_savings": round(accumulated_reduction, 1),
        "unresolved_deficit": round(max(0.0, deficit_hours - accumulated_reduction), 1),
        "recommendations": recommendations,
        "message": f"Triage suggestions generated to address {deficit_hours}h deficit."
    }
