from characterlab import db as database
from tests.conftest import csrf


def test_site_pages(client):
    for path in ['/', '/games', '/characters','/statistics','/help','/generate/dnd','/generate/bg3']:
        assert client.get(path).status_code==200
    assert client.get('/generate/absent').status_code==404


def test_generation_crud_and_export(client,app):
    client.get('/generate/dnd')
    token=csrf(client)
    response=client.post('/generate/dnd',data={'csrf':token,'role':'Воин','origin':'Эльф','level':'1'})
    assert response.status_code==200
    assert 'Сгенерировать'.encode('utf-8') in response.data
    res=client.post('/characters/save',data={'csrf':token},follow_redirects=True)
    assert res.status_code==200
    with app.app_context():
        row=database.get_db().execute('SELECT * FROM characters').fetchone()
        cid=row['id']
        assert database.get_db().execute('SELECT count(*) AS n FROM character_stats WHERE character_id=?',(cid,)).fetchone()['n']==6
        assert database.get_db().execute('SELECT count(*) AS n FROM character_abilities WHERE character_id=?',(cid,)).fetchone()['n']==2
    res=client.get(f'/characters/{cid}/export')
    assert res.json['role']=='Воин'
    res=client.post(f'/characters/{cid}/favorite',data={'csrf':token})
    assert res.status_code==302
    res=client.post(f'/characters/{cid}/edit',data={'csrf':token,'name':'Новый герой','bio':'Новая история',**{f'stat_{s["id"]}':s['value'] for s in database_get_stats(app,cid)}})
    assert res.status_code==302
    assert b'\xd0\x9d\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb9' in client.get('/characters?q=Новый').data
    res=client.post(f'/characters/{cid}/delete',data={'csrf':token})
    assert res.status_code==302
    assert client.get(f'/characters/{cid}').status_code==404


def database_get_stats(app,cid):
    with app.app_context():
        res=database.find_character(database.get_db(),cid)
        return [dict(s) for s in res[1]]


def test_csrf(client):
    client.get('/games')
    assert client.post('/characters/save',data={}).status_code==400


def test_queries(app):
    with app.app_context():
        db=database.get_db()
        assert db.execute('SELECT count(*) FROM games').fetchone()[0]==16
        sql=(database.ROOT/'database'/'queries.sql').read_text(encoding='utf-8')
        for chunk in sql.split(';'):
            if chunk.strip(): db.execute(chunk).fetchall()


def test_new_design_is_available(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'СОЗДАВАЙТЕ' in response.get_data(as_text=True)
    assert 'portrait-kaydren.webp' in response.get_data(as_text=True)
    for url, mime in [
        ('/static/css/design.css', 'text/css'),
        ('/static/js/app.js', 'javascript'),
        ('/static/images/hero-cover.webp', 'image/webp'),
        ('/static/images/promo-cover.webp', 'image/webp'),
        ('/static/images/mythoria-mark.svg', 'image/svg+xml'),
    ]:
        asset = client.get(url)
        assert asset.status_code == 200, url
        assert mime in asset.content_type


def test_art_for_game_is_available(client):
    art = client.get('/art/dnd.svg')
    assert art.status_code == 200
    assert 'svg' in art.content_type
    assert client.get('/art/not-a-game.svg').status_code == 404
