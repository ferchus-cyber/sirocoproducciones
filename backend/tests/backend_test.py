"""Backend API tests for Siroco Producciones."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://flamenco-multiidioma.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@sirocoproducciones.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Siroco2026!")


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
        assert "hero" in data and "origin" in data
        # artists feature fully removed
        assert "artists" not in data, "artists key must not appear in /api/site"
        assert data["hero"].get("tagline")
        assert data["ui"].get("nav_events") == "Eventos"

    def test_site_en_nav_events_translated(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "en"}, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert "hero" in data
        assert "artists" not in data
        nav_events = data["ui"].get("nav_events")
        assert nav_events, "ui.nav_events missing for lang=en"
        # should be translated (not still 'Eventos')
        assert nav_events.lower() != "eventos", f"nav_events not translated: {nav_events}"

    def test_site_invalid_lang_defaults_es(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "xx"}, timeout=30)
        assert r.status_code == 200

    def test_site_en_services_title(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "en"}, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert data["ui"].get("nav_events") == "Events"
        assert data["ui"].get("services_title") == "Services"

    def test_site_de_no_crash_translated(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "de"}, timeout=90)
        assert r.status_code == 200
        data = r.json()
        assert "hero" in data and data["ui"].get("nav_events")
        # Should not remain as Spanish "Eventos" after translation
        # (allow fallback on very rare LLM failure but at least no crash)

    def test_site_fr_no_crash_translated(self, api):
        r = api.get(f"{BASE_URL}/api/site", params={"lang": "fr"}, timeout=90)
        assert r.status_code == 200
        data = r.json()
        assert "hero" in data and data["ui"].get("nav_events")


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
        assert data.get("success")
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
        data = r.json()
        assert "hero" in data
        # artists removed from admin content too
        assert "artists" not in data

    def test_update_content_hero(self, auth_headers):
        # read
        r0 = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        original_content = r0.json()
        original_hero = original_content["hero"]
        new_hero = dict(original_hero)
        new_hero["tagline"] = f"TEST_TAGLINE_{uuid.uuid4().hex[:6]}"
        payload = dict(original_content)
        payload["hero"] = new_hero
        r = requests.put(f"{BASE_URL}/api/admin/content",
                         headers=auth_headers, json=payload, timeout=30)
        assert r.status_code == 200, r.text
        # verify persisted
        r2 = requests.get(f"{BASE_URL}/api/admin/content", headers=auth_headers, timeout=30)
        assert r2.json()["hero"]["tagline"] == new_hero["tagline"]
        # restore
        payload["hero"] = original_hero
        requests.put(f"{BASE_URL}/api/admin/content",
                     headers=auth_headers, json=payload, timeout=30)

    def test_artist_endpoints_removed(self, auth_headers):
        new_id = str(uuid.uuid4())
        payload = {"id": new_id, "name": "TEST_Artist", "role": "Test",
                   "bio": "bio", "image": "/media/test.jpg", "order": 99}
        r = requests.post(f"{BASE_URL}/api/admin/artists",
                          headers=auth_headers, json=payload, timeout=30)
        assert r.status_code == 404, f"POST /api/admin/artists should be 404, got {r.status_code}"
        r_u = requests.put(f"{BASE_URL}/api/admin/artists/{new_id}",
                           headers=auth_headers, json=payload, timeout=30)
        assert r_u.status_code == 404
        r_d = requests.delete(f"{BASE_URL}/api/admin/artists/{new_id}",
                              headers=auth_headers, timeout=30)
        assert r_d.status_code == 404

    def test_messages_require_auth(self):
        r = requests.get(f"{BASE_URL}/api/admin/messages", timeout=15)
        assert r.status_code == 401
