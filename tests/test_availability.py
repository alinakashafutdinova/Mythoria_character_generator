"""Проверка статусов игровых миров и безопасной блокировки будущих систем."""
from characterlab.catalog import (
    GAMES, AVAILABLE_GAME_SLUGS, available_games, coming_soon_games, game_is_available
)
from characterlab.engine import generate
from characterlab import db as database
from tests.conftest import csrf


def test_four_ready_and_twelve_coming_soon():
    assert len(GAMES) == 16
    assert AVAILABLE_GAME_SLUGS == {'dnd', 'pathfinder', 'darkest', 'diablo2'}
    assert len(available_games()) == 4
    assert len(coming_soon_games()) == 12
    assert set(x.slug for x in available_games()).isdisjoint(x.slug for x in coming_soon_games())
    assert all(not game_is_available(x.slug) for x in coming_soon_games())


def test_catalog_shows_real_statuses_and_lock(client):
    html = client.get('/games').get_data(as_text=True)
    assert html.count('data-availability="available"') == 4
    assert html.count('data-availability="soon"') == 12
    assert 'data-filter="available"' in html
    assert 'data-filter="soon"' in html
    assert 'mythoria-lock.svg' in html
    assert 'МИР ПОКА ЗАКРЫТ' not in html  # текст на карточке не обязан быть заглавным
    home = client.get('/').get_data(as_text=True)
    assert home.count('class="my-world-card is-locked"') == 12
    assert 'data-ready-games="dnd,pathfinder,darkest,diablo2"' in home


def test_coming_soon_page_is_teaser_not_generator(client):
    for slug in ('cthulhu', 'cyberpunk', 'battlebrothers', 'poe'):
        html = client.get('/generate/' + slug)
        assert html.status_code == 200
        page = html.get_data(as_text=True)
        assert 'МИР ОТКРОЕТСЯ ПОЗЖЕ' in page
        assert 'Сгенерировать' not in page
        assert 'Вернуться к играм' in page


def test_soon_world_rejects_post_without_creating_preview(client):
    client.get('/games')
    token = csrf(client)
    forbidden = client.post('/generate/cthulhu', data={'csrf': token, 'level':'1'})
    assert forbidden.status_code == 403
    with client.session_transaction() as session:
        assert 'preview' not in session


def test_coming_soon_does_not_allow_saving_stale_preview(client, app):
    client.get('/games')
    token = csrf(client)
    with client.session_transaction() as session:
        session['preview'] = generate('cthulhu', seed=101)
    result = client.post('/characters/save', data={'csrf':token})
    assert result.status_code == 302
    with app.app_context():
        assert database.get_db().execute('SELECT COUNT(*) FROM characters').fetchone()[0] == 0


def test_available_games_still_generate_and_save(client, app):
    for slug in ('dnd','pathfinder','darkest','diablo2'):
        client.get('/generate/'+slug)
        token=csrf(client)
        result=client.post('/generate/'+slug,data={'csrf':token,'level':'1'})
        assert result.status_code==200
        assert 'Сгенерировать' in result.get_data(as_text=True)
        saved=client.post('/characters/save',data={'csrf':token})
        assert saved.status_code==302
    with app.app_context():
        assert database.get_db().execute('SELECT COUNT(*) FROM characters').fetchone()[0]==4


def test_coming_soon_style_assets_are_available(client):
    assert client.get('/static/css/availability.css').status_code == 200
    icon = client.get('/static/images/mythoria-lock.svg')
    assert icon.status_code == 200
    assert b'<svg' in icon.data
