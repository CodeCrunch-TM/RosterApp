import unittest, pytest
from datetime import datetime, timedelta
from App.database import db, create_db
from App.models import User, Schedule
from App.controllers import create_user, schedule_shift, get_shift_report

class AdminTests(unittest.TestCase):
    """Unit + Integration tests for Admin functionality"""

    # ---- Unit Tests ----
    @pytest.mark.unit
    def test_schedule_shift_valid(self):
        admin = create_user("admin1", "adminpass", "admin")
        staff = create_user("staff1", "staffpass", "staff")
        schedule = Schedule(name="Morning Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime(2025, 10, 22, 8, 0, 0)
        end = datetime(2025, 10, 22, 16, 0, 0)
        shift = schedule_shift(admin.id, staff, schedule, start, end)

        self.assertEqual(shift.staff_id, staff.id)
        self.assertEqual(shift.schedule_id, schedule.id)
        self.assertEqual(shift.start_time, start)
        self.assertEqual(shift.end_time, end)

    # ---- Integration Tests ----
    @pytest.mark.integration
    def test_admin_generate_shift_report(self):
        admin = create_user("boss", "boss123", "admin")
        staff = create_user("sam", "sampass", "staff")

        schedule = Schedule(name="Weekly Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)
        schedule_shift(admin.id, staff, schedule, start, end)

        report = get_shift_report(admin.id)
        self.assertTrue(any("sam" in r["staff_name"] for r in report))
        self.assertTrue(all("start_time" in r and "end_time" in r for r in report))
