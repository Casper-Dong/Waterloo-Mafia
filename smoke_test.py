"""
Smoke tests for the Modal backend integration.

These tests verify the backend module structure and core logic
without requiring a live Modal deployment (no network calls made).

Run with:  python -m pytest smoke_test.py -v
"""

import importlib
import sys
import types
import unittest


# ---------------------------------------------------------------------------
# Minimal stubs so the Modal SDK is not required at test time
# ---------------------------------------------------------------------------

def _build_modal_stub() -> types.ModuleType:
    """Return a lightweight mock of the `modal` package."""
    modal_mod = types.ModuleType("modal")

    # A no-op decorator factory used for @app.function() and @modal.web_endpoint(...)
    def _noop_decorator(*args, **kwargs):
        def decorator(fn):
            return fn
        # Support both @decorator and @decorator(...) styles
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]
        return decorator

    class _FakeApp:
        def __init__(self, name: str):
            self.name = name

        def function(self, *args, **kwargs):
            return _noop_decorator(*args, **kwargs)

    modal_mod.App = _FakeApp
    modal_mod.web_endpoint = _noop_decorator
    modal_mod.Response = None
    return modal_mod


# Inject the stub before importing the backend module
sys.modules.setdefault("modal", _build_modal_stub())

import modal_backend  # noqa: E402 – must come after stub injection


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestModalBackendStructure(unittest.TestCase):
    """Verify that the Modal backend module has the expected structure."""

    def test_app_created(self):
        """modal_backend.app must be a Modal App instance."""
        self.assertIsNotNone(modal_backend.app)
        self.assertEqual(modal_backend.app.name, "waterloo-mafia")

    def test_members_constant_not_empty(self):
        """MEMBERS list must contain at least one entry."""
        self.assertIsInstance(modal_backend.MEMBERS, list)
        self.assertGreater(len(modal_backend.MEMBERS), 0)

    def test_members_have_required_keys(self):
        """Every member dict must expose 'name' and 'url'."""
        for member in modal_backend.MEMBERS:
            self.assertIn("name", member, f"Missing 'name' in {member}")
            self.assertIn("url", member, f"Missing 'url' in {member}")

    def test_members_urls_are_https(self):
        """All member URLs should use HTTPS."""
        for member in modal_backend.MEMBERS:
            self.assertTrue(
                member["url"].startswith("https://"),
                f"URL for {member['name']} is not HTTPS: {member['url']}",
            )

    def test_members_endpoint_callable(self):
        """The `members` endpoint function must be importable and callable."""
        self.assertTrue(callable(modal_backend.members))

    def test_health_endpoint_callable(self):
        """The `health` endpoint function must be importable and callable."""
        self.assertTrue(callable(modal_backend.health))


class TestMembersEndpointLogic(unittest.TestCase):
    """Smoke-test the endpoint return values without a live Modal runtime."""

    def test_members_returns_dict_with_members_key(self):
        result = modal_backend.members()
        self.assertIsInstance(result, dict)
        self.assertIn("members", result)

    def test_members_returns_correct_count(self):
        result = modal_backend.members()
        self.assertEqual(len(result["members"]), len(modal_backend.MEMBERS))

    def test_health_returns_ok(self):
        result = modal_backend.health()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")

    def test_health_identifies_service(self):
        result = modal_backend.health()
        self.assertEqual(result.get("service"), "waterloo-mafia-backend")

    def test_known_members_present(self):
        """The five founding members must be present."""
        result = modal_backend.members()
        names = {m["name"] for m in result["members"]}
        for expected in ("kevin", "casper", "shayaan", "daniel", "chinmay"):
            self.assertIn(expected, names, f"Missing member: {expected}")


if __name__ == "__main__":
    unittest.main()
