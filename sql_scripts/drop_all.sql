DROP TABLE IF EXISTS food_nutrient;

DROP TABLE IF EXISTS nutrient;

DROP TABLE IF EXISTS nutrient_unit;

DROP TABLE IF EXISTS gram_measurement;

DROP TABLE IF EXISTS portion_measurement;

DROP TABLE IF EXISTS food_portion;

DROP TABLE IF EXISTS measure_unit;

DROP TABLE IF EXISTS food;

DROP TABLE IF EXISTS category;

DROP TABLE IF EXISTS food_log;

DROP PROCEDURE IF EXISTS create_tables();

DROP FUNCTION IF EXISTS insert_log(timestamp, char, real, integer);

DROP FUNCTION IF EXISTS select_daily_nutrients(date);

DROP TYPE IF EXISTS nutrients_per_food_per_day;
