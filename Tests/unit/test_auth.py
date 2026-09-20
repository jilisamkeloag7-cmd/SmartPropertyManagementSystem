print(">>> test_auth.py <<<")

import pytest
from Services.security import hash_password, verify_password
from Services.auth_service import AuthService


# -------------------------------------------------------------- security
class TestSecurity:

    def test_hash_then_verify_ok(self):
        h = hash_password("correct horse battery")
        assert verify_password("correct horse battery", h) is True

    def test_verify_wrong_password(self):
        h = hash_password("right")
        assert verify_password("wrong", h) is False

    def test_hash_is_not_plaintext(self):
        h = hash_password("hello")
        assert "hello" not in h
        assert h.startswith("$2")


# -------------------------------------------------------------- login
class TestAuthService:

    def test_login_success(self, seeded_db):
        svc = AuthService()
        ok, user, err = svc.authenticate("admin@test.local", "admin123", "Administrator")
        assert ok is True
        assert user is not None
        assert user["role"] == "Administrator"
        assert err is None

    def test_login_wrong_password(self, seeded_db):
        svc = AuthService()
        ok, user, err = svc.authenticate("admin@test.local", "wrongpass", "Administrator")
        assert ok is False
        assert user is None
        assert "Incorrect password" in err

    def test_login_unknown_user(self, seeded_db):
        svc = AuthService()
        ok, user, err = svc.authenticate("ghost@nowhere.local", "x", "Administrator")
        assert ok is False
        assert "No account found" in err

    def test_login_role_mismatch(self, seeded_db):
        svc = AuthService()
        ok, user, err = svc.authenticate("admin@test.local", "admin123", "Tenant")
        assert ok is False
        assert "not registered as Tenant" in err

    def test_login_email_case_insensitive(self, seeded_db):
        svc = AuthService()
        ok, user, err = svc.authenticate("ADMIN@TEST.LOCAL", "admin123", "Administrator")
        assert ok is True

    def test_login_missing_fields(self, seeded_db):
        svc = AuthService()
        ok, user, err = svc.authenticate("", "", "Administrator")
        assert ok is False
        assert "enter both" in err.lower()

    def test_login_inactive_account(self, seeded_db):
        from Database.connection import get_session
        from Models.user import User
        db = get_session()
        try:
            u = db.query(User).filter(User.email == "ten@test.local").first()
            u.status = "Inactive"
            db.commit()
        finally:
            db.close()

        svc = AuthService()
        ok, user, err = svc.authenticate("ten@test.local", "ten123", "Tenant")
        assert ok is False
        assert "deactivated" in err.lower()