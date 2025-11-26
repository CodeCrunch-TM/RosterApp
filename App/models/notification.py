from datetime import datetime

class Notification:
    def __init__(self, notif_id: int, receiver_id: int, contents: str, timestamp: datetime = None):
        self.notif_id = notif_id
        self.receiver_id = receiver_id
        self.contents = contents
        self.timestamp = datetime.now()
        
    def send(self):
        print(f"[{self.timestamp}] Notification sent to {self.receiver_id}: {self.contents}.") #gonna need to update this later i'm sure