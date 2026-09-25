import asyncio

from app.safety.allowlist import AllowlistManager
from app.safety.policy import SafetyPolicy
from app.safety.redaction import redact


# ============================================================
# TEST ALLOWLIST
# ============================================================

def test_allowlist():

    print("\n========================================")
    print("TEST: ALLOWLIST")
    print("========================================")

    manager = AllowlistManager()

    allowed_url = "http://localhost:5173"
    blocked_url = "https://example.com"

    # --------------------------------------------------------
    # Allowed URL
    # --------------------------------------------------------

    try:

        result = manager.is_allowed(
            allowed_url
        )

        print(
            f"\nAllowed URL: {allowed_url}"
        )

        print(
            f"Result: {result}"
        )

        assert result is True

        print("✓ Allowed URL passed")

    except Exception as exc:

        print(
            f"❌ Allowlist test failed: {exc}"
        )

        raise

    # --------------------------------------------------------
    # Blocked URL
    # --------------------------------------------------------

    try:

        result = manager.is_allowed(
            blocked_url
        )

        print(
            f"\nBlocked URL: {blocked_url}"
        )

        print(
            f"Result: {result}"
        )

        assert result is False

        print("✓ Blocked URL passed")

    except Exception as exc:

        print(
            f"❌ Blocked URL test failed: {exc}"
        )

        raise


# ============================================================
# TEST SAFETY POLICY
# ============================================================

def test_safety_policy():

    print("\n========================================")
    print("TEST: SAFETY POLICY")
    print("========================================")

    policy = SafetyPolicy()

    # --------------------------------------------------------
    # Safe action
    # --------------------------------------------------------

    safe_action = {
        "action": "click",
        "target": {
            "strategy": "test_id",
            "value": "search-button",
        },
    }

    try:

        result = policy.check(
            safe_action
        )

        print("\nSafe action:")
        print(result)

        print("✓ Safe action checked")

    except Exception as exc:

        print(
            f"❌ Safe action test failed: {exc}"
        )

        raise

    # --------------------------------------------------------
    # Navigation action
    # --------------------------------------------------------

    navigation_action = {
        "action": "navigate",
        "target": {
            "strategy": "url",
            "value": "https://example.com",
        },
    }

    try:

        result = policy.check(
            navigation_action
        )

        print("\nNavigation action:")
        print(result)

        print("✓ Navigation policy checked")

    except Exception as exc:

        print(
            f"❌ Navigation test failed: {exc}"
        )

        raise


# ============================================================
# TEST REDACTION
# ============================================================

def test_redaction():

    print("\n========================================")
    print("TEST: REDACTION")
    print("========================================")

    data = {
        "username": "john",
        "password": "SuperSecret123",
        "token": "abc123secret",
        "email": "john@example.com",
    }

    print("\nOriginal:")
    print(data)

    try:

        result = redact(data)

        print("\nRedacted:")
        print(result)

        # Password/token should not remain exposed.
        assert (
            "SuperSecret123"
            not in str(result)
        )

        assert (
            "abc123secret"
            not in str(result)
        )

        print(
            "✓ Sensitive information redacted"
        )

    except Exception as exc:

        print(
            f"❌ Redaction test failed: {exc}"
        )

        raise


# ============================================================
# RUN ALL TESTS
# ============================================================

def main():

    print("\n")
    print("########################################")
    print("# COMPUTER-USE SAFETY TESTS")
    print("########################################")

    test_allowlist()

    test_safety_policy()

    test_redaction()

    print("\n########################################")
    print("# ALL SAFETY TESTS PASSED")
    print("########################################")


if __name__ == "__main__":

    main()