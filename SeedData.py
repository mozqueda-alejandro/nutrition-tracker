

def seed_data(food_log_repository):
    food_log_repository.insert_log("2004-10-19 10:23:54", 'g', 100, 321358)
    food_log_repository.insert_log("2021-01-02 01:00:00", 'g', 50, 321358)
    food_log_repository.insert_log("2021-01-02 01:00:00", 'p', 1, 0)
    food_log_repository.insert_log("2021-01-02 02:00:00", 'p', 1, 1)
