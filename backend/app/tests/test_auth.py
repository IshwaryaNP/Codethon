import pytest
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token

def test_password_hashing():
    raw_pwd = "SecurePassword123!"
    hashed = hash_password(raw_pwd)
    assert hashed != raw_pwd
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_flow():
    user_id = "user_12345"
    token = create_access_token({"sub": user_id, "email": "test@example.com"})
    assert token is not None and isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["email"] == "test@example.com"

def test_invalid_jwt():
    bad_payload = decode_access_token("invalid.jwt.token")
    assert bad_payload is None
