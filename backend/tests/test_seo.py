"""SEO audit tests for Siroco Producciones site."""
import json
import os
import re
import pytest
import requests
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
CANONICAL = "https://www.sirocoproducciones.es/"


@pytest.fixture(scope="module")
def html():
    r = requests.get(BASE_URL + "/", timeout=30)
    assert r.status_code == 200
    return r.text


class TestHeadSEO:
    def test_lang_es(self, html):
        assert re.search(r'<html[^>]*lang="es"', html)

    def test_title(self, html):
        assert "<title>Siroco Producciones | Producción de Espectáculos Musicales y Flamenco</title>" in html

    def test_meta_description(self, html):
        m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
        assert m
        desc = m.group(1).lower()
        assert "siroco" in desc and ("flamenco" in desc or "conciertos" in desc)

    def test_robots_index_follow(self, html):
        assert re.search(r'<meta\s+name="robots"\s+content="index,\s*follow"', html)

    def test_no_noindex(self, html):
        assert "noindex" not in html.lower()

    def test_canonical(self, html):
        assert f'<link rel="canonical" href="{CANONICAL}"' in html


class TestOpenGraph:
    def test_og_tags(self, html):
        for prop, val in [
            ("og:type", "website"),
            ("og:site_name", "Siroco Producciones"),
            ("og:url", CANONICAL),
            ("og:image", "https://www.sirocoproducciones.es/og-image.jpg"),
            ("og:locale", "es_ES"),
        ]:
            assert re.search(rf'property="{re.escape(prop)}"\s+content="{re.escape(val)}"', html), f"missing {prop}"
        assert re.search(r'property="og:title"\s+content="[^"]+"', html)
        assert re.search(r'property="og:description"\s+content="[^"]+"', html)

    def test_twitter_card(self, html):
        assert re.search(r'name="twitter:card"\s+content="summary_large_image"', html)
        for k in ("twitter:title", "twitter:description", "twitter:image"):
            assert re.search(rf'name="{k}"\s+content="[^"]+"', html), f"missing {k}"


class TestStructuredData:
    def test_jsonld_valid_org(self, html):
        m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
        assert m, "JSON-LD script not found"
        data = json.loads(m.group(1))
        assert data["@type"] == "Organization"
        assert data["name"] == "Siroco Producciones"
        assert data["telephone"] == "+34679360643"
        assert data["address"]["addressLocality"] == "San Fernando"
        assert data["address"]["addressRegion"] == "Cádiz"
        assert data["address"]["addressCountry"] == "ES"
        sameas = " ".join(data.get("sameAs", []))
        assert "instagram.com" in sameas and "youtube.com" in sameas
        assert "EntertainmentBusiness" in data.get("additionalType", "")


class TestAssets:
    @pytest.mark.parametrize("path,ctype", [
        ("/favicon.png", "image/png"),
        ("/apple-touch-icon.png", "image/png"),
        ("/og-image.jpg", "image/jpeg"),
    ])
    def test_asset(self, path, ctype):
        r = requests.get(BASE_URL + path, timeout=30)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert ctype in r.headers.get("content-type", "").lower(), f"{path} ctype={r.headers.get('content-type')}"

    def test_head_references(self, html):
        assert 'rel="icon"' in html and "/favicon.png" in html
        assert 'rel="apple-touch-icon"' in html and "/apple-touch-icon.png" in html


class TestRobotsSitemap:
    def test_robots(self):
        r = requests.get(BASE_URL + "/robots.txt", timeout=30)
        assert r.status_code == 200
        assert "Allow: /" in r.text
        assert "Sitemap: https://www.sirocoproducciones.es/sitemap.xml" in r.text
        # Ensure there is no global Disallow: / for User-agent: *
        # (Cloudflare preview prepends AI-bot specific Disallow blocks; ignore those)
        # Find the last "User-agent: *" block and verify no Disallow: /
        blocks = re.split(r"(?m)^User-agent:\s*\*\s*$", r.text)
        star_block = blocks[-1] if len(blocks) > 1 else r.text
        assert "Disallow: /" not in star_block, f"Global Disallow: / detected in User-agent:* block:\n{star_block}"

    def test_sitemap(self):
        r = requests.get(BASE_URL + "/sitemap.xml", timeout=30)
        assert r.status_code == 200
        ct = r.headers.get("content-type", "").lower()
        assert "xml" in ct
        locs = re.findall(r"<loc>([^<]+)</loc>", r.text)
        assert locs == [CANONICAL], f"got {locs}"
        assert "<lastmod>2026-08-15</lastmod>" in r.text
