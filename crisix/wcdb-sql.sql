-- Get Celebrities (Actors, Musicians, Athletes) related to Crises/Orginizations

-- show databases;
-- use cs373_ejenioc;
-- show tables;

-- -- Crisix Queries

"Get Celebrities (Actors, Musicians, Athletes) related to Crises/Orginizations"
SELECT id, kind, name FROM database_entity e WHERE id LIKE "PER_%%" and kind REGEXP '.*(Actor|Actress|Singer|Celebrity|Athlete|Player).*' AND (EXISTS (SELECT * from database_crisis_people cp WHERE cp.person_id = e.id) OR EXISTS (SELECT * from database_organization_people cp WHERE cp.person_id = e.id));

"Get all Crises/Organizations/People who have feeds"
SELECT DISTINCT entity_id, name FROM database_webelement AS w, database_entity AS e WHERE ctype = "FEED" AND w.entity_id = e.id;

"Get the name and location of all crises related to natural disasters"
SELECT kind, name, location FROM database_entity WHERE kind REGEXP '.*(Earthquake|Fire|Tsunami|Natural Disaster|Epidemic|Hurricane|Tornado|Flood|Storm|Blizzard).*' AND id LIKE "CRI_%%";

"People involved in crises that happened in China/Japan"
SELECT person_id, name FROM database_crisis_people AS p, database_entity AS e WHERE p.person_id=e.id AND crisis_id IN (SELECT id FROM database_entity WHERE (location LIKE "%%China%%" OR location LIKE "%%Japan%%") AND id LIKE "CRI_%%");

"Crises that are tied to a president"
SELECT crisis_id, name FROM database_crisis_people AS p, database_entity AS e WHERE p.crisis_id=e.id AND person_id IN (SELECT id FROM database_entity WHERE kind LIKE "%%President%%");

-- Other Group Queries
"All crises in alphabetical order by name of crisis (no duplicates)"
SELECT DISTINCT id, name FROM database_entity WHERE id LIKE "CRI_%%" ORDER BY name;

"Crises whose kind value contains the word 'shooting'"
SELECT id, kind, name FROM database_entity WHERE kind LIKE "%%Shooting%%" AND id LIKE "CRI_%%";

"All people with first names that start with letters A through P (no duplicates)"
SELECT id, name FROM database_entity WHERE name REGEXP '^[A-P]' AND id LIKE "PER_%%" ORDER BY name;

"Show the name and economic impact of natural disasters occuring after 2001"
SELECT c.date, e.kind, e.name, c.eimpact FROM database_crisis c, database_entity e WHERE date >= '2002-01-01' AND kind REGEXP '.*(Earthquake|Fire|Tsunami|Natural Disaster|Epidemic|Hurricane|Tornado|Flood|Storm|Blizzard).*' AND c.entity_ptr_id = e.id ORDER BY c.date; 

"Crises that took place in Texas (Location data should contain 'Texas' or 'TX')"
SELECT id, name, location FROM database_entity WHERE (location LIKE "%%Texas%%" OR location LIKE "%%TX%%") and id LIKE "CRI_%%";
