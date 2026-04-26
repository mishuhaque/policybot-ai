import pytest
from datetime import timedelta
from jose import jwt
from src.auth import create_access_token, SECRET_KEY, ALGORITHM

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_create_access_token_with_expiration():
    data = {"sub": "testuser"}
    expires_delta = timedelta(hours=1)
    token = create_access_token(data, expires_delta)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "testuser"
    assert "exp" in payload

def test_token_contains_subject():
    username = "john_doe"
    token = create_access_token({"sub": username})

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == username

def test_token_signature_valid():
    token = create_access_token({"sub": "user123"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload is not None
    except jwt.JWTError:
        pytest.fail("Token signature is invalid")
