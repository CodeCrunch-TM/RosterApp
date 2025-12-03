import unittest, pytest
from datetime import datetime, timedelta
from App.controllers.admin import auto_populate_schedule
from App.controllers.user import get_user
from App.database import db
from App.models import User, Schedule
from App.controllers import create_user, schedule_shift, get_shift_report, get_combined_roster
from App.models.ScheduleGroup import ScheduleGroup
from App.models.shift import Shift

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
        
    @pytest.mark.unit
    def test_schedule_shift_invalid(self):
        admin = User("admin2", "adminpass", "admin")
        staff = User("staff2", "staffpass", "staff")
        invalid_schedule = Schedule(id=999, name="Invalid Schedule", created_by=admin.id)

        start = datetime(2025, 10, 22, 8, 0, 0)
        end = datetime(2025, 10, 22, 16, 0, 0)
        with self.assertRaises(Exception):
            schedule_shift(admin.id, staff, invalid_schedule, start, end)
            
    @pytest.mark.unit
    def test_get_shift_report(self):
        admin = create_user("superadmin", "superpass", "admin")
        staff = create_user("worker1", "workerpass", "staff")
        db.session.add_all([admin, staff])
        db.session.commit()

        schedule = Schedule(name="Weekend Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        schedule_shift(admin.id, staff, schedule,
                       datetime(2025, 10, 26, 8, 0, 0),
                       datetime(2025, 10, 26, 16, 0, 0))
        schedule_shift(admin.id, staff, schedule,
                       datetime(2025, 10, 27, 8, 0, 0),
                       datetime(2025, 10, 27, 16, 0, 0))
        
        report = get_shift_report(admin.id)
        self.assertGreaterEqual(len(report), 2)
        # Robust check: ensure at least one entry matches staff and schedule
        self.assertTrue(any(r["staff_id"] == staff.id and r["schedule_id"] == schedule.id for r in report))

    @pytest.mark.unit
    def test_get_shift_report_invalid(self):
        non_admin = User("randomstaff", "randompass", "staff")
        with self.assertRaises(PermissionError):
            get_shift_report(non_admin.id)
            
    @pytest.mark.unit
    def test_auto_populate_invalid_strategy(self):
        admin = create_user("auto_admin2", "adminpass", "admin")
        schedule_group = ScheduleGroup(name="Bad Strategy Group")
        db.session.add(schedule_group)
        db.session.commit()

        shifts = [Shift(start_time=datetime(2025, 10, 24, 8, 0, 0),
                        end_time=datetime(2025, 10, 24, 16, 0, 0))]

        with self.assertRaises(ValueError):
            auto_populate_schedule(admin.id, schedule_group.id, shifts, "nonexistent_strategy")

    @pytest.mark.unit
    def test_auto_populate_invalid_admin(self):
        staff = create_user("not_admin", "pass", "staff")
        schedule_group = ScheduleGroup(name="Invalid Admin Group")
        db.session.add(schedule_group)
        db.session.commit()

        shifts = [Shift(start_time=datetime(2025, 10, 24, 8, 0, 0),
                        end_time=datetime(2025, 10, 24, 16, 0, 0))]

        with self.assertRaises(PermissionError):
            auto_populate_schedule(staff.id, schedule_group.id, shifts, "even_distribution")

    @pytest.mark.unit
    def test_auto_populate_empty_shifts(self):
        admin = create_user("auto_admin3", "adminpass", "admin")
        schedule_group = ScheduleGroup(name="Empty Shifts Group")
        db.session.add(schedule_group)
        db.session.commit()

        with self.assertRaises(ValueError):
            auto_populate_schedule(admin.id, schedule_group.id, [], "even_distribution")

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
        self.assertTrue(any("sam" in r.get("staff_name", "") for r in report))
        self.assertTrue(all("start_time" in r and "end_time" in r for r in report))
       
    @pytest.mark.integration 
    def test_admin_schedule_shift_for_staff(self):
        admin = create_user("admin1", "adminpass", "admin")
        staff = create_user("staff1", "staffpass", "staff")

        schedule = Schedule(name="Week 1 Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        shift = schedule_shift(admin.id, staff, schedule, start, end)
        retrieved = get_user(staff.id)

        self.assertIn(shift.id, [s.id for s in retrieved.shifts])
        self.assertEqual(shift.staff_id, staff.id)
        self.assertEqual(shift.schedule_id, schedule.id)
     
    @pytest.mark.integration   
    def test_permission_restrictions(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("worker", "workpass", "staff")

        schedule = Schedule(name="Restricted Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        with self.assertRaises(PermissionError):
            schedule_shift(staff.id, staff, schedule, start, end)

        with self.assertRaises(PermissionError):
            get_combined_roster(admin.id)

        with self.assertRaises(PermissionError):
            get_shift_report(staff.id)

    @pytest.mark.integration
    def test_auto_populate_valid(self):
        admin = create_user("auto_admin", "adminpass", "admin")
        staff1 = create_user("staffA", "passA", "staff")
        staff2 = create_user("staffB", "passB", "staff")

        schedule_group = ScheduleGroup(name="Auto Group")
        db.session.add(schedule_group)
        db.session.commit()

        shifts = [
            Shift(start_time=datetime(2025, 10, 24, 8, 0, 0),
                  end_time=datetime(2025, 10, 24, 16, 0, 0)),
            Shift(start_time=datetime(2025, 10, 25, 8, 0, 0),
                  end_time=datetime(2025, 10, 25, 16, 0, 0))
        ]

        populated_group = auto_populate_schedule(admin.id, schedule_group.id, shifts, "even_distribution")

        # Ensure observers exist
        self.assertTrue(any(s.id == staff1.id for s in populated_group.observers))
        self.assertTrue(any(s.id == staff2.id for s in populated_group.observers))

        generated_shifts = Shift.query.filter(
            Shift.schedule_id.in_([s.id for s in populated_group.schedules])
        ).all()

        staff_ids = {s.staff_id for s in generated_shifts}
        self.assertTrue(any(sid in (staff1.id, staff2.id) for sid in staff_ids))
        self.assertGreaterEqual(len(generated_shifts), 2)