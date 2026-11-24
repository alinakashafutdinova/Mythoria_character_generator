PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS games (
 id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
 game_group TEXT NOT NULL CHECK (game_group IN ('tabletop','video')),
 edition TEXT NOT NULL, description TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS game_options (
 id INTEGER PRIMARY KEY, game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
 option_group TEXT NOT NULL CHECK(option_group IN ('origin','role')),
 label TEXT NOT NULL, UNIQUE(game_id,option_group,label)
);
CREATE TABLE IF NOT EXISTS attribute_definitions (
 id INTEGER PRIMARY KEY, game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
 label TEXT NOT NULL, min_value INTEGER NOT NULL DEFAULT 0, max_value INTEGER NOT NULL DEFAULT 200,
 UNIQUE(game_id,label),CHECK(max_value >= min_value)
);
CREATE TABLE IF NOT EXISTS characters (
 id INTEGER PRIMARY KEY, game_id INTEGER NOT NULL REFERENCES games(id),
 name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 80),
 origin_option_id INTEGER NOT NULL REFERENCES game_options(id),
 role_option_id INTEGER NOT NULL REFERENCES game_options(id),
 level INTEGER NOT NULL CHECK(level BETWEEN 1 AND 150),
 bio TEXT NOT NULL DEFAULT '' CHECK(length(bio) <= 1000),
 favorite INTEGER NOT NULL DEFAULT 0 CHECK(favorite IN (0,1)),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS character_stats (
 id INTEGER PRIMARY KEY, character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
 attribute_id INTEGER NOT NULL REFERENCES attribute_definitions(id),
 value INTEGER NOT NULL CHECK(value BETWEEN 0 AND 200),
 UNIQUE(character_id,attribute_id)
);
CREATE TABLE IF NOT EXISTS abilities (
 id INTEGER PRIMARY KEY, game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
 label TEXT NOT NULL, UNIQUE(game_id,label)
);
CREATE TABLE IF NOT EXISTS character_abilities (
 character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
 ability_id INTEGER NOT NULL REFERENCES abilities(id),
 PRIMARY KEY(character_id,ability_id)
);
CREATE INDEX IF NOT EXISTS idx_characters_game ON characters(game_id);
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_character_stats_character ON character_stats(character_id);
