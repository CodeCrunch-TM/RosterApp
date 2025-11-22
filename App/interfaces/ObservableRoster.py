from abc import abstractmethod

class ObservableRoster():
    
    @abstractmethod
    def attach(self, Observer):
        pass
    
    @abstractmethod
    def detach(self, Observer):
        pass
    
    @abstractmethod
    def notifyObservers(self):
        pass
    
    @abstractmethod
    def updateRoster(self):
        pass
    