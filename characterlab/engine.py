"""Шестнадцать автономных стратегий генерации персонажей для учебного Mythoria.

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

def _bg3(game, role, rng):
    # Упрощённый набор очков: не воспроизводит UI/стоимость point-buy в BG3.
    numbers = [15,14,13,12,10,8]
    priority = _priority(game.stats,role)
    order = priority + [s for s in game.stats if s not in priority]
    output = dict(zip(order,numbers))
    output[order[0]] += 2
    output[order[1]] += 1
    return output

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

def _divinity(game, role, rng):
    out={s:10 for s in game.stats}
    p=_priority(game.stats,role)
    out[p[0] if p else 'Интеллект'] += 3
    out['Память'] += rng.randint(0,2)
    return out

def _skyrim(game, role, rng):
    out={'Здоровье':100,'Магия':100,'Запас сил':100}
    if role in ('Воин','Лучник','Вор'): out['Запас сил']+=20
    elif role in ('Маг','Боевой маг'): out['Магия']+=20
    return out

ELDEN_BASE={
 'Бродяга':(15,10,11,14,13,9,9,7),
 'Воин':(11,12,11,10,16,10,8,9),
 'Герой':(14,9,12,16,9,7,8,11),
 'Астролог':(9,15,9,8,12,16,7,9),
 'Самурай':(12,11,13,12,15,9,8,8),
}
def _elden(game, role, rng):
    return dict(zip(game.stats, ELDEN_BASE[role]))

def _fallout(game, role, rng):
    # 7 базовых очков + 21 на распределение; диапазон 1..10.
    out={s:1 for s in game.stats}
    preferred=_priority(game.stats,role)
    pool=21
    while pool:
        valid=[s for s in game.stats if out[s]<10]
        weighted=preferred*3+valid
        s=rng.choice([v for v in weighted if v in valid])
        out[s]+=1;pool-=1
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

def _dragonage(game, role, rng):
    out={s:rng.randint(10,16) for s in game.stats}
    for s in _priority(game.stats,role): out[s]+=4
    return out

def _wow(game, role, rng):
    out={s:rng.randint(10,20) for s in game.stats}
    primary={'Воин':'Сила','Маг':'Интеллект','Охотник':'Ловкость','Жрец':'Интеллект','Паладин':'Сила'}.get(role,'Сила')
    out[primary]+=10
    return out

def _diablo(game, role, rng):
    out={s:rng.randint(6,12) for s in game.stats}
    primary={'Варвар':'Сила','Чародей':'Интеллект','Некромант':'Интеллект','Разбойник':'Ловкость','Друид':'Воля'}.get(role,'Воля')
    out[primary]+=6
    return out

STRATEGIES = {'dnd':_dnd,'pathfinder':_pathfinder,'cthulhu':_cthulhu,'cyberpunk':_cyberpunk,'vampire':_vampire,'bg3':_bg3,'divinity':_divinity,'skyrim':_skyrim,'elden':_elden,'fallout':_fallout,'warhammer':_warhammer,'starfinder':_starfinder,'shadowrun':_shadowrun,'dragonage':_dragonage,'wow':_wow,'diablo':_diablo}

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
