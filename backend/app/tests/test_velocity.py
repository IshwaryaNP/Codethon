import pytest
from app.services.velocity import calculate_subject_velocity, get_all_subject_velocities

def test_velocity_no_history():
    vel = calculate_subject_velocity([])
    assert vel == 1.0, "Velocity should default to 1.0 when no history exists"

def test_velocity_slower_student():
    # Student took 90 minutes for a 60 minute planned session (ratio 1.5)
    sessions = [{"status": "done", "actual_minutes": 90, "planned_minutes": 60}]
    vel = calculate_subject_velocity(sessions)
    assert vel == 1.5

def test_velocity_faster_student():
    # Student took 30 minutes for a 60 minute planned session (ratio 0.5)
    sessions = [{"status": "done", "actual_minutes": 30, "planned_minutes": 60}]
    vel = calculate_subject_velocity(sessions)
    assert vel == 0.5

def test_velocity_clamping():
    # Extreme slow student taking 5x expected time
    sessions_slow = [{"status": "done", "actual_minutes": 500, "planned_minutes": 100}]
    vel_slow = calculate_subject_velocity(sessions_slow)
    assert vel_slow == 2.5, "Velocity must be clamped to upper bound 2.5"

    # Extreme fast student taking 0.1x expected time
    sessions_fast = [{"status": "done", "actual_minutes": 10, "planned_minutes": 100}]
    vel_fast = calculate_subject_velocity(sessions_fast)
    assert vel_fast == 0.5, "Velocity must be clamped to lower bound 0.5"

def test_velocity_grouping():
    sessions = [
        {"subject_id": "sub1", "status": "done", "actual_minutes": 120, "planned_minutes": 60},
        {"subject_id": "sub2", "status": "done", "actual_minutes": 30, "planned_minutes": 60},
        {"subject_id": "sub1", "status": "missed", "actual_minutes": 0, "planned_minutes": 60}
    ]
    vel_map = get_all_subject_velocities(sessions)
    assert vel_map["sub1"] == 2.0
    assert vel_map["sub2"] == 0.5
