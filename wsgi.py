import click, pytest, sys, os
from flask.cli import with_appcontext, AppGroup
from datetime import datetime, timedelta
from flask_jwt_extended import decode_token, verify_jwt_in_request, get_jwt_identity

from App.database import db, get_migrate
from App.models import User, Schedule
from App.main import create_app 
from App.controllers import (
    create_user, get_all_users_json, get_user, get_all_users, initialize,
    schedule_shift, get_combined_roster, clock_in, clock_out, get_shift_report,
    login, loginCLI
)

#App and Database initialization
app = create_app()
migrate = get_migrate(app)



#Initialize Database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')



#Authentication CLI commands
auth_cli = AppGroup('auth', help='Authentication commands')

@auth_cli.command("login", help="Login and get JWT token")
@click.argument("username")
@click.argument("password")
def login_command(username, password):
    result = loginCLI(username, password)
    if result["message"] == "Login successful":
        with open("active_token.txt", "w") as f:
            f.write(result["token"])
        print(f"✅ {result['message']}! JWT token saved for CLI use.")
    else:
        print(f"⚠️ {result['message']}")


@auth_cli.command("logout", help="Logout a user by username")
@click.argument("username")
def logout_command(username):
    from App.controllers.auth import logout
    result = logout(username)
    if os.path.exists("active_token.txt"):
        os.remove("active_token.txt")
    print(result["message"])
    
app.cli.add_command(auth_cli)



# User CLI commands
user_cli = AppGroup('user', help='User object commands') 

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
@click.argument("role", default="staff")
def create_user_command(username, password, role):
    create_user(username, password, role)
    print(f'{username} created!')

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli)



# Staff and Admin Authentication Helpers
def require_admin_login():
    if not os.path.exists("active_token.txt"):
        raise PermissionError("No active session. Please login.")

    with open("active_token.txt", "r") as f:
        token = f.read().strip()

    try:
        decoded = decode_token(token)
        user = get_user(decoded["sub"])
        if not user or user.role != "admin":
            raise PermissionError("Only an admin can use this command.")
        return user
    except Exception as e:
        raise PermissionError(f"Invalid or expired token. ({e})")


def require_staff_login():
    if not os.path.exists("active_token.txt"):
        raise PermissionError("No active session. Please login.")

    with open("active_token.txt", "r") as f:
        token = f.read().strip()

    try:
        decoded = decode_token(token)
        user = get_user(decoded["sub"])
        if not user or user.role != "staff":
            raise PermissionError("Only staff can use this command.")
        return user
    except Exception as e:
        raise PermissionError(f"Invalid or expired token. ({e})")



# Shift CLI commands
shift_cli = AppGroup('shift', help='Shift management commands')

@shift_cli.command("schedule", help="Admin schedules a shift and assigns it to a schedule")
@click.argument("staff_id", type=int)
@click.argument("schedule_id", type=int)
@click.argument("start")
@click.argument("end")

def schedule_shift_command(staff_id, schedule_id, start, end):
    admin = require_admin_login()
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    
    from App.controllers.user import get_user  # make sure you import

    staff = get_user(staff_id)
    if not staff:
        print(f"⚠️ No user found with ID {staff_id}")
        return
    if staff.role != "staff":
        print(f"⚠️ User {staff.username} is not staff (role={staff.role})")
        return
    
    
    schedule = db.session.get(Schedule, schedule_id)
    
    shift = schedule_shift(admin.id, staff, schedule, start_time, end_time)
    print(f"✅ Shift scheduled under Schedule {schedule_id} by {admin.username}:")
    print(shift.get_json())

@shift_cli.command("roster", help="Staff views combined roster")
def roster_command():
    staff = require_staff_login()
    roster = get_combined_roster(staff.id)
    print(f"📋 Roster for {staff.username}:")
    print(roster)


@shift_cli.command("clockin", help="Staff clocks in")
@click.argument("shift_id", type=int)
def clockin_command(shift_id):
    staff = require_staff_login()
    shift = clock_in(staff.id, shift_id)
    print(f"🕒 {staff.username} clocked in:")
    print(shift.get_json())


@shift_cli.command("clockout", help="Staff clocks out")
@click.argument("shift_id", type=int)
def clockout_command(shift_id):
    staff = require_staff_login()
    shift = clock_out(staff.id, shift_id)
    print(f"🕕 {staff.username} clocked out:")
    print(shift.get_json())


@shift_cli.command("report", help="Admin views shift report")
def report_command():
    admin = require_admin_login()
    report = get_shift_report(admin.id)
    print(f"📊 Shift report for {admin.username}:")
    print(report)

app.cli.add_command(shift_cli)



# Schedule CLI commands
schedule_cli = AppGroup('schedule', help='Schedule management commands')

@schedule_cli.command("create", help="Create a schedule")
@click.argument("name")
def create_schedule_command(name):
    from App.models import Schedule
    admin = require_admin_login()
    
    schedule = Schedule(name=name, created_by=admin.id)
    db.session.add(schedule)
    db.session.commit()
    
    print(f"✅ Schedule created:")
    print(schedule.get_json())


@schedule_cli.command("list", help="List all schedules")
def list_schedules_command():
    from App.models import Schedule
    admin = require_admin_login()
    
    schedules = Schedule.query.all()
    print(f"✅ Found {len(schedules)} schedule(s):")
    for s in schedules:
        print(s.get_json())


@schedule_cli.command("view", help="View a schedule and its shifts")
@click.argument("schedule_id", type=int)
def view_schedule_command(schedule_id):
    from App.models import Schedule
    admin = require_admin_login()
    
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        print("⚠️ Schedule not found.")
    else:
        print(f"✅ Viewing schedule {schedule_id}:")
        print(schedule.get_json())



#Auto Populate Schedule Command
@schedule_cli.command("autopopulate", help="Auto-populate schedule with strategy")
@click.argument("schedule_group_id", type=int)
@click.argument("strategy", type=click.Choice(["even", "minimize_days", "day_night"]))
@click.option("--start-date", required=True)
@click.option("--end-date", required=True)
@click.option("--shift-duration", default=8)
def autopopulate_command(schedule_group_id, strategy, start_date, end_date, shift_duration):

    from App.models import Shift
    from App.controllers.admin import auto_populate_schedule

    admin = require_admin_login()

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    shifts = []
    current = start

    while current < end:
        for hour in [6, 14, 22]:  # Morning, Afternoon, Night
            shift_start = current.replace(hour=hour, minute=0, second=0)
            shift_end = shift_start + timedelta(hours=shift_duration)

            if shift_end <= end:
                shifts.append(Shift(start_time=shift_start, end_time=shift_end))

        current += timedelta(days=1)

    schedule_group = auto_populate_schedule(admin.id, schedule_group_id, shifts, strategy)

    print(f"✅ Auto-populated schedule using '{strategy}' strategy:")
    print(schedule_group.get_json())

app.cli.add_command(schedule_cli)



#Notification CLI commands
notification_cli = AppGroup('notification', help='Notification commands')

@notification_cli.command("list", help="View your notifications")
def list_notifications_command():
    # View all notifications for the logged-in user.
    from App.controllers.notification import get_user_notifications

    if not os.path.exists("active_token.txt"):
        print("No active session. Please login first.")
        return

    with open("active_token.txt", "r") as f:
        token = f.read().strip()

    try:
        decoded = decode_token(token)
        user_id = int(decoded["sub"])

        user_notifications = get_user_notifications(user_id)

        if not user_notifications:
            print("📭 No notifications.")
            return

        print(f"📬 You have {len(user_notifications)} notification(s):")
        for n in user_notifications:
            status = "✅ Read" if getattr(n, "read", False) else "• Unread"
            timestamp = getattr(n, "timestamp", "Unknown time")
            print(f"  [{timestamp}] ({status}) {n.contents}")

    except Exception as e:
        print(f"❌ Error reading notifications: {e}")


@notification_cli.command("clear", help="Clear all notifications for your account")
def clear_notifications_command():
    # Delete all notifications for the logged-in user.
    from App.controllers.notification import clear_notifications

    if not os.path.exists("active_token.txt"):
        print("No active session. Please login first.")
        return

    with open("active_token.txt", "r") as f:
        token = f.read().strip()

    try:
        decoded = decode_token(token)
        user_id = int(decoded["sub"])

        clear_notifications(user_id)
        print("🗑️ All notifications cleared.")

    except Exception as e:
        print(f"❌ Error clearing notifications: {e}")


@notification_cli.command("mark", help="Mark a notification as read")
@click.argument("notification_id", type=int)
def mark_notification_command(notification_id):
    # Mark a specific notification as read
    from App.controllers.notification import mark_as_read

    notif = mark_as_read(notification_id)
    if notif:
        print(f"📘 Notification {notification_id} marked as read.")
    else:
        print("⚠️ Notification not found.")

app.cli.add_command(notification_cli)



#Testing Commands
test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    
app.cli.add_command(test)
