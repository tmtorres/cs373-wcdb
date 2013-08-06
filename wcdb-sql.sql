-- Get Celebrities (Actors, Musicians, Athletes) related to Crises/Orginizations

show databases;
use cs373_ejenioc;
show tables;

-- Show content of tables
SELECT "";
SELECT `COLUMN_NAME` as 'database_entity_columns' FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='cs373_ejenioc' AND `TABLE_NAME`='database_entity';
SELECT "";
SELECT `COLUMN_NAME` as 'database_crisis_columns' FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='cs373_ejenioc' AND `TABLE_NAME`='database_crisis';
SELECT "";
SELECT `COLUMN_NAME` as 'database_crisis_organizations_columns' FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='cs373_ejenioc' AND `TABLE_NAME`='database_crisis_organizations';
SELECT "";
SELECT `COLUMN_NAME` as 'database_crisis_people_columns' FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='cs373_ejenioc' AND `TABLE_NAME`='database_crisis_people';
SELECT "";

-- Crisix Queries

SELECT "Get Celebrities (Actors, Musicians, Athletes) related to Crises/Orginizations";
SELECT id FROM database_entity WHERE id LIKE "PER_%" and kind REGEXP '.*(Actor|Actress|Singer|Celebrity|Athlete|Player$).*';
SELECT "";

SELECT "Get all Crises/Organizations/People who have feeds";
SELECT DISTINCT entity_id FROM database_webelement WHERE ctype = "FEED";
SELECT "";

SELECT "Get the name and location of all crises related to natural disasters";
SELECT kind, name, location FROM database_entity WHERE (kind LIKE "%Earthquake%" or kind LIKE "%Natural Disaster%" OR kind LIKE "%Epidemic%") and id LIKE "CRI_%";
SELECT "";

SELECT "People involved in crises that happened in China/Japan";
SELECT person_id FROM database_crisis_people WHERE crisis_id IN
	(SELECT id FROM database_entity WHERE (location LIKE "%China%" OR location LIKE "%Japan%") AND id LIKE "CRI_%");
SELECT "";

SELECT "Crises that are tied to a president";
SELECT crisis_id FROM database_crisis_people WHERE person_id IN
	(SELECT id FROM database_entity WHERE kind LIKE "%President%");
SELECT "";

-- Other Group Queries
SELECT "All crises in alphabetical order by name of crisis (no duplicates)";
SELECT DISTINCT id, name FROM database_entity WHERE id LIKE "CRI_%" ORDER BY name;
SELECT "";

SELECT "Crises whose kind value contains the word 'shooting'";
SELECT id, name FROM database_entity WHERE kind LIKE "%Shooting%" AND id LIKE "CRI_%";
SELECT "";

SELECT "All people with first names that start with letters A through P (no duplicates)";
SELECT id, name FROM database_entity WHERE name REGEXP '^[A-P]' AND id LIKE "PER_%" ORDER BY name;
SELECT "";

SELECT "Show the name and economic impact of natural disasters occuring after 2001";
SELECT e.name, c.eimpact FROM database_crisis c, database_entity e WHERE date >= '2002-01-01' AND c.entity_ptr_id = e.id; 
SELECT "";

SELECT "Crises that took place in Texas (Location data should contain 'Texas' or 'TX')";
SELECT id, name, location FROM database_entity WHERE (location LIKE "%Texas%" OR location LIKE "%TX%") and id LIKE "CRI_%";
SELECT "";

exit