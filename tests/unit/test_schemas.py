"""Unit tests for Pydantic schema validation."""
import pytest
from pydantic import ValidationError

from app.schemas.user import UserRegister


class TestUserRegisterSchema:
    def _valid(self, **overrides) -> dict:
        base = {
            "email": "test@example.com",
            "password": "Valid@Pass1",
            "full_name": "Test User",
        }
        return {**base, **overrides}

    def test_valid_payload(self):
        user = UserRegister(**self._valid())
        assert user.email == "test@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserRegister(**self._valid(email="not-an-email"))

    @pytest.mark.parametrize(
        "password",
        [
            "short1A!",          # valid (exactly 8)
            "nouppercase1!",     # missing uppercase
            "NOLOWERCASE1!",     # missing lowercase
            "NoDigitHere!",      # missing digit
            "NoSpecial123",      # missing special char
        ],
    )
    def test_weak_passwords(self, password):
        valid = all([
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(c in "!@#$%^&*(),.?\":{}|<>" for c in password),
            len(password) >= 8,
        ])
        if valid:
            # Should not raise
            UserRegister(**self._valid(password=password))
        else:
            with pytest.raises(ValidationError):
                UserRegister(**self._valid(password=password))

    def test_full_name_is_stripped(self):
        user = UserRegister(**self._valid(full_name="  Alice  "))
        assert user.full_name == "Alice"

    def test_full_name_optional(self):
        payload = self._valid()
        del payload["full_name"]
        user = UserRegister(**payload)
        assert user.full_name is None
