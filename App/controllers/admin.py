from App.models import Admin, Schedule
from App.controllers.user import get_user
from App.database import db

def create_schedule(admin_id, schedule_name):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can create schedules")

    return admin.createSchedule(schedule_name)


def schedule_shift(admin_id, staff, schedule, start_time, end_time):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can schedule shifts")

    return admin.scheduleShift(staff, schedule, start_time, end_time)


def get_shift_report(admin_id):
    admin = get_user(admin_id)

    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can view shift reports")

    return admin.viewShift()
