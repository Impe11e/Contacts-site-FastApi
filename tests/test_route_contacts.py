from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from src.database.models import User
from main import app


# def test_create_contact(client, contact_data, monkeypatch):
#     mock_init = MagicMock()
#     monkeypatch.setattr("fastapi_limiter.FastAPILimiter.init", mock_init)
#     mock_create_contact = MagicMock()
#     monkeypatch.setattr("src.repository.contacts.create_contact", mock_create_contact)
#     auth_token = "test-token"
#     headers = {"Authorization": f"Bearer {auth_token}"}
#     response = client.post("/api/contacts/", json=contact_data, headers=headers)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["name"] == contact_data["name"]
#     assert data["surname"] == contact_data["surname"]
#     assert "id" in data
#
#     mock_create_contact.assert_called_once_with(contact_data)
#     mock_init.assert_called_once()

# TODO: Finish the implementation later