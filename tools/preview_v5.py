"""Локальный HTML-предпросмотр Mythoria без Flask (только для проверки дизайна)."""
import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT=Path(__file__).resolve().parents[1]
# Не загружаем characterlab/__init__.py: Flask здесь необязателен.
pkg=ModuleType('characterlab');pkg.__path__=[str(ROOT/'characterlab')]
sys.modules['characterlab']=pkg
catalog=importlib.import_module('characterlab.catalog')
portraits=importlib.import_module('characterlab.portraits')
engine=importlib.import_module('characterlab.engine')

def url_for(endpoint,**kw):
    if endpoint=='static':return 'static/'+kw['filename']
    if endpoint=='generator': return 'preview-v5-generator.html'
    if endpoint=='characters': return 'preview-v5-collection.html'
    return 'preview-v5-home.html'

env=Environment(loader=FileSystemLoader(str(ROOT/'templates')),autoescape=select_autoescape(['html']))
env.globals.update(url_for=url_for,portrait_for=portraits.portrait_for,
    portrait_choices=portraits.portrait_choices,portrait_style=portraits.portrait_style,
    get_flashed_messages=lambda **kwargs:[])
hero=engine.generate('bg3',seed=791,role='Воин',origin='Эльф',level=3)
class Result(dict):
    __getattr__=dict.get
sample=Result(hero)
common={'games':catalog.GAMES,'csrf_token':'DEMO','count':6}
items=[]
for idx,slug in enumerate(('bg3','cyberpunk','dnd','cthulhu')):
    result=engine.generate(slug,seed=idx+12)
    item={'id':idx+1,'game_slug':slug,'game_title':catalog.BY_SLUG[slug].title,
          'favorite': idx==1,'created_at':'2026-11-26 10:00:00',**result}
    items.append(Result(item))
for filename,target,vars,endpoint in [
    ('index.html','preview-v5-home.html',{},'index'),
    ('generator.html','preview-v5-generator.html',{'game':catalog.BY_SLUG['bg3'],'result':sample,
      'stat_max':{s:20 for s in catalog.BY_SLUG['bg3'].stats}},'generator'),
    ('characters.html','preview-v5-collection.html',{'rows':items,'filters':SimpleNamespace(q='',game_slug='',favorite=False,order='new')},'characters')]:
    context={**common,**vars,'request':SimpleNamespace(endpoint=endpoint,form={})}
    output=env.get_template(filename).render(**context)
    (ROOT/target).write_text(output,encoding='utf-8')
    print(target,len(output))
