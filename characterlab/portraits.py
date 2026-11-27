"""Оригинальные портреты персонажей: тематический выбор и сохраняемый облик.

Здесь используются подготовленные иллюстрации, а не вызовы нейросети или API.
Для одного персонажа хранится выбранная картинка и визуальный код, поэтому
переименование или повторное открытие не меняет его внешность.
"""
from __future__ import annotations

from hashlib import blake2b
from random import Random

# 8 отдельных иллюстраций + 16 персонажей из авторской галереи.
# Метки задают тематическое соответствие роли и происхождению.
ART = {
    'astral-oracle': ('images/portraits/astral-oracle.webp', {'mage', 'elf', 'space'}),
    'rift-guardian': ('images/portraits/rift-guardian.webp', {'fighter', 'magic'}),
    'blood-noble': ('images/portraits/blood-noble.webp', {'vampire', 'mage', 'gothic'}),
    'forest-warden': ('images/portraits/forest-warden.webp', {'ranger', 'elf', 'nature'}),
    'neon-runner': ('images/portraits/neon-runner.webp', {'tech', 'ranger', 'future'}),
    'wasteland-scout': ('images/portraits/wasteland-scout.webp', {'ranger', 'survival'}),
    'arcane-scholar': ('images/portraits/arcane-scholar.webp', {'mage', 'scholar', 'gothic'}),
    'frost-berserker': ('images/portraits/frost-berserker.webp', {'fighter', 'survival'}),
    'hero-00': ('images/avatars/hero-00.webp', {'fighter'}),
    'hero-01': ('images/avatars/hero-01.webp', {'mage', 'elf'}),
    'hero-02': ('images/avatars/hero-02.webp', {'scholar', 'gothic'}),
    'hero-03': ('images/avatars/hero-03.webp', {'tech', 'future'}),
    'hero-04': ('images/avatars/hero-04.webp', {'vampire', 'gothic'}),
    'hero-05': ('images/avatars/hero-05.webp', {'fighter'}),
    'hero-06': ('images/avatars/hero-06.webp', {'space'}),
    'hero-07': ('images/avatars/hero-07.webp', {'tech', 'scholar'}),
    'hero-08': ('images/avatars/hero-08.webp', {'mage'}),
    'hero-09': ('images/avatars/hero-09.webp', {'ranger', 'elf'}),
    'hero-10': ('images/avatars/hero-10.webp', {'fighter', 'survival'}),
    'hero-11': ('images/avatars/hero-11.webp', {'fighter', 'gothic'}),
    'hero-12': ('images/avatars/hero-12.webp', {'survival', 'tech'}),
    'hero-13': ('images/avatars/hero-13.webp', {'mage', 'scholar'}),
    'hero-14': ('images/avatars/hero-14.webp', {'fighter', 'orc'}),
    'hero-15': ('images/avatars/hero-15.webp', {'space', 'tech'}),
}

# В каждой игре есть отдельный тематический пул. Можно добавлять новые рисунки
# без изменений базы данных и без копирования шаблонов страниц.
GAME_ART = {
    'dnd': ('astral-oracle', 'rift-guardian', 'forest-warden', 'hero-00', 'hero-01', 'hero-14'),
    'pathfinder': ('forest-warden', 'astral-oracle', 'rift-guardian', 'hero-01', 'hero-09', 'hero-13'),
    'cthulhu': ('arcane-scholar', 'hero-02', 'hero-04', 'hero-07'),
    'cyberpunk': ('neon-runner', 'hero-03', 'hero-07', 'hero-15'),
    'vampire': ('blood-noble', 'hero-04', 'arcane-scholar', 'hero-11'),
    'warhammer': ('frost-berserker', 'rift-guardian', 'hero-05', 'hero-11', 'hero-14'),
    'starfinder': ('astral-oracle', 'neon-runner', 'hero-06', 'hero-15'),
    'shadowrun': ('neon-runner', 'hero-07', 'hero-03', 'hero-14'),
    'darkest': ('blood-noble', 'arcane-scholar', 'hero-11', 'hero-04', 'hero-05'),
    'battlebrothers': ('frost-berserker', 'rift-guardian', 'hero-05', 'hero-10', 'hero-00'),
    'disco': ('arcane-scholar', 'hero-02', 'hero-07', 'wasteland-scout', 'hero-12'),
    'grimdawn': ('blood-noble', 'rift-guardian', 'hero-11', 'arcane-scholar', 'hero-05'),
    'lastepoch': ('astral-oracle', 'forest-warden', 'frost-berserker', 'hero-01', 'hero-10'),
    'diablo2': ('rift-guardian', 'blood-noble', 'frost-berserker', 'hero-00', 'hero-13'),
    'poe': ('rift-guardian', 'arcane-scholar', 'hero-11', 'hero-09', 'hero-00'),
    'titanquest': ('frost-berserker', 'forest-warden', 'hero-00', 'hero-09', 'hero-13'),
}

# Совместимость со старыми тестами и кодом: пути именно из локальной галереи.
POOLS = {slug: tuple(ART[key][0] for key in keys) for slug, keys in GAME_ART.items()}


def _role_tags(role: str, origin: str) -> set[str]:
    text = (role or '').casefold()
    tags = set()
    for key in ('маг', 'волшеб', 'жрец', 'чарод', 'астролог', 'некромант', 'мистик', 'заклин', 'друид'):
        if key in text:
            tags.add('mage')
    for key in ('воин', 'рыцарь', 'варвар', 'паладин', 'самурай', 'соло', 'солдат', 'бродяг', 'герой', 'бруха'):
        if key in text:
            tags.add('fighter')
    for key in ('плут', 'следопыт', 'разбойник', 'охотник', 'снайпер', 'лучник', 'вор', 'дозор', 'оперативник'):
        if key in text:
            tags.add('ranger')
    for key in ('декер', 'нетраннер', 'техник', 'механик', 'медтех', 'риггер'):
        if key in text:
            tags.add('tech')
    for key in ('учён', 'профессор', 'журналист', 'археолог', 'врач', 'алхимик', 'детектив'):
        if key in text:
            tags.add('scholar')
    if 'эльф' in (origin or '').casefold():
        tags.add('elf')
    if 'орк' in (origin or '').casefold():
        tags.add('orc')
    return tags


def portrait_choices(slug: str, role: str = '', origin: str = '') -> tuple[str, ...]:
    """Картинки, разрешённые для выбранной игры, приоритетно по роли героя."""
    names = GAME_ART.get(slug)
    if not names:
        return ()
    wanted = _role_tags(role, origin)
    scored = [(-len(ART[key][1] & wanted), index, ART[key][0]) for index, key in enumerate(names)]
    scored.sort()
    return tuple(path for _, _, path in scored)


def is_valid_portrait(slug: str, path: str) -> bool:
    return path in POOLS.get(slug, ())


def portrait_for(slug: str, name: str = '', origin: str = '', role: str = '',
                 *, seed: int | None = None, selected: str = '') -> str:
    """Вернуть допустимое изображение; конкретный выбор лучше сохранять в БД."""
    if selected and (is_valid_portrait(slug, selected) or (slug not in GAME_ART and selected in {art[0] for art in ART.values()})):
        return selected
    paths = portrait_choices(slug, role, origin)
    if not paths:
        return 'images/avatars/hero-00.webp'
    if seed is not None:
        return paths[Random(int(seed)).randrange(min(3, len(paths)))]
    if not (name or origin or role):
        return paths[0]
    raw = '\x1f'.join((slug, name, origin, role)).encode('utf-8')
    idx = int.from_bytes(blake2b(raw, digest_size=4).digest(), 'big') % min(3, len(paths))
    return paths[idx]


def portrait_style(seed: int | None) -> str:
    """Повторяемая цветовая подсветка портрета, без внешних изображений/API."""
    value = int(seed or 0)
    hue = value % 29 - 14
    angle = value % 360
    cyan = ('#31e8ff', '#80b8ff', '#44ffd8')[value % 3]
    pink = ('#ff67d4', '#c785ff', '#ff9bbd')[value // 3 % 3]
    return f'--portrait-hue:{hue}deg;--portrait-angle:{angle}deg;--portrait-cyan:{cyan};--portrait-pink:{pink};'
