import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator

from fastapi import Depends
from database.database import Base, get_db
from main import app
from models.user import User
from models.user_role import UserRole
from schemas.authentication_schemas import create_access_token, create_refresh_token

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user(test_db):
    # Create a test user
    user = User(
        email="test@example.com",
        username="testuser",
        nickname="Test User",
        hashed_password="$2b$12$RBxWZvlZt9o./JubwxUFPOZ9xvKyBKJuOK8QYV.IYG3YeRRDZq0Q.",  # hashed 'password'
        role=UserRole.SUBSCRIBER.value
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def admin_user(test_db):
    # Create an admin user
    user = User(
        email="admin@example.com",
        username="adminuser",
        nickname="Admin User",
        hashed_password="$2b$12$RBxWZvlZt9o./JubwxUFPOZ9xvKyBKJuOK8QYV.IYG3YeRRDZq0Q.",  # hashed 'password'
        role=UserRole.ADMIN.value
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_user_token(test_user):
    return {
        "access_token": create_access_token(data={"sub": test_user.email}),
        "refresh_token": create_refresh_token(data={"sub": test_user.email})
    }

@pytest.fixture
def admin_user_token(admin_user):
    return {
        "access_token": create_access_token(data={"sub": admin_user.email}),
        "refresh_token": create_refresh_token(data={"sub": admin_user.email})
    }

@pytest.fixture
def authenticated_client(client, test_user_token):
    """Return a client with valid authentication token."""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user_token['access_token']}"
    }
    return client

@pytest.fixture
def admin_client(client, admin_user_token):
    """Return a client with valid admin authentication token."""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {admin_user_token['access_token']}"
    }
    return client 