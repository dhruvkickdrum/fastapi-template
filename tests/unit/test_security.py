"""Unit tests for core security utilities."""
import time

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("MyPass@1")
        assert hashed != "MyPass@1"
        assert len(hashed) > 20

    def test_verify_correct_password(self):
        hashed = hash_password("Correct@1")
        assert verify_password("Correct@1", hashed) is True

    def test_reject_wrong_password(self):
        hashed = hash_password("Correct@1")
        assert verify_password("Wrong@1", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt should produce different salts each time."""
        h1 = hash_password("Same@Pass1")
        h2 = hash_password("Same@Pass1")
        assert h1 != h2
        assert verify_password("Same@Pass1", h1)
        assert verify_password("Same@Pass1", h2)


class TestJWT:
    def test_access_token_decode(self):
        token = create_access_token("test@example.com", role="user")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "access"
        assert payload["role"] == "user"

    def test_refresh_token_decode(self):
        token = create_refresh_token("test@example.com")
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_access_token_is_not_refresh(self):
        token = create_access_token("test@example.com")
        payload = decode_token(token)
        assert payload["type"] != "refresh"

    def test_invalid_token_returns_none(self):
        assert decode_token("not.a.valid.token") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token("test@example.com")
        tampered = token[:-5] + "XXXXX"
        assert decode_token(tampered) is None

    def test_admin_role_in_token(self):
        token = create_access_token("admin@example.com", role="admin")
        payload = decode_token(token)
        assert payload["role"] == "admin"
