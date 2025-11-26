from typing import List, Optional

from App.database import db
from App.models.schedule import Schedule


class ScheduleGroup(db.Model):

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
        self.updateRoster()

    def remove_schedule(self, schedule_id: int) -> bool:
        for s in list(self.schedules):
            if getattr(s, "id", None) == schedule_id:
                self.schedules.remove(s)
                self.updateRoster()
                return True
        return False

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "schedule_count": len(self.schedules),
            "schedules": [s.get_json() for s in self.schedules],
        }
