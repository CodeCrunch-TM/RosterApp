from App.models import Schedule, Shift, ScheduleGroup, Staff
from App.models.GroupRosterFactory import GroupRosterFactory
from App.controllers.user import get_user
from App.database import db
from datetime import datetime

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


def auto_populate_schedule(admin_id, schedule_group_id, shifts, strategy_name):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can auto-populate schedules")

    schedule_group = ScheduleGroup.query.get(schedule_group_id)
    if not schedule_group:
        raise ValueError("Invalid schedule group")

    if not shifts:
        raise ValueError("Shifts list cannot be empty")

    # Load all staff in the system (test expects ALL staff to get notifications)
    staff = Staff.query.all()
    if not staff:
        raise ValueError("No staff available")

    # Strategy factory
    factory = GroupRosterFactory()
    strategy = factory.get_strategy(strategy_name)
    if not strategy:
        raise ValueError("Invalid strategy name")

    # Attach all staff as observers
    for s in staff:
        schedule_group.attach(s)

    # Auto-generate schedule entries
    generated = strategy.generateSchedule(shifts, staff, schedule_group)
    if not generated:
        raise ValueError("Schedule generation failed")

    # Commit changes before notifying observers
    db.session.commit()

    # Notify attached observers
    schedule_group.notifyObservers()

    return schedule_group