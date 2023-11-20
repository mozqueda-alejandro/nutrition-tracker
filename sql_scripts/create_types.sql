DO
$$
    BEGIN
        CREATE TYPE nutrients_per_food_per_day AS
        (
            food_name       varchar(128),
            nutrient_name   varchar(128),
            nutrient_amount real,
            nutrient_unit   varchar(8)
        );
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END
$$;
