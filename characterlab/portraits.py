"""Тематические оригинальные портреты для 16 поддерживаемых игровых систем.

Иллюстрации выбираются устойчиво для одного героя. Это не генерация изображений
нейросетью при нажатии кнопки: портреты подготовлены для учебного проекта.
"""
from hashlib import blake2b

POOLS = {
    'dnd': (0, 1, 5, 8, 9, 10, 13, 14),
    'pathfinder': (1, 0, 8, 9, 10, 11, 13, 14),
    'cthulhu': (2, 4, 5, 11),
    'cyberpunk': (3, 7, 12, 15),
    'vampire': (4, 2, 8, 11),
    'warhammer': (5, 0, 10, 11, 14),
    'starfinder': (6, 15, 3, 7),
    'shadowrun': (7, 3, 15, 12),
    'bg3': (8, 1, 9, 0, 13),
    'divinity': (9, 1, 8, 10, 13),
    'skyrim': (10, 5, 9, 11),
    'elden': (11, 5, 13, 10),
    'fallout': (12, 7, 3, 15),
    'dragonage': (13, 0, 1, 8, 9),
    'wow': (14, 5, 0, 13, 10),
    'diablo': (15, 11, 5, 14),
}


def portrait_for(slug: str, name: str = '', origin: str = '', role: str = '') -> str:
    """Путь к иллюстрации, одинаковый для предпросмотра и сохранённого героя."""
    pool = POOLS.get(slug, (0,))
    if name or origin or role:
        data = '\x1f'.join((slug, name, origin, role)).encode('utf-8')
        index = int.from_bytes(blake2b(data, digest_size=4).digest(), 'big') % len(pool)
    else:
        index = 0
    return f'images/avatars/hero-{pool[index]:02d}.webp'
