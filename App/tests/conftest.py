# File: tests/conftest.py
import pytest
from App.main import create_app
from App.database import db, create_db

@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"
    })
    with app.app_context():
        create_db()
    yield app

@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Reset the database before each test function."""
    with app.app_context():
        db.drop_all()
        create_db()
        db.session.remove()
    yield
