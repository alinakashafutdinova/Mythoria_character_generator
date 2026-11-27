import pytest
from characterlab.catalog import GAMES
from characterlab.engine import generate,InvalidGeneration

@pytest.mark.parametrize('game',GAMES,ids=lambda g:g.slug)
def test_every_game_is_generated(game):
    result=generate(game.slug,seed=42)
    assert result['game_slug']==game.slug
    assert result['origin'] in game.origins
    assert result['role'] in game.roles
    assert set(result['stats'])==set(game.stats)
    assert all(isinstance(v,int) for v in result['stats'].values())
    assert result['abilities']

@pytest.mark.parametrize('game',GAMES,ids=lambda g:g.slug)
def test_seed_is_reproducible(game):
    assert generate(game.slug,seed=12)==generate(game.slug,seed=12)

def test_invalid_parameters():
    with pytest.raises(InvalidGeneration): generate('unknown')
    with pytest.raises(InvalidGeneration): generate('dnd',role='Тёмный маг')
    with pytest.raises(InvalidGeneration): generate('dnd',level=-1)

def test_disco_profile_points():
    for i in range(40):
        hero=generate('disco',seed=i)
        assert sum(hero['stats'].values())==12
        assert all(1<=x<=6 for x in hero['stats'].values())

def test_vampire_dots():
    assert sum(generate('vampire',seed=1)['stats'].values())==22

def test_removed_games_are_disabled():
    for slug in ('fallout','skyrim','elden','bg3','divinity','dragonage','wow','diablo'):
        with pytest.raises(InvalidGeneration): generate(slug)

def test_new_character_builds():
    assert set(generate('poe',seed=12)['stats'])=={'Сила','Ловкость','Интеллект'}
    assert generate('darkest',seed=12)['role'] in ('Крестоносец','Чумной доктор','Охотник за головами','Весталка','Разбойник','Оккультист')
