"""Фабрика Flask-приложения Mythoria."""
import os
import secrets
import json
import mimetypes
from pathlib import Path
from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,flash,abort,session,g,Response
from .catalog import GAMES, BY_SLUG
from .engine import generate,InvalidGeneration
from . import db as database

mimetypes.add_type('image/webp', '.webp')

ROOT=Path(__file__).resolve().parents[1]

def create_app(test_config=None):
    app=Flask(__name__,template_folder=str(ROOT/'templates'),static_folder=str(ROOT/'static'))
    app.config.update(SECRET_KEY=os.environ.get('MYTHORIA_SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=os.environ.get('MYTHORIA_DB') or str(Path.home()/'.mythoria'/'mythoria.sqlite3'),
                      MAX_CONTENT_LENGTH=128*1024)
    if test_config: app.config.update(test_config)
    database.init_db(app.config['DATABASE'])
    app.teardown_appcontext(database.close_db)

    @app.before_request
    def csrf_check():
        if 'csrf' not in session: session['csrf']=secrets.token_urlsafe(24)
        if request.method in ('POST','PUT','PATCH','DELETE'):
            if not secrets.compare_digest(request.form.get('csrf',''),session['csrf']): abort(400,'Неверный защитный токен формы')

    @app.context_processor
    def common(): return {'csrf_token':session.get('csrf',''),'games':GAMES}

    @app.get('/')
    def index():
        count=database.get_db().execute('SELECT COUNT(*) AS n FROM characters').fetchone()['n']
        return render_template('index.html',count=count)

    @app.get('/games')
    def games_page(): return render_template('games.html')

    @app.route('/generate/<slug>',methods=['GET','POST'])
    def generator(slug):
        game=BY_SLUG.get(slug)
        if not game: abort(404)
        result=None
        if request.method=='POST':
            try:
                result=generate(slug,request.form.get('origin') or None,request.form.get('role') or None,level=request.form.get('level') or 1)
                session['preview']=result
            except InvalidGeneration as exc: flash(str(exc),'error')
        else: session.pop('preview',None)
        return render_template('generator.html',game=game,result=result)

    @app.post('/characters/save')
    def save():
        p=session.pop('preview',None)
        if not p: flash('Сначала сгенерируйте персонажа','error');return redirect(url_for('games_page'))
        try: cid=database.save_character(database.get_db(),p)
        except (ValueError,KeyError,TypeError) as exc:
            flash(f'Не удалось сохранить: {exc}','error');return redirect(url_for('games_page'))
        flash('Персонаж сохранён','success')
        return redirect(url_for('detail',cid=cid))

    @app.get('/characters')
    def characters():
        filters={'q':request.args.get('q','').strip()[:80], 'game_slug':request.args.get('game',''),
                 'favorite':request.args.get('favorite')=='1','order':request.args.get('order','new')}
        if filters['game_slug'] not in BY_SLUG: filters['game_slug']=''
        rows=database.list_characters(database.get_db(),**filters)
        return render_template('characters.html',rows=rows,filters=filters)

    def fetch_or_404(cid):
        res=database.find_character(database.get_db(),cid)
        if not res: abort(404)
        return res

    @app.get('/characters/<int:cid>')
    def detail(cid):
        item,stats,skills=fetch_or_404(cid)
        return render_template('detail.html',item=item,stats=stats,skills=skills)

    @app.route('/characters/<int:cid>/edit',methods=['GET','POST'])
    def edit(cid):
        item,stats,skills=fetch_or_404(cid)
        if request.method=='POST':
            name=request.form.get('name','').strip()
            bio=request.form.get('bio','').strip()
            if not 1<=len(name)<=80 or len(bio)>1000:
                flash('Имя: 1–80 символов, биография: до 1000','error')
                return render_template('edit.html',item=item,stats=stats),400
            try:
                changes=[]
                for s in stats:
                    value=int(request.form[f'stat_{s["id"]}'])
                    if not s['min_value']<=value<=s['max_value']: raise ValueError('Выход за диапазон')
                    changes.append((value,cid,s['id']))
                connection=database.get_db()
                with connection:
                    connection.execute('UPDATE characters SET name=?,bio=? WHERE id=?',(name,bio,cid))
                    connection.executemany('UPDATE character_stats SET value=? WHERE character_id=? AND attribute_id=?',changes)
            except (ValueError,KeyError):
                flash('Проверьте характеристики','error')
                return render_template('edit.html',item=item,stats=stats),400
            flash('Изменения сохранены','success')
            return redirect(url_for('detail',cid=cid))
        return render_template('edit.html',item=item,stats=stats)

    @app.post('/characters/<int:cid>/favorite')
    def favorite(cid):
        fetch_or_404(cid)
        connection=database.get_db()
        with connection: connection.execute('UPDATE characters SET favorite=1-favorite WHERE id=?',(cid,))
        return redirect(url_for('detail',cid=cid))

    @app.post('/characters/<int:cid>/delete')
    def delete(cid):
        fetch_or_404(cid)
        connection=database.get_db()
        with connection: connection.execute('DELETE FROM characters WHERE id=?',(cid,))
        flash('Персонаж удалён','success')
        return redirect(url_for('characters'))

    @app.get('/characters/<int:cid>/export')
    def export(cid):
        item,stats,skills=fetch_or_404(cid)
        fields={'id':item['id'],'game':item['game_title'],'name':item['name'],'origin':item['origin'],
                'role':item['role'],'level':item['level'],'bio':item['bio'],'stats':{s['label']:s['value'] for s in stats},'abilities':[x['label'] for x in skills]}
        return Response(json.dumps(fields,ensure_ascii=False,indent=2),mimetype='application/json',headers={'Content-Disposition':f'attachment; filename="character-{cid}.json"'})

    @app.get('/statistics')
    def statistics():
        conn=database.get_db()
        summary=conn.execute('SELECT COUNT(*) AS total, COALESCE(SUM(favorite),0) AS favorites,ROUND(AVG(level),1) AS avg_level FROM characters').fetchone()
        groups=conn.execute('SELECT g.title,COUNT(c.id) AS total FROM games g LEFT JOIN characters c ON c.game_id=g.id GROUP BY g.id ORDER BY total DESC,g.title').fetchall()
        return render_template('statistics.html',summary=summary,groups=groups)


    @app.get('/art/<slug>.svg')
    def world_art(slug):
        """Собственные декоративные иллюстрации для каталога, без чужих игровых артов."""
        if slug not in BY_SLUG:
            abort(404)
        colors = [
            ('#221035','#5d316d','#ea80c8'),('#102d52','#765d9c','#9bdcff'),
            ('#182638','#497d86','#b9c7b6'),('#180b30','#8a3e89','#36dcff'),
            ('#210c23','#962d4e','#fba99d'),('#170f43','#8d3b9c','#ffc09c'),
            ('#30123b','#bb5d7b','#f7b8a9'),('#14314a','#4b84a0','#d0a1d9'),
            ('#241b32','#7b556c','#e4ae86'),('#172c3a','#8a634d','#f9b25a'),
            ('#2b1826','#776074','#eabea8'),('#111d4a','#4f5bad','#b5c3fa'),
            ('#180b35','#5b2d8c','#ff85dc'),('#1d2b4c','#8a5688','#f9b9a4'),
            ('#1c2448','#5e4f9b','#c7a5d8'),('#230e31','#913b63','#f9a36a')
        ]
        a, b, c = colors[list(BY_SLUG).index(slug) % len(colors)]
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
        <defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="{a}"/>
        <stop offset=".63" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient>
        <radialGradient id="light"><stop stop-color="#ffe3fb" stop-opacity=".8"/>
        <stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient></defs>
        <rect width="800" height="600" fill="url(#sky)"/>
        <circle cx="570" cy="155" r="220" fill="url(#light)"/>
        <circle cx="568" cy="155" r="62" fill="#f9d9f0" opacity=".66"/>
        <path d="M0 380L142 266 234 354 332 188 462 348 605 228 800 372V600H0Z" fill="{a}" opacity=".68"/>
        <path d="M0 451L124 327 246 434 398 286 530 418 650 329 800 420V600H0Z" fill="{b}" opacity=".69"/>
        <path d="M0 505L165 408 251 467 383 353 535 471 716 406 800 440V600H0Z" fill="{a}" opacity=".85"/>
        <path d="M0 560Q170 500 380 554T800 536V600H0Z" fill="#111023" opacity=".83"/>
        <g stroke="#ffddfb" stroke-opacity=".58" fill="none">
          <circle cx="402" cy="258" r="150" stroke-dasharray="3 14"/>
          <path d="M402 155L421 238 500 258 421 278 402 358 381 278 303 258 381 238Z"/>
        </g></svg>'''
        return Response(svg, mimetype='image/svg+xml',
                        headers={'Cache-Control': 'public, max-age=86400'})

    @app.get('/help')
    def help_page(): return render_template('help.html')

    @app.errorhandler(404)
    def notfound(err): return render_template('error.html',title='Страница не найдена',message='Проверьте адрес или перейдите в каталог игр.'),404
    @app.errorhandler(400)
    def badrequest(err): return render_template('error.html',title='Ошибка запроса',message='Проверьте введённые данные и попробуйте снова.'),400

    return app
