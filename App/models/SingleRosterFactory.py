
from typing import Optional, Dict, Any
from App.interfaces.RosterFactory import RosterFactory
from App.models.schedule import Schedule
from App.models.shift import Shift
from App.models.staff import Staff
from App.database import db


class SingleRosterFactory(RosterFactory): #this mighg need to be changed based on refaactoring
    def __init__(self) -> None:           #i dont think i violated model rules but eh
        self.roster: Optional[Schedule] = None

    def createRoster(
        self,
        roster_data: Optional[Dict[str, Any]] = None,
        session: Optional[object] = None,
        commit: bool = False,
    ) -> Schedule:
        data = roster_data or {}

        schedule = Schedule(
            name=data.get("name", ""),
            created_by=data.get("created_by"), #minor addition 
        )

        for s in data.get("shifts", []):
            start_time = s.get("start_time")
            end_time = s.get("end_time")

            shift_kwargs: Dict[str, Any] = {"start_time": start_time, "end_time": end_time}

            staff_value = s.get("staff")    
            if isinstance(staff_value, Staff):
                shift_kwargs["staff"] = staff_value         
            elif isinstance(staff_value, dict):        #staff error handling stuff, we might not need it after refactoring
                try:
                    shift_kwargs["staff"] = Staff(**staff_value)
                except TypeError:
                    staff_id = staff_value.get("id")
                    if staff_id is not None:
                        shift_kwargs["staff_id"] = staff_id
            elif isinstance(staff_value, int):
                shift_kwargs["staff_id"] = staff_value

            shift = Shift(**shift_kwargs)

            schedule.shifts.append(shift)
            if session is not None:
                session.add(shift)

        if session is not None:
            session.add(schedule)
            if commit:
                session.commit()

        self.roster = schedule
        return schedule
