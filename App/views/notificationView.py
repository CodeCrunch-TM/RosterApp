from models.notification import Notification
from typing import List

def display(notification: Notification):
    print(f"[{notification.timestamp}] Received by {notification.receiver_id} : {notification.contents}")
    
def display_list(notification: List[Notification]):
    for n in notification:
        display(n)
        
#pretty barren for now, will update as i need more