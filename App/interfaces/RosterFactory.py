from abc import ABC, abstractmethod

class RosterFactory(ABC):
    
    @abstractmethod
    def createRoster(self):
        pass