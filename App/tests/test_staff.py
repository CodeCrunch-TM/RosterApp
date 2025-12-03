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
    def test_get_combined_roster_invalid(self):
        non_staff = create_user("admin4", "adminpass", "admin")
        try:
            get_combined_roster(non_staff.id)
            assert False, "Expected PermissionError for non-staff"
        except PermissionError as e:
            assert str(e) == "Only staff can view roster"


    @pytest.mark.unit
    def test_clock_in_valid(self):
        admin = create_user("admin_clock", "adminpass", "admin")
        staff = create_user("staff_clock", "staffpass", "staff")

        schedule = Schedule(name="Clock Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime(2025, 10, 25, 8, 0, 0)
        end = datetime(2025, 10, 25, 16, 0, 0)
        shift = schedule_shift(admin.id, staff, schedule, start, end)

        clocked_in_shift = clock_in(staff.id, shift.id)
        assert clocked_in_shift.clock_in is not None
        assert isinstance(clocked_in_shift.clock_in, datetime)

    @pytest.mark.unit
    def test_clock_in_invalid_user(self):
        admin = create_user("admin_clockin", "adminpass", "admin")
        schedule = Schedule(name="Invalid Clock In", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        staff = create_user("staff_invalid", "staffpass", "staff")
        start = datetime(2025, 10, 26, 8, 0, 0)
        end = datetime(2025, 10, 26, 16, 0, 0)
        shift = schedule_shift(admin.id, staff, schedule, start, end)

        with pytest.raises(PermissionError) as e:
            clock_in(admin.id, shift.id)
        assert str(e.value) == "Only staff can clock in"

    @pytest.mark.unit
    def test_clock_in_invalid_shift(self):
        staff = create_user("clockstaff_invalid", "clockpass", "staff")
        with pytest.raises(ValueError) as e:
            clock_in(staff.id, 999)
        assert str(e.value) == "Invalid shift for staff"

    @pytest.mark.unit
    def test_clock_out_valid(self):
        admin = create_user("admin_clockout", "adminpass", "admin")
        staff = create_user("staff_clockout", "staffpass", "staff")

        schedule = Schedule(name="ClockOut Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime(2025, 10, 27, 8, 0, 0)
        end = datetime(2025, 10, 27, 16, 0, 0)
        shift = schedule_shift(admin.id, staff, schedule, start, end)

        clocked_out_shift = clock_out(staff.id, shift.id)
        assert clocked_out_shift.clock_out is not None
        assert isinstance(clocked_out_shift.clock_out, datetime)

    @pytest.mark.unit
    def test_clock_out_invalid_user(self):
        admin = create_user("admin_invalid_out", "adminpass", "admin")
        schedule = Schedule(name="Invalid ClockOut Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        staff = create_user("staff_invalid_out", "staffpass", "staff")
        start = datetime(2025, 10, 28, 8, 0, 0)
        end = datetime(2025, 10, 28, 16, 0, 0)
        shift = schedule_shift(admin.id, staff, schedule, start, end)

        with pytest.raises(PermissionError) as e:
            clock_out(admin.id, shift.id)
        assert str(e.value) == "Only staff can clock out"

    @pytest.mark.unit
    def test_clock_out_invalid_shift(self):
        staff = create_user("staff_invalid_shift_out", "staffpass", "staff")
        with pytest.raises(ValueError) as e:
            clock_out(staff.id, 999)  
        assert str(e.value) == "Invalid shift for staff"
    
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
        
    @pytest.mark.integration
    def test_staff_clock_in_and_out(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("lee", "leepass", "staff")

        schedule = Schedule(name="Daily Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        shift = schedule_shift(admin.id, staff, schedule, start, end)

        clock_in(staff.id, shift.id)
        clock_out(staff.id, shift.id)


        updated_shift = get_shift(shift.id)
        self.assertIsNotNone(updated_shift.clock_in)
        self.assertIsNotNone(updated_shift.clock_out)
        self.assertLess(updated_shift.clock_in, updated_shift.clock_out)
