"""Фабрика Flask-приложения Mythoria."""
import os
import secrets
import json
from pathlib import Path
from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,flash,abort,session,g,Response
from .catalog import GAMES, BY_SLUG
from .engine import generate,InvalidGeneration
from . import db as database

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

    @app.get('/help')
    def help_page(): return render_template('help.html')

    @app.errorhandler(404)
    def notfound(err): return render_template('error.html',title='Страница не найдена',message='Проверьте адрес или перейдите в каталог игр.'),404
    @app.errorhandler(400)
    def badrequest(err): return render_template('error.html',title='Ошибка запроса',message='Проверьте введённые данные и попробуйте снова.'),400

    return app
