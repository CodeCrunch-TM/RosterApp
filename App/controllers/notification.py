from App.models.notification import Notification
from App.database import db

notifications = []

#Create a new notification and add it to the list
def create_notification(receiver_id, message):
    notification = Notification(receiver_id=receiver_id, message=message)
    db.session.add(notification)
    db.session.commit()
    return notification

#Retrieve all notifications for a specific user
def get_user_notifications(receiver_id):
    return Notification.query.filter_by(
        receiver_id=receiver_id
    ).order_by(Notification.timestamp.desc()).all()

# Mark a specific notification as read.
def mark_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification:
        notification.read = True
        db.session.commit()
        return notification
    return None

#Remove all notifications for a specific user
def clear_notifications(receiver_id):
    Notification.query.filter_by(receiver_id=receiver_id).delete()
    db.session.commit()
    return True