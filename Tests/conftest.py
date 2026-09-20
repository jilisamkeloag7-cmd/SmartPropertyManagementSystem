"""
Pytest fixtures for SPMS tests.

Creates an isolated temporary SQLite database so tests never touch
the development/production database.
"""

import os
import tempfile
import pytest

# ---- IMPORTANT: set env var BEFORE importing any app module
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["SPMS_DATABASE_URL"] = f"sqlite:///{_tmp.name}"

# Now safe to import app modules
from Database.connection import engine, get_session, Session  # noqa: E402
from Models.base import Base  # noqa: E402
import Models  # noqa: E402,F401  — registers all models
from Models.user import User, UserRole  # noqa: E402
from Services.security import hash_password  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _session_db_setup():
    Base.metadata.create_all(engine)
    yield
    Session.remove()
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def _clean_session_after_each():
    yield
    Session.remove()


@pytest.fixture
def fresh_db():
    """Drop + recreate all tables. Runs before every test that needs it."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def seeded_db(fresh_db):
    """
    Fresh DB with 4 users: admin / manager / owner / tenant.
    Returns a dict of session_user-style dicts.
    """
    db = get_session()
    try:
        admin = User(
            id_number="ADM001", name="Admin User", email="admin@test.local",
            phone="1000000001", password_hash=hash_password("admin123"),
            role=UserRole.ADMIN, status="Active",
        )
        manager = User(
            id_number="MGR001", name="Manager User", email="mgr@test.local",
            phone="1000000002", password_hash=hash_password("mgr123"),
            role=UserRole.MANAGER, status="Active",
        )
        owner = User(
            id_number="OWN001", name="Owner User", email="own@test.local",
            phone="1000000003", password_hash=hash_password("own123"),
            role=UserRole.OWNER, status="Active",
        )
        tenant = User(
            id_number="TEN001", name="Tenant User", email="ten@test.local",
            phone="1000000004", password_hash=hash_password("ten123"),
            role=UserRole.TENANT, status="Active",
        )
        db.add_all([admin, manager, owner, tenant])
        db.commit()
        db.refresh(admin); db.refresh(manager); db.refresh(owner); db.refresh(tenant)
    finally:
        db.close()

    return {
        "admin":   {"user_id": admin.user_id,  "role": "Administrator",    "name": "Admin User",   "email": "admin@test.local"},
        "manager": {"user_id": manager.user_id,"role": "Property Manager", "name": "Manager User", "email": "mgr@test.local"},
        "owner":   {"user_id": owner.user_id,  "role": "Owner",            "name": "Owner User",   "email": "own@test.local"},
        "tenant":  {"user_id": tenant.user_id, "role": "Tenant",           "name": "Tenant User",  "email": "ten@test.local"},
    }