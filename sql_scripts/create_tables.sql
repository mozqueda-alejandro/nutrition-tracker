CREATE OR REPLACE PROCEDURE create_tables()
    LANGUAGE plpgsql
AS
$$
BEGIN

    CREATE TABLE IF NOT EXISTS category
    (
        id          INT PRIMARY KEY,
        description VARCHAR(40) NOT NULL,
        code        VARCHAR(4)  NOT NULL
    );

    CREATE TABLE IF NOT EXISTS measure_unit
    (
        id   INT PRIMARY KEY,
        name VARCHAR(20) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS food
    (
        id          INT PRIMARY KEY,
        name        VARCHAR(128) NOT NULL,
        category_id INT          NOT NULL REFERENCES category (id)
    );
    CREATE INDEX IF NOT EXISTS idx_food_category_id ON food (category_id);

    CREATE TABLE IF NOT EXISTS nutrient_unit
    (
        id   INT PRIMARY KEY,
        name VARCHAR(8) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS nutrient
    (
        id               INT PRIMARY KEY,
        name             VARCHAR(128) NOT NULL,
        nutrient_unit_id INT          NOT NULL REFERENCES nutrient_unit (id)
    );
    CREATE INDEX IF NOT EXISTS idx_nutrient_nutrient_unit_id ON nutrient (nutrient_unit_id);

    CREATE TABLE IF NOT EXISTS food_nutrient
    (
        id          INT PRIMARY KEY,
        amount      REAL NOT NULL,
        food_id     INT  NOT NULL REFERENCES food (id),
        nutrient_id INT  NOT NULL REFERENCES nutrient (id)
    );
    CREATE INDEX IF NOT EXISTS idx_food_nutrient_food_id ON food_nutrient (food_id);
    CREATE INDEX IF NOT EXISTS idx_food_nutrient_nutrient_id ON food_nutrient (nutrient_id);

    CREATE TABLE IF NOT EXISTS food_portion
    (
        id              INT PRIMARY KEY,
        amount          REAL NOT NULL,
        modifier        VARCHAR(60),
        gram_weight     REAL NOT NULL,
        food_id         INT  NOT NULL REFERENCES food (id),
        measure_unit_id INT  NOT NULL REFERENCES measure_unit (id)
    );
    CREATE INDEX IF NOT EXISTS idx_food_portion_food_id ON food_portion (food_id);
    CREATE INDEX IF NOT EXISTS idx_food_portion_measure_unit_id ON food_portion (measure_unit_id);

    CREATE TABLE IF NOT EXISTS food_log
    (
        id               SERIAL PRIMARY KEY,
        date_time        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        measurement_type CHAR(1)                     NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_food_log_food_portion_id ON food_log (id);

    CREATE TABLE IF NOT EXISTS gram_measurement
    (
        id      INT PRIMARY KEY,
        amount  INT NOT NULL,
        food_id INT NOT NULL REFERENCES food (id),
        FOREIGN KEY (id) REFERENCES food_log (id)
    );
    CREATE INDEX IF NOT EXISTS idx_gram_measurement_food_id ON gram_measurement (food_id);

    CREATE TABLE IF NOT EXISTS portion_measurement
    (
        id              INT PRIMARY KEY,
        portion_size    REAL NOT NULL,
        food_portion_id INT  NOT NULL REFERENCES food_portion (id),
        FOREIGN KEY (id) REFERENCES food_log (id)
    );
    CREATE INDEX IF NOT EXISTS idx_portion_measurement_food_portion_id ON portion_measurement (food_portion_id);
END;
$$;

CALL create_tables();
