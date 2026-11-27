"""Изображения, устойчивость внешности и совместимость со старой БД."""
from pathlib import Path
import sqlite3
import pytest

from characterlab import db as database
from characterlab.catalog import GAMES
from characterlab.engine import generate
from characterlab.portraits import ART, GAME_ART, portrait_choices, portrait_for, is_valid_portrait
from tests.conftest import csrf


def test_all_games_have_their_own_gallery():
    assets = database.ROOT / 'static'
    assert len(GAME_ART) == len(GAMES) == 16
    assert len(ART) >= 24
    for game in GAMES:
        choices=portrait_choices(game.slug)
        assert len(choices) >= 4, game.slug
        assert len(choices) == len(set(choices))
        assert all((assets / item).is_file() for item in choices), game.slug
        assert portrait_for(game.slug, role=game.roles[0]) in choices


@pytest.mark.parametrize('game',GAMES,ids=lambda g:g.slug)
def test_generated_portrait_is_allowed_and_repeatable(game):
    hero=generate(game.slug, seed=211)
    assert is_valid_portrait(game.slug,hero['portrait_path'])
    assert 0 <= hero['visual_seed'] <= 2147483647
    assert generate(game.slug,seed=211)['portrait_path'] == hero['portrait_path']
    results={generate(game.slug,seed=i)['portrait_path'] for i in range(50)}
    assert len(results) >= 2


def test_a_chosen_portrait_is_saved_and_not_changed_by_renaming(client,app):
    client.get('/generate/dnd')
    token=csrf(client)
    response=client.post('/generate/dnd',data={'csrf':token,'origin':'Эльф','role':'Воин','level':'3'})
    assert response.status_code==200
    assert 'v5-portrait-picker' in response.get_data(as_text=True)
    with client.session_transaction() as s:
        preview=s['preview']
    options=portrait_choices('dnd',preview['role'],preview['origin'])
    selected=next(item for item in options if item != preview['portrait_path'])
    res=client.post('/characters/save',data={'csrf':token,'portrait_path':selected},follow_redirects=True)
    assert res.status_code==200
    with app.app_context():
        record=database.get_db().execute('SELECT * FROM characters ORDER BY id DESC').fetchone()
        cid=record['id']
        seed=record['visual_seed']
        assert record['portrait_path']==selected
    assert selected in client.get(f'/characters/{cid}').get_data(as_text=True)
    stats=database_get_stats(app,cid)
    edit=client.post(f'/characters/{cid}/edit',data={'csrf':token,'name':'Новое имя','bio':'История',
                       'portrait_path':selected,**{f'stat_{x["id"]}':x['value'] for x in stats}})
    assert edit.status_code==302
    with app.app_context():
        record=database.get_db().execute('SELECT * FROM characters WHERE id=?',(cid,)).fetchone()
        assert record['name']=='Новое имя'
        assert record['portrait_path']==selected
        assert record['visual_seed']==seed
    assert client.get(f'/characters/{cid}/export').json['portrait']==selected


def database_get_stats(app,cid):
    with app.app_context():
        return [dict(x) for x in database.find_character(database.get_db(),cid)[1]]


def test_external_portrait_is_rejected(client):
    client.get('/generate/dnd')
    token=csrf(client)
    assert client.post('/generate/dnd',data={'csrf':token,'level':'1'}).status_code==200
    response=client.post('/characters/save',data={'csrf':token,'portrait_path':'../../private.txt'})
    assert response.status_code==400


def test_old_database_migrates_without_deleting_people(tmp_path):
    db_path=tmp_path/'old.sqlite3'
    sql=(database.ROOT/'database'/'schema.sql').read_text(encoding='utf-8')
    sql=sql.replace(" portrait_path TEXT NOT NULL DEFAULT '',\n",'')
    sql=sql.replace(" visual_seed INTEGER NOT NULL DEFAULT 0 CHECK(visual_seed BETWEEN 0 AND 2147483647),\n",'')
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
        conn.execute("INSERT INTO games(slug,title,game_group,edition,description) VALUES('dnd','Старый мир','tabletop','test','test')")
    database.init_db(db_path)
    with database.connect(db_path) as conn:
        columns={row['name'] for row in conn.execute('PRAGMA table_info(characters)')}
        assert {'portrait_path','visual_seed'} <= columns
        assert conn.execute("SELECT title FROM games WHERE slug='dnd'").fetchone()['title']=='Старый мир'
    database.init_db(db_path)
    with database.connect(db_path) as conn:
        assert conn.execute('SELECT COUNT(*) FROM games').fetchone()[0]==16


def test_removed_unused_games_are_cleaned_up(tmp_path):
    """Устаревшие игры без сохранённых героев исчезают после инициализации."""
    path=tmp_path/'retired.sqlite3'
    database.init_db(path)
    with database.connect(path) as conn:
        conn.execute("INSERT INTO games(slug,title,game_group,edition,description) VALUES(?,?,?,?,?)",
                     ('fallout','Старая игра','video','архив','не используется'))
    database.init_db(path)
    with database.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]==16
        assert conn.execute("SELECT COUNT(*) FROM games WHERE slug='fallout'").fetchone()[0]==0
