from typing import List, Optional, Dict, Any
from App.interfaces.RosterFactory import RosterFactory
from App.models.SingleRosterFactory import SingleRosterFactory
from App.models.ScheduleGroup import ScheduleGroup
from App.models.schedule import Schedule
from App.models.strategies.EvenDistributionStrategy import EvenDistributionStrategy


class GroupRosterFactory(RosterFactory): #class diagram might need updating

    def __init__(self) -> None:
        self._single = SingleRosterFactory()
        self._strategies = {
            "even": EvenDistributionStrategy()
        }
        
    def get_strategy(self, name: str):
        return self._strategies.get(name)

    def createRoster(
        self,
        rosters_data: Optional[List[Dict[str, Any]]] = None, #not sure how we passing data quite yet since we havent done integration
        session: Optional[object] = None,
        commit: bool = False,
        group_name: Optional[str] = None,

    ) -> ScheduleGroup:
        data_list = rosters_data or []
        schedule_group = ScheduleGroup(name=group_name)

        for item in data_list:
            schedule = self._single.createRoster(item, session=session, commit=False)
            schedule_group.add_schedule(schedule)

        if session is not None:
            session.add(schedule_group)
            if commit:
                session.commit()

        return schedule_group
