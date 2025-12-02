from App.database import db
from .user import User
from App.interfaces.Observer import Observer

class Staff(User, Observer):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "staff",
    }

    def __init__(self, username, password):
        super().__init__(username, password, "staff")
        
    def update(self, observable_roster):
        from App.controllers.notification import create_notification
        # Get schedule name
        schedule_name = getattr(observable_roster, 'name', 'Schedule')
        
        # Create notification
        message = f"Schedule '{schedule_name}' has been updated with new shifts"
        notification = create_notification(self.id, message)
        
        return notification