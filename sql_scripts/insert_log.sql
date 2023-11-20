CREATE OR REPLACE FUNCTION insert_log(
    date_time_param TIMESTAMP WITHOUT TIME ZONE,
    measurement_type_param CHAR(1),
    quantifier REAL DEFAULT NULL,
    fk_id INT DEFAULT NULL
)
    RETURNS VOID
AS
$$
DECLARE
    measurement_id_param INT;
BEGIN
    -- Step 1: Insert into the supertype table
    INSERT INTO food_log (date_time, measurement_type)
    VALUES (date_time_param, measurement_type_param)
    RETURNING id INTO measurement_id_param;

    -- Step 2: Insert into the corresponding subtype table based on measurement_type
    IF measurement_type_param = 'g' THEN
        INSERT INTO gram_measurement (id, amount, food_id)
        VALUES (measurement_id_param, quantifier, fk_id);
    ELSIF measurement_type_param = 'p' THEN
        INSERT INTO portion_measurement (id, portion_size, food_portion_id)
        VALUES (measurement_id_param, quantifier, fk_id);
    END IF;
    RETURN;
END;
$$ LANGUAGE plpgsql;