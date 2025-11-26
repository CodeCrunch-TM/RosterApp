from datetime import datetime #this entire thing is AI, purely for testing functionality we can delete later
import os
import sys

# ensure project root is on sys.path so `App` package is importable during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from App.models.SingleRosterFactory import SingleRosterFactory
from App.models.GroupRosterFactory import GroupRosterFactory


def safe_schedule_repr(schedule):
    return {
        "id": getattr(schedule, "id", None),
        "name": schedule.name,
        "created_by": schedule.created_by,
        "shift_count": len(schedule.shifts),
        "shifts": [
            {
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "staff_id": getattr(s, "staff_id", None),
                "staff_username": getattr(s, "staff", None).username if getattr(s, "staff", None) else None,
            }
            for s in schedule.shifts
        ],
    }


def test_single_roster_factory_creates_schedule_with_shifts():
    data = {
        "name": "Week 1",
        "created_by": 1,
        "shifts": [
            {"start_time": datetime(2025, 1, 1, 9), "end_time": datetime(2025, 1, 1, 17), "staff": 42},
            {"start_time": datetime(2025, 1, 2, 9), "end_time": datetime(2025, 1, 2, 17), "staff": {"username": "alice", "password": "pw"}},
        ],
    }

    factory = SingleRosterFactory()
    schedule = factory.createRoster(data)

    # print a safe representation (don't call Schedule.get_json — created_at is
    # only populated after DB insert, so avoid .isoformat() on None)
    print("SingleRosterFactory produced:", safe_schedule_repr(schedule))

    assert schedule.name == "Week 1"
    assert schedule.created_by == 1
    assert len(schedule.shifts) == 2

    s0 = schedule.shifts[0]
    s1 = schedule.shifts[1]

    # first shift used staff id
    assert getattr(s0, "staff_id", None) == 42

    # second shift should have a Staff instance attached
    assert getattr(s1, "staff", None) is not None
    assert s1.staff.username == "alice"


def test_group_roster_factory_builds_multiple():
    group_data = [
        {"name": "A", "created_by": 2, "shifts": [{"start_time": datetime(2025, 1, 3, 9), "end_time": datetime(2025, 1, 3, 17), "staff": 7} ]},
        {"name": "B", "created_by": 3, "shifts": []},
    ]

    factory = GroupRosterFactory()
    schedule_group = factory.createRoster(group_data)

    # print all schedules produced by the group factory using the safe repr
    print("GroupRosterFactory produced:", [safe_schedule_repr(s) for s in schedule_group.schedules])

    # schedule_group is a ScheduleGroup container
    assert hasattr(schedule_group, "schedules")
    assert len(schedule_group.schedules) == 2
    assert schedule_group.schedules[0].name == "A"
    assert schedule_group.schedules[1].name == "B"
    assert len(schedule_group.schedules[0].shifts) == 1
    assert schedule_group.schedules[0].shifts[0].staff_id == 7
