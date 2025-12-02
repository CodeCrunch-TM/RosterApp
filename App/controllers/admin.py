from App.models import Schedule, Shift
from App.controllers.user import get_user
from App.database import db
from datetime import datetime

from App.models import Schedule, Shift
from App.models.strategies import (
    EvenDistributionStrategy,
    MinimizeDaySchedulingStrategy,
    DayNightBalancedScheduling
)

def create_schedule(admin_id, schedule_name):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can create schedules")

    new_schedule = Schedule(
        name=schedule_name,
        created_by=admin.id,
        created_at=datetime.utcnow()
    )

    db.session.add(new_schedule)
    db.session.commit()

    return new_schedule


def schedule_shift(admin_id, staff, schedule, start_time, end_time):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can schedule shifts")

    if not staff or staff.role != "staff":
        raise ValueError("Invalid staff member")

    if not schedule:
        raise ValueError("Invalid schedule")

    new_shift = Shift(
        staff_id=staff.id,
        schedule_id=schedule.id,
        start_time=start_time,
        end_time=end_time
    )

    db.session.add(new_shift)
    db.session.commit()

    return new_shift


def get_shift_report(admin_id):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can view shift reports")

    shifts = Shift.query.order_by(Shift.start_time).all()
    return [shift.get_json() for shift in shifts]


# Auto-populate schedule using a given strategy
def auto_populate_schedule(admin_id, schedule_group_id, shifts, strategy_name="even"):

    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can auto-populate schedules")

    # Fetch staff list
    from App.models import Staff
    staff = Staff.query.all()
    if not staff:
        raise ValueError("No staff members available")

    # Strategy lookup
    strategies = {
        "even": EvenDistributionStrategy(),
        "minimize_days": MinimizeDaySchedulingStrategy(),
        "day_night": DayNightBalancedScheduling()
    }

    strategy = strategies.get(strategy_name)
    if not strategy:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    # Generate schedule using strategy
    schedule_group = strategy.generateSchedule(shifts, staff)
    schedule_group.id = schedule_group_id

    db.session.add(schedule_group)
    db.session.commit()

    # Observer pattern: notify staff of new assignment
    for staff_member in staff:
        schedule_group.attach(staff_member)

    schedule_group.notifyObservers()

    return schedule_group
