import pytest #this one was also AI assited, way too much stuff to test on short notice
from datetime import datetime, timedelta
from App.models.SingleRosterFactory import SingleRosterFactory
from App.models.GroupRosterFactory import GroupRosterFactory
from App.models.schedule import Schedule
from App.models.shift import Shift
from App.models.staff import Staff
from App.models.user import User
from App.models.admin import Admin
from App.models.ScheduleGroup import ScheduleGroup
from App.database import db


class TestSingleRosterFactoryIntegration:
    """Integration tests for SingleRosterFactory with database operations."""

    def test_create_and_persist_schedule_with_staff_ids(self, app):
        """Test creating a schedule with staff IDs and persisting to database."""
        with app.app_context():
            # Create test users
            admin = Admin("admin_user", "password123")
            staff1 = Staff("john_doe", "password123")
            staff2 = Staff("jane_smith", "password123")
            
            db.session.add(admin)
            db.session.add(staff1)
            db.session.add(staff2)
            db.session.commit()
            
            # Get IDs after commit
            admin_id = admin.id
            staff1_id = staff1.id
            staff2_id = staff2.id
            
            # Create schedule data
            schedule_data = {
                "name": "Week 1 Schedule",
                "created_by": admin_id,
                "shifts": [
                    {
                        "start_time": datetime(2025, 1, 6, 9, 0),
                        "end_time": datetime(2025, 1, 6, 17, 0),
                        "staff": staff1_id
                    },
                    {
                        "start_time": datetime(2025, 1, 6, 17, 0),
                        "end_time": datetime(2025, 1, 7, 1, 0),
                        "staff": staff2_id
                    }
                ]
            }
            
            # Create schedule with factory
            factory = SingleRosterFactory()
            schedule = factory.createRoster(
                schedule_data, 
                session=db.session, 
                commit=True
            )
            
            # Verify schedule was created
            assert schedule.id is not None
            assert schedule.name == "Week 1 Schedule"
            assert schedule.created_by == admin_id
            assert len(schedule.shifts) == 2
            
            # Verify shifts were persisted
            persisted_schedule = Schedule.query.get(schedule.id)
            assert persisted_schedule is not None
            assert len(persisted_schedule.shifts) == 2
            
            # Verify shift details
            shift1 = persisted_schedule.shifts[0]
            assert shift1.staff_id == staff1_id
            assert shift1.start_time == datetime(2025, 1, 6, 9, 0)
            assert shift1.end_time == datetime(2025, 1, 6, 17, 0)

    def test_create_schedule_with_staff_objects(self, app):
        """Test creating a schedule with Staff object instances."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            staff1 = Staff("alice_worker", "password123")
            
            db.session.add(admin)
            db.session.add(staff1)
            db.session.commit()
            
            admin_id = admin.id
            
            # Create new staff object (not yet in DB)
            new_staff = Staff("bob_worker", "password123")
            
            schedule_data = {
                "name": "Test Schedule",
                "created_by": admin_id,
                "shifts": [
                    {
                        "start_time": datetime(2025, 1, 7, 9, 0),
                        "end_time": datetime(2025, 1, 7, 17, 0),
                        "staff": new_staff
                    }
                ]
            }
            
            factory = SingleRosterFactory()
            schedule = factory.createRoster(
                schedule_data,
                session=db.session,
                commit=True
            )
            
            # Verify staff object was persisted
            assert new_staff.id is not None
            assert schedule.shifts[0].staff_id == new_staff.id
            
            # Verify we can query the staff
            persisted_staff = Staff.query.filter_by(username="bob_worker").first()
            assert persisted_staff is not None
            assert persisted_staff.id == new_staff.id

    def test_create_schedule_with_staff_dict(self, app):
        """Test creating a schedule with staff provided as dictionaries."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            db.session.add(admin)
            db.session.commit()
            
            schedule_data = {
                "name": "Dict Staff Schedule",
                "created_by": admin.id,
                "shifts": [
                    {
                        "start_time": datetime(2025, 1, 8, 9, 0),
                        "end_time": datetime(2025, 1, 8, 17, 0),
                        "staff": {"username": "charlie", "password": "pass123"}
                    }
                ]
            }
            
            factory = SingleRosterFactory()
            schedule = factory.createRoster(
                schedule_data,
                session=db.session,
                commit=True
            )
            
            # Verify staff was created from dict
            assert schedule.shifts[0].staff is not None
            assert schedule.shifts[0].staff.username == "charlie"
            
            # Verify persistence
            charlie = Staff.query.filter_by(username="charlie").first()
            assert charlie is not None

    def test_validation_errors_rollback(self, app):
        """Test that validation errors trigger proper rollback."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            db.session.add(admin)
            db.session.commit()
            
            # Missing required 'staff' field
            invalid_data = {
                "name": "Invalid Schedule",
                "created_by": admin.id,
                "shifts": [
                    {
                        "start_time": datetime(2025, 1, 9, 9, 0),
                        "end_time": datetime(2025, 1, 9, 17, 0)
                        # Missing 'staff' field
                    }
                ]
            }
            
            factory = SingleRosterFactory()
            
            with pytest.raises(ValueError, match="missing required 'staff' assignment"):
                factory.createRoster(
                    invalid_data,
                    session=db.session,
                    commit=True
                )
            
            # Verify no schedule was created
            schedules = Schedule.query.filter_by(name="Invalid Schedule").all()
            assert len(schedules) == 0

    def test_missing_created_by_validation(self, app):
        """Test that missing 'created_by' field raises validation error."""
        with app.app_context():
            factory = SingleRosterFactory()
            
            invalid_data = {
                "name": "No Creator Schedule",
                "shifts": []
            }
            
            with pytest.raises(ValueError, match="must have 'created_by' field"):
                factory.createRoster(invalid_data)

    def test_invalid_created_by_type(self, app):
        """Test that invalid 'created_by' type raises validation error."""
        with app.app_context():
            factory = SingleRosterFactory()
            
            invalid_data = {
                "name": "Bad Creator",
                "created_by": "not_an_integer",
                "shifts": []
            }
            
            with pytest.raises(ValueError, match="must be a valid integer user ID"):
                factory.createRoster(invalid_data)


class TestGroupRosterFactoryIntegration:
    """Integration tests for GroupRosterFactory with database operations."""

    def test_create_multiple_schedules_in_group(self, app):
        """Test creating multiple schedules grouped together."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            staff1 = Staff("worker1", "password123")
            staff2 = Staff("worker2", "password123")
            
            db.session.add_all([admin, staff1, staff2])
            db.session.commit()
            
            group_data = [
                {
                    "name": "Morning Schedule",
                    "created_by": admin.id,
                    "shifts": [
                        {
                            "start_time": datetime(2025, 1, 10, 6, 0),
                            "end_time": datetime(2025, 1, 10, 14, 0),
                            "staff": staff1.id
                        }
                    ]
                },
                {
                    "name": "Evening Schedule",
                    "created_by": admin.id,
                    "shifts": [
                        {
                            "start_time": datetime(2025, 1, 10, 14, 0),
                            "end_time": datetime(2025, 1, 10, 22, 0),
                            "staff": staff2.id
                        }
                    ]
                }
            ]
            
            factory = GroupRosterFactory()
            schedule_group = factory.createRoster(
                group_data,
                session=db.session,
                commit=True,
                group_name="Daily Rotation"
            )
            
            # Verify schedule group
            assert schedule_group.id is not None
            assert schedule_group.name == "Daily Rotation"
            assert len(schedule_group.schedules) == 2
            
            # Verify individual schedules
            assert schedule_group.schedules[0].name == "Morning Schedule"
            assert schedule_group.schedules[1].name == "Evening Schedule"
            
            # Verify persistence
            persisted_group = ScheduleGroup.query.get(schedule_group.id)
            assert persisted_group is not None
            assert len(persisted_group.schedules) == 2

    def test_create_roster_with_strategy(self, app):
        """Test creating schedules using a scheduling strategy."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            staff1 = Staff("worker1", "password123")
            staff2 = Staff("worker2", "password123")
            staff3 = Staff("worker3", "password123")
            
            db.session.add_all([admin, staff1, staff2, staff3])
            db.session.commit()
            
            # Create shifts that need to be distributed
            shifts = [
                Shift(
                    staff_id=staff1.id,
                    start_time=datetime(2025, 1, 11, 9, 0),
                    end_time=datetime(2025, 1, 11, 17, 0)
                ),
                Shift(
                    staff_id=staff2.id,
                    start_time=datetime(2025, 1, 12, 9, 0),
                    end_time=datetime(2025, 1, 12, 17, 0)
                ),
                Shift(
                    staff_id=staff3.id,
                    start_time=datetime(2025, 1, 13, 9, 0),
                    end_time=datetime(2025, 1, 13, 17, 0)
                )
            ]
            
            staff_list = [staff1, staff2, staff3]
            
            factory = GroupRosterFactory()
            schedule_group = factory.createRosterWithStrategy(
                strategy_name="even_distribution",
                shifts=shifts,
                staff=staff_list,
                group_name="Strategy-Based Schedule",
                session=db.session,
                commit=True
            )
            
            # Verify schedule group was created
            assert schedule_group.id is not None
            assert schedule_group.name == "Strategy-Based Schedule"
            assert len(schedule_group.schedules) > 0
            
            # Verify persistence
            persisted_group = ScheduleGroup.query.get(schedule_group.id)
            assert persisted_group is not None

    def test_strategy_validation_errors(self, app):
        """Test that invalid strategy parameters raise appropriate errors."""
        with app.app_context():
            factory = GroupRosterFactory()
            
            # Test invalid strategy name
            with pytest.raises(ValueError, match="Unknown strategy"):
                factory.createRosterWithStrategy(
                    strategy_name="nonexistent_strategy",
                    shifts=[],
                    staff=[]
                )
            
            # Test empty strategy name
            with pytest.raises(ValueError, match="must be a non-empty string"):
                factory.createRosterWithStrategy(
                    strategy_name="",
                    shifts=[],
                    staff=[]
                )
            
            # Test invalid shifts type
            with pytest.raises(TypeError, match="'shifts' must be a list"):
                factory.createRosterWithStrategy(
                    strategy_name="even_distribution",
                    shifts="not_a_list",
                    staff=[]
                )
            
            # Test invalid staff type
            with pytest.raises(TypeError, match="'staff' must be a list"):
                factory.createRosterWithStrategy(
                    strategy_name="even_distribution",
                    shifts=[],
                    staff="not_a_list"
                )

    def test_empty_shifts_or_staff_validation(self, app):
        """Test that empty shifts or staff lists raise errors."""
        with app.app_context():
            factory = GroupRosterFactory()
            
            # Test empty shifts
            with pytest.raises(ValueError, match="'shifts' list cannot be empty"):
                factory.createRosterWithStrategy(
                    strategy_name="even_distribution",
                    shifts=[],
                    staff=[Staff("test", "pass")]
                )
            
            # Test empty staff
            with pytest.raises(ValueError, match="'staff' list cannot be empty"):
                factory.createRosterWithStrategy(
                    strategy_name="even_distribution",
                    shifts=[Shift(
                        staff_id=1,
                        start_time=datetime.now(),
                        end_time=datetime.now()
                    )],
                    staff=[]
                )

    def test_invalid_roster_data_in_group(self, app):
        """Test error handling when one schedule in a group has invalid data."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            db.session.add(admin)
            db.session.commit()
            
            group_data = [
                {
                    "name": "Valid Schedule",
                    "created_by": admin.id,
                    "shifts": []
                },
                {
                    "name": "Invalid Schedule",
                    "created_by": "not_an_integer",  # Invalid type
                    "shifts": []
                }
            ]
            
            factory = GroupRosterFactory()
            
            with pytest.raises(ValueError, match="Failed to create schedule at index 1"):
                factory.createRoster(
                    group_data,
                    session=db.session,
                    commit=True
                )
            
            # Verify rollback - no schedules should be created
            valid_schedule = Schedule.query.filter_by(name="Valid Schedule").first()
            assert valid_schedule is None

    def test_get_strategy_method(self, app):
        """Test that all expected strategies are available."""
        with app.app_context():
            factory = GroupRosterFactory()
            
            # Test known strategies
            assert factory.get_strategy("even_distribution") is not None
            assert factory.get_strategy("day_night_balanced") is not None
            assert factory.get_strategy("minimize_day") is not None
            
            # Test unknown strategy
            assert factory.get_strategy("unknown_strategy") is None


class TestFactoryInteroperability:
    """Test interaction between SingleRosterFactory and GroupRosterFactory."""

    def test_group_factory_uses_single_factory_internally(self, app):
        """Test that GroupRosterFactory correctly delegates to SingleRosterFactory."""
        with app.app_context():
            admin = Admin("admin_user", "password123")
            staff = Staff("worker", "password123")
            
            db.session.add_all([admin, staff])
            db.session.commit()
            
            # Create schedule using group factory with single item
            group_data = [
                {
                    "name": "Single in Group",
                    "created_by": admin.id,
                    "shifts": [
                        {
                            "start_time": datetime(2025, 1, 14, 9, 0),
                            "end_time": datetime(2025, 1, 14, 17, 0),
                            "staff": staff.id
                        }
                    ]
                }
            ]
            
            group_factory = GroupRosterFactory()
            schedule_group = group_factory.createRoster(
                group_data,
                session=db.session,
                commit=True
            )
            
            # Create same schedule using single factory
            single_data = {
                "name": "Direct Single",
                "created_by": admin.id,
                "shifts": [
                    {
                        "start_time": datetime(2025, 1, 14, 9, 0),
                        "end_time": datetime(2025, 1, 14, 17, 0),
                        "staff": staff.id
                    }
                ]
            }
            
            single_factory = SingleRosterFactory()
            single_schedule = single_factory.createRoster(
                single_data,
                session=db.session,
                commit=True
            )
            
            # Verify both approaches create valid schedules
            group_schedule = schedule_group.schedules[0]
            assert group_schedule.name == "Single in Group"
            assert single_schedule.name == "Direct Single"
            
            # Verify both have same structure
            assert len(group_schedule.shifts) == len(single_schedule.shifts)
            assert group_schedule.created_by == single_schedule.created_by

    def test_complex_multi_day_schedule(self, app):
        """Test creating a complex multi-day schedule with multiple staff."""
        with app.app_context():
            admin = Admin("manager", "password123")
            staff_members = [
                Staff(f"staff_{i}", "password123") for i in range(5)
            ]
            
            db.session.add(admin)
            db.session.add_all(staff_members)
            db.session.commit()
            
            # Create a week-long schedule with morning and evening shifts
            week_data = []
            base_date = datetime(2025, 1, 15)
            
            for day in range(7):
                current_date = base_date + timedelta(days=day)
                
                day_schedule = {
                    "name": f"Day {day + 1} Schedule",
                    "created_by": admin.id,
                    "shifts": [
                        {
                            "start_time": current_date.replace(hour=8, minute=0),
                            "end_time": current_date.replace(hour=16, minute=0),
                            "staff": staff_members[day % len(staff_members)].id
                        },
                        {
                            "start_time": current_date.replace(hour=16, minute=0),
                            "end_time": current_date.replace(hour=23, minute=59),
                            "staff": staff_members[(day + 1) % len(staff_members)].id
                        }
                    ]
                }
                week_data.append(day_schedule)
            
            factory = GroupRosterFactory()
            schedule_group = factory.createRoster(
                week_data,
                session=db.session,
                commit=True,
                group_name="Weekly Rotation"
            )
            
            # Verify complete week schedule
            assert len(schedule_group.schedules) == 7
            
            # Verify each day has 2 shifts
            for schedule in schedule_group.schedules:
                assert len(schedule.shifts) == 2
            
            # Verify total shifts
            total_shifts = sum(len(s.shifts) for s in schedule_group.schedules)
            assert total_shifts == 14
            
            # Verify all staff were assigned
            assigned_staff_ids = set()
            for schedule in schedule_group.schedules:
                for shift in schedule.shifts:
                    assigned_staff_ids.add(shift.staff_id)
            
            assert len(assigned_staff_ids) == len(staff_members)
