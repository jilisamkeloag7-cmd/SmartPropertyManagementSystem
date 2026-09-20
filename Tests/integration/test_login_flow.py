print(">>> test_login_flow.py <<<")

from Services.auth_service import AuthService


class TestLoginIntegration:

    def test_successful_login_returns_user_dict(self, seeded_db):
        """End-to-end: authenticate → verify user dict shape."""
        ok, user, err = AuthService().authenticate(
            "mgr@test.local", "mgr123", "Property Manager"
        )
        assert ok is True
        # Required keys for dashboard
        assert set(user.keys()) >= {"user_id", "name", "email", "role"}
        assert user["role"] == "Property Manager"

    def test_full_login_then_dashboard_stats(self, seeded_db):
        """Authenticate then aggregate dashboard stats for that user."""
        ok, user, err = AuthService().authenticate(
            "admin@test.local", "admin123", "Administrator"
        )
        assert ok is True

        from Services.dashboard_service import DashboardService
        stats = DashboardService().aggregate_for(user)
        assert stats["role"] == "Administrator"
        assert isinstance(stats["stats"], list)
        assert any(s["label"] == "Users" for s in stats["stats"])