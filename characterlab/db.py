"""SQLite: схема, справочники и транзакционная работа с персонажами."""
import sqlite3
from pathlib import Path
from flask import current_app, g
from .catalog import GAMES, BY_SLUG, ROLE_SKILLS

ROOT = Path(__file__).resolve().parents[1]

def connect(path):
    conn=sqlite3.connect(str(path))
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def get_db():
    if 'db' not in g: g.db=connect(current_app.config['DATABASE'])
    return g.db

def close_db(e=None):
    db=g.pop('db',None)
    if db is not None: db.close()

def init_db(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with connect(path) as conn:
        conn.executescript((ROOT/'database'/'schema.sql').read_text(encoding='utf-8'))
        for game in GAMES:
            conn.execute('INSERT OR IGNORE INTO games(slug,title,game_group,edition,description) VALUES(?,?,?,?,?)',
                         (game.slug,game.title,game.group,game.edition,game.description))
            gid=conn.execute('SELECT id FROM games WHERE slug=?',(game.slug,)).fetchone()['id']
            for group,items in [('origin',game.origins),('role',game.roles)]:
                conn.executemany('INSERT OR IGNORE INTO game_options(game_id,option_group,label) VALUES(?,?,?)',[(gid,group,x) for x in items])
            for role in game.roles:
                conn.executemany('INSERT OR IGNORE INTO abilities(game_id,label) VALUES(?,?)',[(gid,a) for a in ROLE_SKILLS.get(role,[])])
            lo,hi=({'cthulhu':(0,99),'cyberpunk':(2,8),'vampire':(1,5),'fallout':(1,10),'skyrim':(100,200),'elden':(1,99),'warhammer':(1,99),'starfinder':(1,30),'shadowrun':(1,10),'dragonage':(1,30),'wow':(1,40),'diablo':(1,30)}.get(game.slug,(1,30)))
            conn.executemany('INSERT OR IGNORE INTO attribute_definitions(game_id,label,min_value,max_value) VALUES(?,?,?,?)',[(gid,x,lo,hi) for x in game.stats])
        conn.commit()

def list_characters(db,game_slug='',q='',favorite=False,order='new'):
    sql='SELECT c.*,g.title AS game_title,g.slug AS game_slug, o.label AS origin, r.label AS role FROM characters c JOIN games g ON g.id=c.game_id JOIN game_options o ON o.id=c.origin_option_id JOIN game_options r ON r.id=c.role_option_id WHERE 1=1'
    params=[]
    if game_slug: sql+=' AND g.slug=?'; params.append(game_slug)
    if q: sql+=' AND c.name LIKE ?';params.append('%'+q+'%')
    if favorite: sql+=' AND c.favorite=1'
    sql+= ' ORDER BY lower(c.name),c.id' if order=='name' else ' ORDER BY c.created_at DESC,c.id DESC'
    return db.execute(sql,params).fetchall()

def find_character(db,cid):
    row=db.execute('''SELECT c.*,g.title AS game_title,g.slug AS game_slug,
                 o.label AS origin,r.label AS role FROM characters c
                 JOIN games g ON g.id=c.game_id
                 JOIN game_options o ON o.id=c.origin_option_id
                 JOIN game_options r ON r.id=c.role_option_id WHERE c.id=?''',(cid,)).fetchone()
    if not row: return None
    attrs=db.execute('''SELECT a.id,a.label,a.min_value,a.max_value,s.value FROM character_stats s
        JOIN attribute_definitions a ON a.id=s.attribute_id WHERE s.character_id=? ORDER BY s.id''',(cid,)).fetchall()
    skills=db.execute('''SELECT a.label FROM character_abilities ca
        JOIN abilities a ON a.id=ca.ability_id WHERE ca.character_id=? ORDER BY a.label''',(cid,)).fetchall()
    return row,attrs,skills

def save_character(db,payload):
    game=BY_SLUG[payload['game_slug']]
    # Verify data at storage boundary as well, never trust client/session payload.
    if payload['origin'] not in game.origins or payload['role'] not in game.roles: raise ValueError('Неверная раса или роль')
    if set(payload['stats'])!=set(game.stats): raise ValueError('Неполный набор характеристик')
    if not 1<=int(payload['level'])<=game.max_level: raise ValueError('Недопустимый уровень')
    name=str(payload['name']).strip()
    if not 1<=len(name)<=80: raise ValueError('Неверное имя')
    bio=str(payload['bio'])
    if len(bio)>1000: raise ValueError('Слишком длинная биография')
    row=db.execute('SELECT id FROM games WHERE slug=?',(game.slug,)).fetchone()
    if not row: raise ValueError('Игра отсутствует в БД')
    gid=row['id']
    origin_id=db.execute('SELECT id FROM game_options WHERE game_id=? AND option_group=? AND label=?',(gid,'origin',payload['origin'])).fetchone()['id']
    role_id=db.execute('SELECT id FROM game_options WHERE game_id=? AND option_group=? AND label=?',(gid,'role',payload['role'])).fetchone()['id']
    with db:
        result=db.execute('INSERT INTO characters(game_id,name,origin_option_id,role_option_id,level,bio) VALUES(?,?,?,?,?,?)',(gid,name,origin_id,role_id,int(payload['level']),bio))
        cid=result.lastrowid
        for ability in ROLE_SKILLS.get(payload['role'],[]):
            a=db.execute('SELECT id FROM abilities WHERE game_id=? AND label=?',(gid,ability)).fetchone()
            if a: db.execute('INSERT INTO character_abilities(character_id,ability_id) VALUES(?,?)',(cid,a['id']))
        for stat,value in payload['stats'].items():
            d=db.execute('SELECT * FROM attribute_definitions WHERE game_id=? AND label=?',(gid,stat)).fetchone()
            if not isinstance(value,int) or not d['min_value']<=value<=d['max_value']: raise ValueError('Неверная характеристика')
            db.execute('INSERT INTO character_stats(character_id,attribute_id,value) VALUES(?,?,?)',(cid,d['id'],value))
    return cid
