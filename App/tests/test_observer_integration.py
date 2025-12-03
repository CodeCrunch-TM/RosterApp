import unittest
from datetime import datetime, timedelta
from App.main import create_app
from App.database import db
from App.models import User, Staff, Shift, ScheduleGroup, Schedule, Notification
from App.controllers.user import create_user
from App.controllers.admin import auto_populate_schedule

class ObserverIntegrationTests(unittest.TestCase):
    """End-to-end tests for Observer pattern with DB"""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
        })
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        with self.app.app_context():
            db.session.rollback()
            Notification.query.delete()
            Schedule.query.delete()
            ScheduleGroup.query.delete()
            Staff.query.delete()
            db.session.commit()

            create_user("admin", "adminpass", "admin")
            create_user("staff1", "pass1", "staff")
            create_user("staff2", "pass2", "staff")
            create_user("staff3", "pass3", "staff")

            self.admin = User.query.filter_by(username="admin").first()
            self.staff1 = Staff.query.filter_by(username="staff1").first()
            self.staff2 = Staff.query.filter_by(username="staff2").first()
            self.staff3 = Staff.query.filter_by(username="staff3").first()

    def test_observer_attach_and_notify(self):
        with self.app.app_context():
            schedule_group = ScheduleGroup(name="Test Observer Group")
            db.session.add(schedule_group)
            db.session.commit()

            staff1 = Staff.query.filter_by(username="staff1").first()
            staff2 = Staff.query.filter_by(username="staff2").first()
            schedule_group.attach(staff1)
            schedule_group.attach(staff2)

            schedule_group.notifyObservers()

            notif1 = Notification.query.filter_by(receiver_id=staff1.id).first()
            notif2 = Notification.query.filter_by(receiver_id=staff2.id).first()

            self.assertIsNotNone(notif1, "Staff1 should receive notification")
            self.assertIsNotNone(notif2, "Staff2 should receive notification")
            self.assertIn("updated", notif1.message.lower())

    def test_autopopulate_triggers_notifications(self):
        with self.app.app_context():
            schedule_group = ScheduleGroup(name="Auto-Populate Test")
            db.session.add(schedule_group)
            db.session.commit()

            base_time = datetime.now()
            shifts = [
                Shift(
                    start_time=base_time + timedelta(days=i, hours=9),
                    end_time=base_time + timedelta(days=i, hours=17)
                )
                for i in range(6)
            ]

            notif_count_before = Notification.query.count()
            auto_populate_schedule(
                admin_id=self.admin.id,
                schedule_group_id=schedule_group.id,
                shifts=shifts,
                strategy_name="even"
            )
            notif_count_after = Notification.query.count()

            self.assertGreater(notif_count_after, notif_count_before,
                               "Auto-populate should create notifications")

            staff_members = Staff.query.all()
            for staff in staff_members:
                notifications = Notification.query.filter_by(receiver_id=staff.id).all()
                self.assertGreater(len(notifications), 0,
                                   f"Staff {staff.username} should have received notification")

    def test_detach_no_notifications(self):
        with self.app.app_context():
            schedule_group = ScheduleGroup(name="Detach Test")
            db.session.add(schedule_group)
            db.session.commit()

            staff1 = Staff.query.filter_by(username="staff1").first()
            staff2 = Staff.query.filter_by(username="staff2").first()
            schedule_group.attach(staff1)
            schedule_group.attach(staff2)
            schedule_group.detach(staff1)

            Notification.query.delete()
            db.session.commit()

            schedule_group.notifyObservers()

            notif1 = Notification.query.filter_by(receiver_id=staff1.id).first()
            self.assertIsNone(notif1, "Detached staff should not receive notifications")

            notif2 = Notification.query.filter_by(receiver_id=staff2.id).first()
            self.assertIsNotNone(notif2, "Attached staff should receive notifications")

    def test_multiple_updates_accumulate_notifications(self):
        with self.app.app_context():
            schedule_group = ScheduleGroup(name="Multiple Updates")
            db.session.add(schedule_group)
            db.session.commit()

            staff = Staff.query.filter_by(username="staff1").first()
            schedule_group.attach(staff)

            Notification.query.filter_by(receiver_id=staff.id).delete()
            db.session.commit()

            for i in range(3):
                schedule = Schedule(name=f"Update {i}", created_by=self.admin.id)
                schedule_group.add_schedule(schedule)
                db.session.commit()

            notifications = Notification.query.filter_by(receiver_id=staff.id).all()
            self.assertEqual(len(notifications), 3,
                             "Should have 3 notifications from 3 updates")

    def test_observer_with_schedule_removal(self):
        with self.app.app_context():
            schedule_group = ScheduleGroup(name="Removal Test")
            db.session.add(schedule_group)
            db.session.commit()

            schedule = Schedule(name="Test Schedule", created_by=self.admin.id)
            schedule_group.add_schedule(schedule)
            db.session.commit()

            staff = Staff.query.filter_by(username="staff1").first()
            schedule_group.attach(staff)

            Notification.query.filter_by(receiver_id=staff.id).delete()
            db.session.commit()

            schedule_group.remove_schedule(schedule.id)

            notifications = Notification.query.filter_by(receiver_id=staff.id).all()
            self.assertGreater(len(notifications), 0,
                               "Removing schedule should trigger notification")


if __name__ == '__main__':
    unittest.main()