import pandas as pd


class DbManager:
    def __init__(self, **kwargs):
        self.utils = kwargs["utils"]
        self.conn_sqlalchemy = kwargs["conn_sqlalchemy"]

    def configure_database(self):
        self.utils.run_sql_file("sql_scripts/create_tables.sql")
        self.utils.run_sql_file("sql_scripts/create_types.sql")
        self.utils.run_sql_file("sql_scripts/insert_log.sql")
        self.utils.run_sql_file("sql_scripts/get_daily_nutrients.sql")
        self.insert_data()

    def insert_data(self):
        foundation_food = pd.read_csv("foundation_food.csv",
                                      usecols=lambda x: x not in ["NDB_number", "footnote"],
                                      dtype={"fdc_id": int})
        nutrient, nutrient_unit, nutrient_temp = None, None, None

        if self.utils.is_empty("category"):
            category = pd.read_csv("food_category.csv",
                                        dtype={"id": int, "code": str, "description": str})
            category.to_sql("category", con=self.conn_sqlalchemy, if_exists="append", index=False)

        if self.utils.is_empty("measure_unit"):
            measure_unit = pd.read_csv("measure_unit.csv",
                                       dtype={"id": int, "name": str})
            measure_unit.to_sql("measure_unit", con=self.conn_sqlalchemy, if_exists="append", index=False)

        if self.utils.is_empty("food"):
            food = pd.read_csv("food.csv",
                               usecols=["fdc_id", "description", "food_category_id"],
                               dtype={"fdc_id": int, "description": str, "food_category_id": "Int64"}).merge(
                foundation_food, on="fdc_id", how="inner")
            new_food_columns = {"fdc_id": "id", "description": "name", "food_category_id": "category_id"}
            food.rename(columns=new_food_columns, inplace=True)
            food.to_sql("food", con=self.conn_sqlalchemy, if_exists="append", index=False)

        if self.utils.is_empty("nutrient_unit"):
            nutrient_temp = pd.read_csv("nutrient.csv",
                                        usecols=["id", "name", "unit_name"],
                                        dtype={"id": int, "name": str, "unit_name": str})
            nutrient_unit = pd.DataFrame({"name": nutrient_temp["unit_name"].unique()})
            nutrient_unit["id"] = range(len(nutrient_unit))
            nutrient_unit = nutrient_unit[["id", "name"]]
            nutrient_unit.to_sql("nutrient_unit", con=self.conn_sqlalchemy, if_exists="append", index=False)

        if self.utils.is_empty("nutrient") and nutrient_unit is not None and nutrient_temp is not None:
            nutrient_unit.rename(columns={"id": "nutrient_unit_id", "name": "unit_name"}, inplace=True)
            nutrient = pd.merge(nutrient_temp, nutrient_unit, on="unit_name", how="left")
            nutrient.drop(columns=["unit_name"], inplace=True)
            nutrient.to_sql("nutrient", con=self.conn_sqlalchemy, if_exists="append", index=False)

        if self.utils.is_empty("food_nutrient") and nutrient is not None:
            food_nutrient_temp = pd.read_csv("food_nutrient.csv",
                                             usecols=["id", "amount", "fdc_id", "nutrient_id"],
                                             dtype={"amount": float, "fdc_id": int, "nutrient_id": int}).merge(
                foundation_food, on="fdc_id", how="inner")
            food_nutrient = food_nutrient_temp[food_nutrient_temp["nutrient_id"].isin(
                nutrient["id"])].copy()  # Filter out food_nutrients that are not in the nutrient table
            food_nutrient["amount"] = food_nutrient["amount"].fillna(0)
            food_nutrient["id"] = range(len(food_nutrient))
            food_nutrient.rename(columns={"fdc_id": "food_id"}, inplace=True)
            food_nutrient.to_sql("food_nutrient", con=self.conn_sqlalchemy, if_exists="append", index=False)

        if self.utils.is_empty("food_portion"):
            food_portion = pd.read_csv("food_portion.csv",
                                       usecols=["id", "amount", "modifier", "gram_weight", "fdc_id", "measure_unit_id"],
                                       dtype={"amount": float, "modifier": str, "gram_weight": float, "fdc_id": int,
                                              "measure_unit_id": int})
            food_portion = pd.merge(food_portion, foundation_food, on="fdc_id", how="inner")
            food_portion["id"] = range(len(food_portion))
            food_portion.rename(columns={"fdc_id": "food_id"}, inplace=True)
            food_portion.to_sql("food_portion", con=self.conn_sqlalchemy, if_exists="append", index=False)

    def drop_all(self):
        self.utils.run_sql_file("sql_scripts/drop_all.sql")
