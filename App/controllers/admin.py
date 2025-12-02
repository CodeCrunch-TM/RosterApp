from App.models import Schedule, Shift
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
