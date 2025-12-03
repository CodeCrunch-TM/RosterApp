import unittest, pytest
from datetime import datetime
from App.database import db, create_db
from App.models import User
from App.controllers import create_user, get_user, update_user, get_all_users_json, loginCLI

@pytest.fixture(autouse=True)
def clean_db():
    db.drop_all()
    create_db()
    db.session.remove()
    yield

class UserTests(unittest.TestCase):
    """Unit and Integration tests for User entity"""

    # ---- Unit Tests ----
    @pytest.mark.unit
    def test_new_user_admin(self):
        user = create_user("bot", "bobpass","admin")
        self.assertEqual(user.username, "bot")

    @pytest.mark.unit
    def test_new_user_staff(self):
        user = create_user("pam", "pampass","staff")
        self.assertEqual(user.username, "pam")

    @pytest.mark.unit
    def test_create_user_invalid_role(self):
        user = create_user("jim", "jimpass","ceo")
        self.assertIsNone(user)

    @pytest.mark.unit
    def test_get_json(self):
        user = User("bob", "bobpass", "admin")
        self.assertDictEqual(user.get_json(), {"id": None, "username":"bob","role":"admin"})

    @pytest.mark.unit
    def test_hashed_password(self):
        password = "mypass"
        user = User("tester", password)
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))
      
    @pytest.mark.unit  
    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password

    # ---- Integration Tests ----
    @pytest.mark.int
    def test_create_and_get_user(self):
        user = create_user("alex", "alexpass", "staff")
        retrieved = get_user(user.id)
        self.assertEqual(retrieved.username, "alex")
        self.assertEqual(retrieved.role, "staff")

    @pytest.mark.int
    def test_update_user(self):
        user = create_user("bot", "bobpass","admin")
        update_user(user.id, "ronnie")
        user = get_user(user.id)
        self.assertEqual(user.username, "ronnie")

    @pytest.mark.int
    def test_get_all_users_json_integration(self):
        create_user("bot", "bobpass", "admin")
        create_user("pam", "pampass", "staff")
        users_json = get_all_users_json()
        expected = [
            {"id": 1, "username": "bot", "role": "admin"},
            {"id": 2, "username": "pam", "role": "staff"},
        ]
        self.assertEqual(users_json, expected)

    @pytest.mark.int
    def test_authenticate(self):
        user = User("bob", "bobpass","user")
        self.assertIsNotNone(loginCLI("bob", "bobpass"))
      
    @pytest.mark.int  
    def test_get_all_users_json(self):
        user = create_user("bot", "bobpass","admin")
        user = create_user("pam", "pampass","staff")
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bot", "role":"admin"}, {"id":2, "username":"pam","role":"staff"}], users_json)

    @pytest.mark.int
    def test_update_user(self):
        user = create_user("bot", "bobpass","admin")
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"

    @pytest.mark.int
    def test_create_and_get_user(self):
        user = create_user("alex", "alexpass", "staff")
        retrieved = get_user(user.id)
        self.assertEqual(retrieved.username, "alex")
        self.assertEqual(retrieved.role, "staff")
    
    @pytest.mark.int
    def test_get_all_users_json_integration(self):
        create_user("bot", "bobpass", "admin")
        create_user("pam", "pampass", "staff")
        users_json = get_all_users_json()
        expected = [
            {"id": 1, "username": "bot", "role": "admin"},
            {"id": 2, "username": "pam", "role": "staff"},
        ]
        self.assertEqual(users_json, expected)