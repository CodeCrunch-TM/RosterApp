from abc import ABC, abstractmethod
from typing import List
from App.models import Shift, Staff, ScheduleGroup

class ScheduleStrategy(ABC):
    @abstractmethod
    def generateSchedule(self, shifts: List[Shift], staff: List[Staff]) -> ScheduleGroup:
        pass