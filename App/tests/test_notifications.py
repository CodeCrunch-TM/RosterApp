import unittest
from datetime import datetime
from App.main import create_app
from App.database import db
from App.models import User, Notification
from App.controllers.notification import (
    create_notification,
    get_user_notifications,
    mark_as_read,
    clear_notifications
)
from App.controllers.user import create_user

class NotificationUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()
    
    def setUp(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
    
    #Test notification creation
    def test_create_notification(self):
        with self.app.app_context():
            user = create_user("test_user", "password", "staff")
            notification = create_notification(user.id, "Test message")
            
            self.assertIsNotNone(notification.id)
            self.assertEqual(notification.receiver_id, user.id)
            self.assertEqual(notification.message, "Test message")
            self.assertFalse(notification.read)
    
    #Test retrieving user notifications
    def test_get_user_notifications(self):
        with self.app.app_context():
            user = create_user("staff1", "password", "staff")
            create_notification(user.id, "Message 1")
            create_notification(user.id, "Message 2")
            
            notifications = get_user_notifications(user.id)
            self.assertEqual(len(notifications), 2)
            # Should be ordered by timestamp DESC
            self.assertEqual(notifications[0].message, "Message 2")
    
    #Test marking notification as read
    def test_mark_as_read(self):
        with self.app.app_context():
            user = create_user("staff2", "password", "staff")
            notification = create_notification(user.id, "Test")
            
            self.assertFalse(notification.read)
            
            updated = mark_as_read(notification.id)
            self.assertTrue(updated.read)
    
    # Test clearing notifications
    def test_clear_notifications(self):
        with self.app.app_context():
            user = create_user("staff3", "password", "staff")
            create_notification(user.id, "Message 1")
            create_notification(user.id, "Message 2")
            
            clear_notifications(user.id)
            
            notifications = get_user_notifications(user.id)
            self.assertEqual(len(notifications), 0)
    
    # Test Notification model's to_json method
    def test_notification_to_json(self):
        with self.app.app_context():
            user = create_user("staff4", "password", "staff")
            notification = create_notification(user.id, "JSON test")
            
            json_data = notification.to_json()
            
            self.assertIn("id", json_data)
            self.assertIn("receiver_id", json_data)
            self.assertIn("message", json_data)
            self.assertIn("read", json_data)
            self.assertIn("timestamp", json_data)

# Notification API Tests
class NotificationAPITests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()
    
    def setUp(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            self.user = create_user("api_staff", "password", "staff")
            
            # Login to get token
            response = self.client.post('/api/login', 
                json={'username': 'api_staff', 'password': 'password'})
            self.token = response.json.get('access_token')
    
    #Test GET /api/notifications
    def test_get_notifications_api(self):
        with self.app.app_context():
            create_notification(self.user.id, "API Test 1")
            create_notification(self.user.id, "API Test 2")
        
        response = self.client.get('/api/notifications',
            headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
    
    #Test POST /api/notifications/<id>/read
    def test_mark_notification_read_api(self):
        with self.app.app_context():
            notification = create_notification(self.user.id, "Read test")
            notif_id = notification.id
        
        response = self.client.post(f'/api/notifications/{notif_id}/read',
            headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['read'])
    
    #Test that users can't mark other's notifications as read
    def test_mark_notification_unauthorized(self):
        with self.app.app_context():
            other_user = create_user("other_staff", "password", "staff")
            notification = create_notification(other_user.id, "Not yours")
            notif_id = notification.id
        
        response = self.client.post(f'/api/notifications/{notif_id}/read',
            headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()