"""Tests for multi-admin management endpoints."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
ADMIN_EMAIL = "admin@sirocoproducciones.com"
ADMIN_PASSWORD = "Siroco2026!"


@pytest.fixture(scope="module")
def auth_headers():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}", "Content-Type": "application/json"}


def _throwaway_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


class TestAdminsCRUD:
    def test_list_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/admin/admins", timeout=15)
        assert r.status_code == 401

    def test_list_contains_primary_marked_self(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/admin/admins", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        admins = r.json()
        prim = [a for a in admins if a["email"] == ADMIN_EMAIL]
        assert prim, "primary admin missing"
        assert prim[0]["is_self"] is True

    def test_create_weak_password_400(self, auth_headers):
        email = _throwaway_email()
        r = requests.post(f"{BASE_URL}/api/admin/admins", headers=auth_headers,
                          json={"email": email, "name": "Weak", "password": "short"}, timeout=15)
        assert r.status_code == 400
        # ensure not persisted
        r2 = requests.get(f"{BASE_URL}/api/admin/admins", headers=auth_headers, timeout=15)
        assert not any(a["email"] == email for a in r2.json())

    def test_create_login_delete_flow(self, auth_headers):
        email = _throwaway_email()
        pw = "StrongPass123!"
        # Create
        rc = requests.post(f"{BASE_URL}/api/admin/admins", headers=auth_headers,
                           json={"email": email, "name": "Throwaway", "password": pw}, timeout=15)
        assert rc.status_code == 200, rc.text
        # List verification
        rl = requests.get(f"{BASE_URL}/api/admin/admins", headers=auth_headers, timeout=15)
        assert any(a["email"] == email for a in rl.json())
        # Duplicate -> 400
        rd = requests.post(f"{BASE_URL}/api/admin/admins", headers=auth_headers,
                           json={"email": email, "name": "Dup", "password": pw}, timeout=15)
        assert rd.status_code == 400
        # Login as new admin
        rli = requests.post(f"{BASE_URL}/api/auth/login",
                            json={"email": email, "password": pw}, timeout=15)
        assert rli.status_code == 200
        assert "token" in rli.json()
        # Delete
        rdel = requests.delete(f"{BASE_URL}/api/admin/admins/{email}",
                               headers=auth_headers, timeout=15)
        assert rdel.status_code == 200
        # Verify gone
        rl2 = requests.get(f"{BASE_URL}/api/admin/admins", headers=auth_headers, timeout=15)
        assert not any(a["email"] == email for a in rl2.json())

    def test_cannot_delete_self(self, auth_headers):
        r = requests.delete(f"{BASE_URL}/api/admin/admins/{ADMIN_EMAIL}",
                            headers=auth_headers, timeout=15)
        assert r.status_code == 400
