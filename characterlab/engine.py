"""Шестнадцать стратегий генерации персонажей для учебного Mythoria.

Это авторские облегчённые модели, а не валидатор официальных листов персонажа.
"""
import random
from .catalog import BY_SLUG, ROLE_PRIMARY, ROLE_SKILLS
from .portraits import portrait_for

NAMES = ('Астра','Лиан','Элвин','Кира','Рен','Мира','Торн','Нора','Дариан','Айрис','Макс','Эрика')
TRAITS = ('любознательный','сдержанный','смелый','осторожный','добродушный','упорный')
GOALS = ('найти утраченное знание','защитить близких','раскрыть старую тайну','заслужить доверие','исследовать неизведанное')

class InvalidGeneration(ValueError):
    pass

def _roll(rng, dice, sides):
    return sum(rng.randint(1, sides) for _ in range(dice))

def _priority(stats, role):
    return [s for s in stats if s in ROLE_PRIMARY.get(role, ())]

def _dnd(game, role, rng):
    # 4d6, отбросить младший куб; высокие результаты первым ключевым статам.
    values = [sum(sorted([rng.randint(1,6) for _ in range(4)])[1:]) for _ in game.stats]
    values.sort(reverse=True)
    priority = _priority(game.stats,role)
    order = priority + [s for s in game.stats if s not in priority]
    return dict(zip(order, values))

def _pathfinder(game, role, rng):
    # Упрощённый тематический набор boosts, не официальный расчёт PF2e.
    output={s:10 for s in game.stats}
    p=_priority(game.stats,role)
    boosts = (p[:2] + [s for s in game.stats if s not in p][:2])
    for s in boosts: output[s] += 2
    return output

def _cthulhu(game, role, rng):
    out={s:_roll(rng,3,6)*5 for s in game.stats}
    for s in ('РАЗ','ОБР'): out[s]=(_roll(rng,2,6)+6)*5
    return out

def _cyberpunk(game, role, rng):
    out={s:rng.randint(2,6) for s in game.stats}
    for s in _priority(game.stats,role): out[s]=rng.randint(6,8)
    return out

def _vampire(game, role, rng):
    dots=[4,3,3,3,2,2,2,2,1]
    rng.shuffle(dots)
    p=_priority(game.stats,role)
    out=dict(zip(game.stats,dots))
    for s in p:
        if out[s]<3:
            target = max(out, key=out.get)
            out[s],out[target]=out[target],out[s]
    return out

def _warhammer(game, role, rng):
    # Approximate profession-oriented d100 values: not official career advancement.
    return {name:min(75, rng.randint(23,45)+(rng.randint(8,18) if name in _priority(game.stats,role) else 0)) for name in game.stats}

def _starfinder(game, role, rng):
    numbers=[16,14,13,12,10,8]
    rng.shuffle(numbers)
    output=dict(zip(game.stats,numbers))
    for s in _priority(game.stats,role): output[s]=min(20,output[s]+2)
    return output

def _shadowrun(game, role, rng):
    output={s:rng.randint(2,5) for s in game.stats}
    for s in _priority(game.stats,role): output[s]=rng.randint(5,7)
    return output


def _darkest(game, role, rng):
    values={'Здоровье':rng.randint(20,43), 'Уклонение':rng.randint(0,22),
            'Скорость':rng.randint(2,9), 'Точность':rng.randint(64,85),
            'Критический шанс':rng.randint(2,14), 'Стрессоустойчивость':rng.randint(18,54)}
    for stat in _priority(game.stats, role):
        values[stat]=min(100,values[stat]+rng.randint(4,10))
    return values

def _battlebrothers(game, role, rng):
    values={'Здоровье':rng.randint(50,78),'Выносливость':rng.randint(83,112),
            'Решимость':rng.randint(25,49),'Инициатива':rng.randint(80,121),
            'Ближняя атака':rng.randint(42,69),'Дальняя атака':rng.randint(32,67),
            'Защита':rng.randint(2,20)}
    for stat in _priority(game.stats,role):
        values[stat]=min(200,values[stat]+rng.randint(5,13))
    return values

def _disco(game, role, rng):
    # Четыре атрибута и двенадцать очков, как упрощённый учебный билд.
    values=[1,2,4,5]
    rng.shuffle(values)
    priorities=_priority(game.stats,role)
    if priorities:
        target=game.stats.index(priorities[0])
        best=values.index(max(values))
        values[target],values[best]=values[best],values[target]
    return dict(zip(game.stats,values))

def _grimdawn(game, role, rng):
    values={stat:rng.randint(35,65) for stat in game.stats}
    for stat in _priority(game.stats,role): values[stat]+=rng.randint(10,19)
    return values

def _lastepoch(game, role, rng):
    values={stat:rng.randint(8,18) for stat in game.stats}
    focus={'Страж':'Сила','Маг':'Интеллект','Первобытный':'Сродство',
           'Послушник':'Интеллект','Разбойник':'Ловкость'}[role]
    values[focus]+=rng.randint(7,15)
    return values

def _diablo2(game, role, rng):
    values={'Сила':rng.randint(20,40),'Ловкость':rng.randint(20,35),
            'Живучесть':rng.randint(20,40),'Энергия':rng.randint(20,35)}
    focus={'Амазонка':'Ловкость','Варвар':'Сила','Некромант':'Энергия',
           'Паладин':'Живучесть','Чародейка':'Энергия','Друид':'Энергия','Ассасин':'Ловкость'}[role]
    values[focus]+=rng.randint(12,26)
    return values

def _poe(game, role, rng):
    values={'Сила':rng.randint(14,27),'Ловкость':rng.randint(14,27),'Интеллект':rng.randint(14,27)}
    for stat in _priority(game.stats,role): values[stat]+=rng.randint(10,22)
    return values

def _titanquest(game, role, rng):
    values={'Сила':rng.randint(40,60),'Ловкость':rng.randint(40,60),
            'Интеллект':rng.randint(40,60),'Здоровье':rng.randint(100,140),
            'Энергия':rng.randint(60,90)}
    for stat in _priority(game.stats,role): values[stat]+=rng.randint(12,25)
    return values

STRATEGIES = {'dnd':_dnd,'pathfinder':_pathfinder,'cthulhu':_cthulhu,'cyberpunk':_cyberpunk,'vampire':_vampire,'warhammer':_warhammer,'starfinder':_starfinder,'shadowrun':_shadowrun,'darkest':_darkest,'battlebrothers':_battlebrothers,'disco':_disco,'grimdawn':_grimdawn,'lastepoch':_lastepoch,'diablo2':_diablo2,'poe':_poe,'titanquest':_titanquest}

def generate(slug, origin=None, role=None, *, seed=None, level=1):
    game=BY_SLUG.get(slug)
    if game is None: raise InvalidGeneration('Неизвестная игровая система')
    if origin and origin not in game.origins: raise InvalidGeneration('Недопустимое происхождение')
    if role and role not in game.roles: raise InvalidGeneration('Недопустимый класс или роль')
    try: level=int(level)
    except (ValueError,TypeError): raise InvalidGeneration('Неверное значение уровня') from None
    if level<1 or level>game.max_level: raise InvalidGeneration(f'Уровень: от 1 до {game.max_level}')
    rng=random.Random(seed)
    origin=origin or rng.choice(game.origins)
    role=role or rng.choice(game.roles)
    stats=STRATEGIES[slug](game,role,rng)
    character_name = f'{rng.choice(NAMES)} {rng.choice(("Северный", "Тихий", "Странник", "Искатель", "Пепельный"))}'
    bio=f'{character_name} — {rng.choice(TRAITS)} персонаж. Его цель — {rng.choice(GOALS)}.'
    visual_seed = rng.getrandbits(31)
    portrait_path = portrait_for(slug, character_name, origin, role, seed=visual_seed)
    return {'game_slug':slug,'name':character_name,'origin':origin,'role':role,'level':level,
            'bio':bio,'stats':stats,'abilities':ROLE_SKILLS.get(role,[]),
            'portrait_path':portrait_path,'visual_seed':visual_seed}
