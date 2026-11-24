"""Генератор презентации Mythoria (PPTX)."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'presentation'/'Презентация.pptx'
prs=Presentation(); prs.slide_width=Inches(13.33);prs.slide_height=Inches(7.5)
BG=(15,16,28);PANEL=(31,30,48);ACC=(188,156,249);WHITE=(250,245,255);MUTED=(181,178,204)

def col(x):return RGBColor(*x)
def rect(sl,x,y,w,h,fill=PANEL,line=None,radius=True):
    sp=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sp.fill.solid();sp.fill.fore_color.rgb=col(fill)
    sp.line.fill.background() if line is None else None
    if line is not None:sp.line.color.rgb=col(line)
    return sp

def text(sl,x,y,w,h,string,size=21,color=WHITE,bold=False,align=None):
    box=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame;tf.word_wrap=True
    for i,line in enumerate(string.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.space_after=Pt(9)
        p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=col(color)
        if align:p.alignment=align
    return box

def slide(title,kicker='MYTHORIA / КУРСОВОЙ ПРОЕКТ'):
    sl=prs.slides.add_slide(prs.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=col(BG)
    rect(sl,.0,.0,.11,7.5,ACC,radius=False)
    text(sl,.65,.4,12,.3,kicker,11,ACC,True)
    text(sl,.65,.95,12,1.0,title,32,WHITE,True)
    text(sl,.65,7.1,10,.25,'Тема № 13 «Генератор персонажей»  ·  Индивидуальная работа',10,MUTED)
    text(sl,12.2,7.09,.6,.25,str(len(prs.slides)).zfill(2),10,ACC,True,PP_ALIGN.RIGHT)
    return sl

def card(sl,x,y,w,h,title,body,sz=17):
    rect(sl,x,y,w,h)
    text(sl,x+.24,y+.19,w-.48,.45,title,sz,ACC,True)
    text(sl,x+.24,y+.78,w-.48,h-1.0,body,15,MUTED)

def bullet_slide(title,bullets,kicker=None):
    sl=slide(title,kicker or 'MYTHORIA / АРХИТЕКТУРА')
    for i,b in enumerate(bullets):
        rect(sl,.75,2.05+i*.88,11.8,.65,fill=PANEL)
        text(sl,1.04,2.17+i*.88,11.1,.48,'✦   '+b,17,WHITE)
    return sl

sl=slide('Mythoria', 'УНИВЕРСИТЕТСКИЙ КУРСОВОЙ ПРОЕКТ · 2026')
text(sl,.7,2.25,8,1.3,'Браузерный генератор\nигровых персонажей',30,WHITE,True)
text(sl,.73,4.43,8,.9,'Python · Flask · SQLite · HTML / CSS / JavaScript',17,ACC)
rect(sl,9.2,2,3.2,3.6,(39,30,65))
text(sl,9.7,2.55,2.2,1.5,'✦',104,ACC,True,PP_ALIGN.CENTER)
text(sl,9.55,5.01,2.5,.4,'10 игровых систем',16,WHITE,True,PP_ALIGN.CENTER)

sl=slide('Актуальность проекта')
card(sl,.75,2,3.75,3.7,'Проблема','Создание персонажей вручную занимает время и требует учёта правил.',18)
card(sl,4.82,2,3.75,3.7,'Решение','Автоматизированная генерация по выбранной игровой модели.',18)
card(sl,8.88,2,3.75,3.7,'Результат','Готовые карточки героев, сохранение и удобная коллекция.',18)

sl=slide('Цель и основные задачи')
text(sl,.8,1.93,11.7,.85,'Цель — разработать локальное веб-приложение для создания и хранения персонажей ролевых игр.',22,WHITE,True)
for i,b in enumerate(['Спроектировать 10 игровых профилей и алгоритмы генерации','Разработать пользовательский интерфейс и CRUD','Спроектировать связанную базу SQLite','Создать диаграммы, SQL-запросы, тесты и инструкции']):
    rect(sl,.8,3.0+i*.69,11.7,.55)
    text(sl,1.05,3.09+i*.69,11.2,.38,f'{i+1:02d}   {b}',16,WHITE)

sl=slide('Десять игровых систем')
card(sl,.74,1.95,5.8,4.35,'5 настольных RPG','Dungeons & Dragons 5e\nPathfinder 2e\nCall of Cthulhu 7e\nCyberpunk RED\nVampire: The Masquerade V5')
card(sl,6.79,1.95,5.8,4.35,'5 компьютерных RPG',"Baldur’s Gate 3\nDivinity: Original Sin 2\nThe Elder Scrolls V: Skyrim\nElden Ring\nFallout 4")
text(sl,.83,6.55,11.5,.28,'Важно: игровые правила адаптированы для учебного генератора, не являются официальными листами.',11,MUTED)

sl=slide('Возможности приложения')
for i,(t,b) in enumerate([('Генерация','Имя, происхождение, роль, игровые характеристики'),('Коллекция','Сохранение, поиск, редактирование и удаление'),('Аналитика','Количество героев, избранное, статистика по играм'),('Дополнительно','Экспорт JSON, печать PDF, справка')]):
    x=.75+(i%2)*6.0;y=2.0+(i//2)*2.0;card(sl,x,y,5.7,1.68,t,b,17)

sl=slide('Технологическая архитектура')
for x,y,t,b in [(1,2.0,'Клиент','HTML5 · CSS3 · JavaScript'),(4.75,2.0,'Сервер','Flask · Python · Jinja2'),(8.5,2.0,'Данные','SQLite · SQL · FK')]:card(sl,x,y,3.5,2.1,t,b,18)
text(sl,4.35,2.72,.4,.6,'→',28,ACC,True)
text(sl,8.08,2.72,.4,.6,'→',28,ACC,True)
rect(sl,1.3,5.05,10.8,.85,(42,32,64))
text(sl,1.67,5.3,10,.42,'Один локальный сайт с запуском на macOS и Windows',19,WHITE,True,PP_ALIGN.CENTER)

sl=slide('Модель предметной области')
sl.shapes.add_picture(str(ROOT/'diagrams'/'er.png'),Inches(3.2),Inches(1.88),height=Inches(4.9))
text(sl,.78,2.2,2.1,2.9,'7 таблиц\n\nСвязи 1:N и M:N\n\nВнешние ключи',19,WHITE,True)
text(sl,10.55,2.25,2.25,3,'В системе хранятся игры, варианты, атрибуты, герои и их умения.',15,MUTED)

sl=slide('Логическая модель SQLite')
sl.shapes.add_picture(str(ROOT/'diagrams'/'logical.png'),Inches(3.7),Inches(1.88),height=Inches(4.95))
text(sl,.83,2.25,2.45,2.5,'PK / FK\nUNIQUE\nCHECK\nТранзакции',20,WHITE,True)
text(sl,10.45,2.3,2.3,2,'Разные наборы параметров — без дублирования игровых систем.',15,MUTED)

sl=slide('Логика генерации персонажа')
sl.shapes.add_picture(str(ROOT/'diagrams'/'generation.png'),Inches(4.7),Inches(1.78),height=Inches(5.13))
text(sl,.82,2.3,3.55,3,'Выбор игры → проверка данных → стратегия генерации → карточка → сохранение в SQLite',19,WHITE,True)

sl=slide('SQL и хранение данных')
for i,(a,b) in enumerate([('01','JOIN: персонажи, игры и роли'),('02','WHERE: фильтрация избранного'),('03','LIKE: поиск и сортировка'),('04','GROUP BY: подсчёт по играм'),('05','M:N: умения персонажей'),('06','AVG: средние характеристики')]):
    x=.78+(i%2)*6.02;y=2.03+(i//2)*1.28
    rect(sl,x,y,5.65,1.03);text(sl,x+.2,y+.25,.53,.45,a,18,ACC,True);text(sl,x+.82,y+.21,4.6,.62,b,15,WHITE)

sl=slide('Проведённые проверки и ограничения')
card(sl,.75,1.95,5.7,3.6,'Подтверждено','Синтаксис Python\n10 генераторов\nSQLite: 7 связанных таблиц\n6 SQL-запросов на демо-БД')
card(sl,6.75,1.95,5.7,3.6,'Ещё проверить на MacBook','Установка Flask и запуск браузера\nПолный pytest\nПользовательский интерфейс\nWindows .exe отдельно в Windows')
text(sl,.84,6.0,11.3,.5,'Результаты тестов не преувеличиваются: полная HTTP-проверка пока не проведена.',13,MUTED)

sl=slide('Результат и следующие шаги')
for i,s in enumerate(['Исходники, SQLite, SQL и схемы подготовлены','Пояснительная записка и инструкции включены','Нужно запустить проект на MacBook и записать видео','При необходимости собрать Windows .exe через GitHub Actions']):
    rect(sl,.85,1.9+i*.98,11.55,.75);text(sl,1.15,2.08+i*.98,11,.43,'✦  '+s,18,WHITE)
text(sl,.9,6.36,11.2,.4,'Mythoria · учебный неофициальный проект',15,ACC,True,PP_ALIGN.CENTER)

OUT.parent.mkdir(parents=True,exist_ok=True)
prs.save(OUT)
print('Saved',OUT,'slides',len(prs.slides))
