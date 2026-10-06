from typing import List, Dict, Any, Optional

def calculate_subject_velocity(
    completed_sessions: List[Dict[str, Any]],
    topic_est_hours_map: Optional[Dict[str, float]] = None,
    min_clamp: float = 0.5,
    max_clamp: float = 2.5
) -> float:
    """
    Calculates subject velocity ratio: average(actual_minutes / estimated_minutes)
    for completed study sessions.
    Default: 1.0. Clamped between min_clamp (0.5) and max_clamp (2.5).
    """
    if not completed_sessions:
        return 1.0

    ratios = []
    topic_est_hours_map = topic_est_hours_map or {}

    for sess in completed_sessions:
        status = sess.get("status")
        if status != "done":
            continue

        actual_mins = sess.get("actual_minutes")
        if actual_mins is None or actual_mins <= 0:
            continue

        planned_mins = sess.get("planned_minutes")
        
        # Fallback to topic estimated hours if planned_minutes is missing/zero
        if not planned_mins or planned_mins <= 0:
            topic_id = str(sess.get("topic_id", ""))
            est_hours = topic_est_hours_map.get(topic_id, 0.0)
            if est_hours > 0:
                planned_mins = int(est_hours * 60)

        if planned_mins and planned_mins > 0:
            ratio = actual_mins / planned_mins
            # Ignore extreme noise per session before averaging if ratio is invalid
            if ratio > 0:
                ratios.append(ratio)

    if not ratios:
        return 1.0

    avg_velocity = sum(ratios) / len(ratios)

    # Clamp result
    clamped_velocity = max(min_clamp, min(max_clamp, avg_velocity))
    return round(clamped_velocity, 4)


def get_all_subject_velocities(
    sessions: List[Dict[str, Any]],
    topic_est_hours_map: Optional[Dict[str, float]] = None,
    min_clamp: float = 0.5,
    max_clamp: float = 2.5
) -> Dict[str, float]:
    """
    Groups completed sessions by subject_id and calculates velocity for each subject.
    """
    subject_sessions: Dict[str, List[Dict[str, Any]]] = {}
    for sess in sessions:
        if sess.get("status") == "done":
            sub_id = str(sess.get("subject_id", "default"))
            if sub_id not in subject_sessions:
                subject_sessions[sub_id] = []
            subject_sessions[sub_id].append(sess)

    velocities = {}
    for sub_id, sess_list in subject_sessions.items():
        velocities[sub_id] = calculate_subject_velocity(
            sess_list, topic_est_hours_map, min_clamp, max_clamp
        )
    return velocities
