from typing import List, Optional, Dict, Any
from App.interfaces.RosterFactory import RosterFactory
from App.models.SingleRosterFactory import SingleRosterFactory
from App.models.ScheduleGroup import ScheduleGroup
from App.models.schedule import Schedule
from App.models.Strategies.EvenDistributionStrategy import EvenDistributionStrategy
from App.models.Strategies.DayNightBalancedScheduling import DayNightBalancedScheduling
from App.models.Strategies.MinimizeDaySchedulingStrategy import MinimizeDaySchedulingStrategy


class GroupRosterFactory(RosterFactory): #class diagram might need updating

    def __init__(self) -> None:
        self._single = SingleRosterFactory()
        self._strategies = {
            "even_distribution": EvenDistributionStrategy(),
            "day_night_balanced": DayNightBalancedScheduling(),
            "minimize_day": MinimizeDaySchedulingStrategy(),
        }
        
    def get_strategy(self, name: str):
        return self._strategies.get(name)

    def createRoster(
        self,
        rosters_data: Optional[List[Dict[str, Any]]] = None,
        session: Optional[object] = None,
        commit: bool = False,
        group_name: Optional[str] = None,
    ) -> ScheduleGroup:
        data_list = rosters_data or []
        
        if not isinstance(data_list, list):
            raise TypeError("'rosters_data' must be a list of dictionaries")
        
        schedule_group = ScheduleGroup(name=group_name)

        for idx, item in enumerate(data_list):
            if not isinstance(item, dict):
                raise TypeError(f"Roster data at index {idx} must be a dictionary")
            
            try:
                schedule = self._single.createRoster(item, session=session, commit=False)
                schedule_group.add_schedule(schedule)
            except Exception as e:
                if session is not None:
                    session.rollback()
                raise ValueError(f"Failed to create schedule at index {idx}: {str(e)}")

        if session is not None:
            session.add(schedule_group)
            if commit:
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise RuntimeError(f"Failed to commit schedule group to database: {str(e)}")

        return schedule_group

    def createRosterWithStrategy(
        self,
        strategy_name: str,
        shifts: List,
        staff: List,
        group_name: Optional[str] = None,
        session: Optional[object] = None,
        commit: bool = False,
    ) -> ScheduleGroup:
        # Validate strategy name
        if not strategy_name or not isinstance(strategy_name, str):
            raise ValueError("'strategy_name' must be a non-empty string")
        
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown strategy: '{strategy_name}'")
        
        # Validate shifts and staff
        if not isinstance(shifts, list):
            raise TypeError("'shifts' must be a list")
        if not isinstance(staff, list):
            raise TypeError("'staff' must be a list")
        
        if not shifts:
            raise ValueError("'shifts' list cannot be empty")
        if not staff:
            raise ValueError("'staff' list cannot be empty")
        
        schedule_group = ScheduleGroup(name=group_name)
        
        # Strategy modifies the schedule_group in place
        try:
            strategy.generateSchedule(shifts, staff, schedule_group)
        except Exception as e:
            if session is not None:
                session.rollback()
            raise RuntimeError(f"Strategy '{strategy_name}' failed to generate schedule: {str(e)}")
        
        if session is not None:
            session.add(schedule_group)
            if commit:
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise RuntimeError(f"Failed to commit schedule group to database: {str(e)}")
        
        return schedule_group
