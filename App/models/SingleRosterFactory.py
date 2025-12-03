
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

        created_by = data.get("created_by") #validation
        if created_by is None:
            raise ValueError("Schedule must have 'created_by' field")
        
        try:
            created_by = int(created_by)
        except (ValueError, TypeError):
            raise ValueError("'created_by' must be a valid integer user ID")

        schedule = Schedule(
            name=data.get("name", ""),
            created_by=created_by,
        )

        shifts_data = data.get("shifts", [])
        if not isinstance(shifts_data, list):
            raise TypeError("'shifts' must be a list")

        for idx, s in enumerate(shifts_data):
            if not isinstance(s, dict):
                raise TypeError(f"Shift at index {idx} must be a dictionary")
            
            start_time = s.get("start_time")
            end_time = s.get("end_time")
            
            if start_time is None: #more validation and error handling
                raise ValueError(f"Shift at index {idx} missing required 'start_time'")
            if end_time is None:
                raise ValueError(f"Shift at index {idx} missing required 'end_time'")

            shift_kwargs: Dict[str, Any] = {"start_time": start_time, "end_time": end_time}

            staff_value = s.get("staff")
            if staff_value is None:
                raise ValueError(f"Shift at index {idx} missing required 'staff' assignment") #error handling
            
            if isinstance(staff_value, Staff):
                shift_kwargs["staff"] = staff_value         
            elif isinstance(staff_value, dict):
                try:
                    shift_kwargs["staff"] = Staff(**staff_value)
                except TypeError:
                    staff_id = staff_value.get("id")
                    if staff_id is not None:
                        shift_kwargs["staff_id"] = staff_id
                    else:
                        raise ValueError(f"Shift at index {idx}: staff dict must have 'id' field")
            elif isinstance(staff_value, int):
                shift_kwargs["staff_id"] = staff_value
            else:
                raise TypeError(f"Shift at index {idx}: 'staff' must be Staff object, dict, or int") #error handling

            try:
                shift = Shift(**shift_kwargs)
            except Exception as e:
                raise ValueError(f"Failed to create shift at index {idx}: {str(e)}")

            schedule.shifts.append(shift)
            if session is not None:
                session.add(shift)

        if session is not None:
            session.add(schedule)
            if commit:
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise RuntimeError(f"Failed to commit schedule to database: {str(e)}")

        self.roster = schedule
        return schedule
