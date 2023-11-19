CREATE OR REPLACE FUNCTION select_daily_nutrients(
    date_param DATE
)
    RETURNS TABLE
            (
                result_row nutrients_per_food_per_day
            )
AS
$$
BEGIN
    RETURN QUERY SELECT f.name, n.name, (fn.amount * gram_amount / 100)::REAL, nu.name
                 FROM (SELECT SUM(t_gram_amount) AS gram_amount, t_food_id
                       FROM (SELECT COALESCE(g.amount, (p.portion_size * fp.gram_weight)::REAL) AS t_gram_amount,
                                    COALESCE(g.food_id, fp.food_id)                             AS t_food_id
                             FROM food_log fl
                                      LEFT JOIN gram_measurement g ON fl.id = g.id AND fl.measurement_type = 'g'
                                      LEFT JOIN portion_measurement p ON fl.id = p.id AND fl.measurement_type = 'p'
                                      LEFT JOIN food_portion fp
                                                ON p.food_portion_id = fp.id AND fl.measurement_type = 'p'
                             WHERE fl.date_time::date = date_param::date) AS raw_logs
                       GROUP BY raw_logs.t_food_id) AS formatted_logs
                          LEFT JOIN food f ON t_food_id = f.id
                          LEFT JOIN food_nutrient fn ON t_food_id = fn.food_id AND fn.amount != 0
                          LEFT JOIN nutrient n ON fn.nutrient_id = n.id
                          LEFT JOIN nutrient_unit nu ON n.nutrient_unit_id = nu.id;
    RETURN;
END;
$$ LANGUAGE plpgsql;