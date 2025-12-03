from typing import List, Optional

from App.database import db
from App.models.schedule import Schedule
from App.models.notification import Notification


class ScheduleGroup(db.Model): #had some tweaks since we decided on the notification design after this was writted

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    schedules = db.relationship("Schedule", backref="schedule_group", lazy=True)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self._observers: List = []

    def attach(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notifyObservers(self) -> None:
        for o in list(self._observers):
            try:
                o.update(self)
            except Exception:
                pass

    def updateRoster(self) -> None:
        self.notifyObservers()

    def add_schedule(self, schedule: Schedule) -> None:
        self.schedules.append(schedule)

    def remove_schedule(self, schedule_id: int) -> bool:
        for s in list(self.schedules):
            if getattr(s, "id", None) == schedule_id:
                self.schedules.remove(s)
                return True
        return False

    def _send_notifications(self) -> None:
        if not self.id:  # skip if not persisted yet
            return
        
        staff_ids = set()
        for schedule in self.schedules:
            for shift in schedule.shifts:
                if shift.staff_id:
                    staff_ids.add(shift.staff_id)
        
        group_name = self.name or f"Schedule Group #{self.id}"
        message = f"Schedule update: {group_name} has been modified"
        
        for staff_id in staff_ids:
            notification = Notification(
                receiver_id=staff_id,
                message=message,
                read=False
            )
            db.session.add(notification) #should be working correctly now

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "schedule_count": len(self.schedules),
            "schedules": [s.get_json() for s in self.schedules],
        }
