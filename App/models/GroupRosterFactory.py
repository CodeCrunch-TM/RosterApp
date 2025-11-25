from typing import List, Optional, Dict, Any
from App.interfaces.RosterFactory import RosterFactory
from App.models.SingleRosterFactory import SingleRosterFactory
from App.models.schedule import Schedule


class GroupRosterFactory(RosterFactory): #shouldnt need to change since i just made it as a subclass of singelrosterfactory

    def __init__(self) -> None:
        self._single = SingleRosterFactory()
        self.rosters: List[Schedule] = []

    def createRoster(self, rosters_data: Optional[List[Dict[str, Any]]] = None) -> List[Schedule]:
        data_list = rosters_data or []
        self.rosters = []

        for item in data_list:
            schedule = self._single.createRoster(item)
            self.rosters.append(schedule)

        return self.rosters
