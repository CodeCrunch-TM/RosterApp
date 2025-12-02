from App.models.notification import Notification
from App.database import db

notifications = []

def create_notification(receiver_id, contents):
    #Create a new notification and add it to the list
    notif_id = len(notifications) + 1 #just take the array size and +1 to maintain unique ids
    notification = Notification(notif_id, receiver_id, contents)
    notifications.append(notification)
    return notification

def get_user_notifications(receiever_id):
    #Retrieve all notifications for a specific user
    return [n for n in notifications if n.receiver_id == receiever_id]

def mark_as_read(notification_id):
    # Mark a specific notification as read.
    for n in notifications:
        if n.notif_id == notification_id:
            n.read = True
            return n
    return None

def clear_notifications(receiver_id):
    #remove all notifications for a specific user
    global notifications
    notifications = [n for n in notifications if n.receiver_id != receiver_id]
    return True