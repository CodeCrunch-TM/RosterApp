import unittest, pytest
from datetime import datetime, timedelta
from App.database import db, create_db
from App.models import Schedule, Shift
from App.controllers import create_user, schedule_shift, get_combined_roster, clock_in, clock_out, get_shift

@pytest.fixture(autouse=True)
def clean_db():
    db.drop_all()
    create_db()
    db.session.remove()
    yield

class StaffTests(unittest.TestCase):
    """Unit + Integration tests for Staff functionality"""

    @pytest.mark.unit
    def test_get_combined_roster_valid(self):
        staff = create_user("staff3", "pass123", "staff")
        admin = create_user("admin3", "adminpass", "admin")
        schedule = Schedule(name="Test Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        shift = schedule_shift(admin.id, staff, schedule,
                               datetime(2025, 10, 23, 8, 0, 0),
                               datetime(2025, 10, 23, 16, 0, 0))

        roster = get_combined_roster(staff.id)
        self.assertEqual(roster[0]["staff_id"], staff.id)
        self.assertEqual(roster[0]["schedule_id"], schedule.id)

    @pytest.mark.unit
    def test_clock_in_and_out(self):
        admin = create_user("admin_clock", "adminpass", "admin")
        staff = create_user("staff_clock", "staffpass", "staff")
        schedule = Schedule(name="Clock Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime(2025, 10, 25, 8, 0, 0)
        end = datetime(2025, 10, 25, 16, 0, 0)
        shift = schedule_shift(admin.id, staff, schedule, start, end)

        clock_in(staff.id, shift.id)
        clock_out(staff.id, shift.id)

        updated_shift = get_shift(shift.id)
        self.assertIsNotNone(updated_shift.clock_in)
        self.assertIsNotNone(updated_shift.clock_out)
        self.assertLess(updated_shift.clock_in, updated_shift.clock_out)

    @pytest.mark.integration
    def test_roster_integration(self):
        admin = create_user("admin", "adminpass", "admin")
        staff1 = create_user("jane", "janepass", "staff")
        staff2 = create_user("mark", "markpass", "staff")
        schedule = Schedule(name="Shared Roster", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        schedule_shift(admin.id, staff1, schedule, datetime.now(), datetime.now() + timedelta(hours=8))
        schedule_shift(admin.id, staff2, schedule, datetime.now(), datetime.now() + timedelta(hours=8))

        roster = get_combined_roster(staff1.id)
        self.assertTrue(any(s["staff_id"] == staff1.id for s in roster))
        self.assertTrue(any(s["staff_id"] == staff2.id for s in roster))
