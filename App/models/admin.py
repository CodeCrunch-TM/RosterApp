from App.database import db
from .user import User
from .shift import Shift
from .schedule import Schedule
from datetime import datetime

class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    def __init__(self, username, password):
        super().__init__(username, password, "admin")

    def scheduleShift(self, staff, schedule, start_time, end_time):
        if staff.role != "staff":
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

    def viewShift(self):
        shifts = Shift.query.order_by(Shift.start_time).all()
        return [s.get_json() for s in shifts]

    def createSchedule(self, name):
        new_schedule = Schedule(
            name=name,
            created_by=self.id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule
