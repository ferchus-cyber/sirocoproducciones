"""Backend API tests for Siroco Producciones."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://flamenco-multiidioma.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@sirocoproducciones.com"
ADMIN_PASSWORD = "Siroco2026!"


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def token(api):
    r = api.post(f"{BASE_URL}/api/auth/login",
                 json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# --- Public: /api/site ---
class TestSite:
    def test_site_es(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "es"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "hero" in data and "artists" in data and "origin" in data
        assert len(data["artists"]) >= 8
        assert data["hero"].get("tagline")

    def test_site_en_no_crash(self, api):
        # LLM key has 0 balance -> should fall back to Spanish, but must NOT crash
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "en"}, timeout=60)
        assert r.status_code == 200
        assert "hero" in r.json()

    def test_site_invalid_lang_defaults_es(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "xx"}, timeout=30)
        assert r.status_code == 200


# --- Public: /api/contact ---
class TestContact:
    submitted_subject = f"TEST_{uuid.uuid4().hex[:8]}"

    def test_create_contact(self, api):
        payload = {
            "name": "TEST_User",
            "email": "test.user@example.com",
            "subject": self.__class__.submitted_subject,
            "message": "This is an automated test message.",
        }
        r = api.post(f"{BASE_URL}/api/contact", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("success") is True
        assert "id" in data

    def test_contact_persisted_in_admin(self, api, auth_headers):
        r = requests.get(f"{BASE_URL}/api/admin/messages", headers=auth_headers, timeout=30)
        assert r.status_code == 200
        msgs = r.json()
        assert any(m.get("subject") == self.__class__.submitted_subject for m in msgs), \
            "Contact message not found in admin listing"

    def test_contact_invalid_email(self, api):
        r = api.post(f"{BASE_URL}/api/contact",
                     json={"name": "x", "email": "not-an-email", "subject": "s", "message": "m"}, timeout=15)
        assert r.status_code in (400, 422)


# --- Auth ---
class TestAuth:
    def test_login_ok(self, api):
        r = api.post(f"{BASE_URL}/api/auth/login",
                     json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert "token" in d and d["user"]["email"] == ADMIN_EMAIL

    def test_login_bad_password(self, api):
        r = api.post(f"{BASE_URL}/api/auth/login",
                     json={"email": ADMIN_EMAIL, "password": "wrong-pass"}, timeout=15)
        assert r.status_code == 401

    def test_me_requires_auth(self, api):
        r = api.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 401

    def test_me_ok(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN_EMAIL


# --- Admin content + artists CRUD ---
class TestAdmin:
    def test_get_admin_content(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        assert r.status_code == 200
        assert "hero" in r.json() and "artists" in r.json()

    def test_update_content_hero(self, auth_headers):
        # read
        r0 = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        original = r0.json()["hero"]
        new_hero = dict(original)
        new_hero["tagline"] = f"TEST_TAGLINE_{uuid.uuid4().hex[:6]}"
        r = requests.put(f"{BASE_URL}/api/admin/content",
                         headers=auth_headers, json={"hero": new_hero}, timeout=30)
        assert r.status_code == 200
        # verify persisted
        r2 = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        assert r2.json()["hero"]["tagline"] == new_hero["tagline"]
        # restore
        requests.put(f"{BASE_URL}/api/admin/content",
                     headers=auth_headers, json={"hero": original}, timeout=30)

    def test_artist_crud(self, auth_headers):
        new_id = str(uuid.uuid4())
        payload = {"id": new_id, "name": "TEST_Artist", "role": "Test",
                   "bio": "bio", "image": "/media/test.jpg", "order": 99}
        # CREATE
        r = requests.post(f"{BASE_URL}/api/admin/artists",
                          headers=auth_headers, json=payload, timeout=30)
        assert r.status_code == 200
        # verify in listing
        r_all = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        ids = [a["id"] for a in r_all.json()["artists"]]
        assert new_id in ids
        # UPDATE
        payload["name"] = "TEST_Artist_Updated"
        r_u = requests.put(f"{BASE_URL}/api/admin/artists/{new_id}",
                           headers=auth_headers, json=payload, timeout=30)
        assert r_u.status_code == 200
        assert r_u.json()["name"] == "TEST_Artist_Updated"
        # DELETE
        r_d = requests.delete(f"{BASE_URL}/api/admin/artists/{new_id}",
                              headers=auth_headers, timeout=30)
        assert r_d.status_code == 200
        # verify deleted
        r_all2 = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        ids2 = [a["id"] for a in r_all2.json()["artists"]]
        assert new_id not in ids2

    def test_messages_require_auth(self):
        r = requests.get(f"{BASE_URL}/api/admin/messages", timeout=15)
        assert r.status_code == 401
