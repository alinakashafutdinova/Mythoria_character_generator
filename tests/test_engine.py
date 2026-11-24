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

def test_fallout_special_points():
    for i in range(40):
        assert sum(generate('fallout',seed=i)['stats'].values())==28

def test_vampire_dots():
    assert sum(generate('vampire',seed=1)['stats'].values())==22

def test_elden_initial_stats():
    assert generate('elden',role='Самурай',seed=1)['stats']['Ловкость']==15
