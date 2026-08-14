"""Gallery endpoints tests for Siroco Producciones."""
import io
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://flamenco-multiidioma.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@sirocoproducciones.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Siroco2026!")


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# 1x1 PNG (89 bytes)
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c6300010000000500010d0a2db40000000049454e44ae426082"
)


class TestGallery:
    uploaded_id = None
    uploaded_url = None

    def test_upload_requires_auth(self):
        files = {"file": ("t.png", io.BytesIO(PNG_BYTES), "image/png")}
        r = requests.post(f"{BASE_URL}/api/admin/gallery", files=files, timeout=30)
        assert r.status_code in (401, 403)

    def test_upload_ok(self, auth_headers):
        files = {"file": ("TEST_gallery.png", io.BytesIO(PNG_BYTES), "image/png")}
        r = requests.post(f"{BASE_URL}/api/admin/gallery",
                          headers=auth_headers, files=files, timeout=60)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data and "url" in data
        assert data["url"].startswith("/api/files/")
        TestGallery.uploaded_id = data["id"]
        TestGallery.uploaded_url = data["url"]

    def test_admin_list_contains_upload(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/admin/gallery", headers=auth_headers, timeout=30)
        assert r.status_code == 200
        ids = [it["id"] for it in r.json()]
        assert TestGallery.uploaded_id in ids

    def test_public_list_contains_upload(self):
        r = requests.get(f"{BASE_URL}/api/gallery", timeout=30)
        assert r.status_code == 200
        ids = [it["id"] for it in r.json()]
        assert TestGallery.uploaded_id in ids

    def test_file_served(self):
        r = requests.get(f"{BASE_URL}{TestGallery.uploaded_url}", timeout=30)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("image/")
        assert len(r.content) > 10

    def test_delete_ok(self, auth_headers):
        r = requests.delete(f"{BASE_URL}/api/admin/gallery/{TestGallery.uploaded_id}",
                            headers=auth_headers, timeout=30)
        assert r.status_code == 200
        # verify removed from public list
        r2 = requests.get(f"{BASE_URL}/api/gallery", timeout=30)
        ids = [it["id"] for it in r2.json()]
        assert TestGallery.uploaded_id not in ids
