from abc import ABC, abstractmethod
from typing import List
from models import Shift, Staff, ScheduleGroup

class ScheduleFactory(ABC):
    @abstractmethod
    def generateSchedule(self, shifts: List[Shift], staff: List[Staff]) -> ScheduleGroup:
        pass