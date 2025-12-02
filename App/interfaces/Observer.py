from abc import abstractmethod

class Observer:
    
    @abstractmethod
    def update(self, observable):
        raise NotImplementedError("Subclasses must implement update()")