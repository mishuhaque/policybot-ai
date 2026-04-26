import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.auth import create_access_token

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["msg"] == "PolicyBot API is running"

def test_token_endpoint():
    response = client.post("/token", data={"username": "testuser"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600

def test_ask_without_token():
    response = client.post("/ask", data={"query": "What is the policy?"})
    assert response.status_code == 403
    assert "detail" in response.json()

def test_ask_with_valid_token():
    token = create_access_token({"sub": "testuser"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/ask", data={"query": "What is the parental leave policy?"}, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is the parental leave policy?"
    assert "summary" in data
    assert "top_k" in data
    assert data["requested_by"] == "testuser"

def test_ask_with_invalid_token():
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.post("/ask", data={"query": "What is the policy?"}, headers=headers)
    assert response.status_code == 401

def test_ask_returns_retrieved_chunks():
    token = create_access_token({"sub": "testuser"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/ask", data={"query": "password policy"}, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["top_k"], list)
    assert len(data["top_k"]) > 0

def test_token_with_different_usernames():
    response1 = client.post("/token", data={"username": "user1"})
    response2 = client.post("/token", data={"username": "user2"})

    token1 = response1.json()["access_token"]
    token2 = response2.json()["access_token"]

    assert token1 != token2

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp1 = client.post("/ask", data={"query": "test"}, headers=headers1)
    resp2 = client.post("/ask", data={"query": "test"}, headers=headers2)

    assert resp1.json()["requested_by"] == "user1"
    assert resp2.json()["requested_by"] == "user2"
