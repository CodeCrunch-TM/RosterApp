from datetime import datetime
from App.database import db

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            "id": self.id,
            "receiver_id": self.receiver_id,
            "message": self.message,
            "read": self.read,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
        
    def get_json(self):
        return self.to_json()