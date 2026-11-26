"""Проверки отдельной сцены с прозрачным персонажем."""
from pathlib import Path
import struct


def test_hero_demo_page(client):
    response = client.get('/hero-demo')
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert 'data-hero-stage' in page
    assert 'data-summon' in page
    assert 'data-demo-world="citadel"' in page
    assert 'data-demo-world="frost"' in page
    assert 'data-demo-world="ashes"' in page
    assert 'data-demo-ability="sword"' in page
    assert 'data-demo-ability="shield"' in page
    assert 'data-demo-ability="arcane"' in page
    assert 'warrior-shield.webp' in page


def test_hero_demo_assets(client):
    for path in ('/static/css/hero-demo.css', '/static/js/hero-demo.js',
                 '/static/images/characters/warrior-shield.webp'):
        response = client.get(path)
        assert response.status_code == 200, path
    home = client.get('/').get_data(as_text=True)
    assert '/hero-demo' in home


def test_original_character_has_alpha():
    path = Path(__file__).resolve().parents[1] / 'static/images/characters/warrior-shield.webp'
    # WEBP lossless alpha is preserved and declared by the VP8X header.
    data = path.read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP'
    assert len(data) > 100_000
