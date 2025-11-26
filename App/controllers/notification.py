from models.notification import Notification

notifications = []

def create_notification(receiver_id, contents):
    notif_id = len(notifications) + 1 #just take the array size and +1 to maintain unique ids
    notification = Notification(notif_id, receiver_id, contents)
    notifications.append(notification)
    return notification

def get_user_notifications(receiever_id):
    return [n for n in notifications if n.receiver_id == receiever_id] #if any of you need this explained i will seriously question your intelligence

#might need to add more stuff later, maybe to clear all notifs or get by sender for call tracing and debugging