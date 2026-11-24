-- 1. Персонажи и их игровые системы
SELECT c.id, c.name, g.title AS game_name, role.label AS role_name
FROM characters c
JOIN games g ON g.id = c.game_id
JOIN game_options role ON role.id = c.role_option_id
ORDER BY c.id DESC;

-- 2. Избранные персонажи выбранной игры
SELECT c.id, c.name, c.level FROM characters c
JOIN games g ON g.id = c.game_id
WHERE c.favorite = 1 AND g.slug = 'dnd';

-- 3. Поиск персонажей по имени
SELECT id, name, created_at FROM characters
WHERE name LIKE '%а%' ORDER BY name COLLATE NOCASE;

-- 4. Количество персонажей по играм
SELECT g.title, COUNT(c.id) AS characters_count
FROM games g LEFT JOIN characters c ON c.game_id = g.id
GROUP BY g.id ORDER BY characters_count DESC;

-- 5. Связь персонажей со способностями
SELECT c.name, a.label AS ability FROM characters c
JOIN character_abilities ca ON ca.character_id = c.id
JOIN abilities a ON a.id = ca.ability_id
ORDER BY c.name, a.label;

-- 6. Средние значения характеристик
SELECT g.title, a.label, ROUND(AVG(s.value), 2) AS average_value
FROM character_stats s
JOIN attribute_definitions a ON a.id = s.attribute_id
JOIN characters c ON c.id = s.character_id
JOIN games g ON g.id = c.game_id
GROUP BY g.id, a.id ORDER BY g.title, a.label;
