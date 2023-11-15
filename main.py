import pandas as pd
import psycopg2 as psycopg
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

def configure():
    load_dotenv()

    # In the form: postgresql://username:password@localhost:port/database_name
    database_url = os.getenv("database_url")

    db = create_engine(database_url)
    conn_sqlalchemy = db.connect()

    conn_psycopg = psycopg.connect(database_url)
    conn_psycopg.autocommit = True
    cursor = conn_psycopg.cursor()

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 10)
    pd.set_option("display.width", 150)

    return conn_sqlalchemy, conn_psycopg, cursor


def main():
    conn_sqlalchemy, conn_psycopg, cursor = configure()
    sql_create_tables = []

    sql_food_category = '''
        CREATE TABLE IF NOT EXISTS category (
            id INT PRIMARY KEY,
            description VARCHAR(40) NOT NULL,
            code VARCHAR(4) NOT NULL
        );
    '''
    sql_create_tables.append(sql_food_category)

    sql_measure_unit = '''
        CREATE TABLE IF NOT EXISTS measure_unit (
            id INT PRIMARY KEY,
            name VARCHAR(20) NOT NULL
        );
    '''
    sql_create_tables.append(sql_measure_unit)

    sql_food = '''
        CREATE TABLE IF NOT EXISTS food (
            id INT PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            category_id INT NOT NULL REFERENCES category (id)
        );
        CREATE INDEX IF NOT EXISTS idx_food_category_id ON food (category_id);
    '''
    sql_create_tables.append(sql_food)

    sql_nutrient_unit = '''
        CREATE TABLE IF NOT EXISTS nutrient_unit (
            id INT PRIMARY KEY,
            name VARCHAR(8) NOT NULL
        );
    '''
    sql_create_tables.append(sql_nutrient_unit)

    sql_nutrient = '''
        CREATE TABLE IF NOT EXISTS nutrient (
            id INT PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            nutrient_unit_id INT NOT NULL REFERENCES nutrient_unit (id)
        );
        CREATE INDEX IF NOT EXISTS idx_nutrient_nutrient_unit_id ON nutrient (nutrient_unit_id);
    '''
    sql_create_tables.append(sql_nutrient)

    sql_food_nutrient = '''
        CREATE TABLE IF NOT EXISTS food_nutrient(
            id INT PRIMARY KEY,
            amount REAL NOT NULL,
            food_id INT NOT NULL REFERENCES food (id),
            nutrient_id INT NOT NULL REFERENCES nutrient (id)
        );
        CREATE INDEX IF NOT EXISTS idx_food_nutrient_food_id ON food_nutrient (food_id);
        CREATE INDEX IF NOT EXISTS idx_food_nutrient_nutrient_id ON food_nutrient (nutrient_id);
    '''
    sql_create_tables.append(sql_food_nutrient)

    sql_food_portion = '''
        CREATE TABLE IF NOT EXISTS food_portion (
            id INT PRIMARY KEY,
            amount REAL NOT NULL,
            modifier VARCHAR(60),
            gram_weight REAL NOT NULL,
            food_id INT NOT NULL REFERENCES food (id),
            measure_unit_id INT NOT NULL REFERENCES measure_unit (id)
        );
        CREATE INDEX IF NOT EXISTS idx_food_portion_food_id ON food_portion (food_id);
        CREATE INDEX IF NOT EXISTS idx_food_portion_measure_unit_id ON food_portion (measure_unit_id);
    '''
    sql_create_tables.append(sql_food_portion)

    sql_food_log = '''
        CREATE TABLE IF NOT EXISTS food_log (
            id INT PRIMARY KEY,
            date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            measurement_type CHAR(1) NOT NULL
            -- g = gram_measurement, p = portion_measurement
        );
        CREATE INDEX IF NOT EXISTS idx_food_log_food_portion_id ON food_log (id);
    '''
    sql_create_tables.append(sql_food_log)

    sql_gram_measurement = '''
        CREATE TABLE IF NOT EXISTS gram_measurement (
            id INT PRIMARY KEY,
            amount INT NOT NULL,
            food_id INT NOT NULL REFERENCES food (id),
            FOREIGN KEY (id) REFERENCES food_log (id)
        );
        CREATE INDEX IF NOT EXISTS idx_gram_measurement_food_id ON gram_measurement (food_id);
    '''
    sql_create_tables.append(sql_gram_measurement)

    sql_portion_measurement = '''
        CREATE TABLE IF NOT EXISTS portion_measurement (
            id INT PRIMARY KEY,
            portion_size REAL NOT NULL,
            food_portion_id INT NOT NULL REFERENCES food_portion (id),
            FOREIGN KEY (id) REFERENCES food_log (id)
        );
        CREATE INDEX IF NOT EXISTS idx_portion_measurement_food_portion_id ON portion_measurement (food_portion_id);
    '''
    sql_create_tables.append(sql_portion_measurement)

    for sql in sql_create_tables:
        cursor.execute(sql)

    conn_psycopg.commit()

    ################ Food Category #################
    food_category = pd.read_csv("food_category.csv",
                                dtype={"id": int, "code": str, "description": str})
    # print("FOOD CATEGORY: \n", food_category.head())
    food_category.to_sql("category", con=conn_sqlalchemy, if_exists="append", index=False)
    conn_psycopg.commit()


    ################ Measure Unit #################
    measure_unit = pd.read_csv("measure_unit.csv",
                               dtype={"id": int, "name": str})
    measure_unit.to_sql("measure_unit", con=conn_sqlalchemy, if_exists="append", index=False)
    print("MEASURE UNIT: \n", measure_unit.head())

    ################ Foundation Food #################
    foundation_food = pd.read_csv("foundation_food.csv",
                                  usecols=lambda x: x not in ["NDB_number", "footnote"],
                                  dtype={"fdc_id": int})
    print("FOUNDATION FOOD: \n", foundation_food.head())

    ################ Food #################
    food_temp = pd.read_csv("food.csv",
                       usecols=["fdc_id", "description", "food_category_id"],
                       dtype={"fdc_id": int, "description": str, "food_category_id": "Int64"})
    food = pd.merge(food_temp, foundation_food, on="fdc_id", how="inner")
    new_food_columns = {"fdc_id": "id", "description": "name", "food_category_id": "category_id"}
    food.rename(columns=new_food_columns, inplace=True)
    food.to_sql("food", con=conn_sqlalchemy, if_exists="append", index=False)
    print("FOOD: \n", food.head())

    ############### Nutrient Unit #################
    nutrient_temp = pd.read_csv("nutrient.csv",
                           usecols=["id", "name", "unit_name"],
                           dtype={"id": int, "name": str, "unit_name": str})

    nutrient_unit = pd.DataFrame({"name": nutrient_temp["unit_name"].unique()}) # Get all unique nutrient units
    nutrient_unit["id"] = range(len(nutrient_unit))
    nutrient_unit = nutrient_unit[["id", "name"]] # Reorder columns
    nutrient_unit.to_sql("nutrient_unit", con=conn_sqlalchemy, if_exists="append", index=False)
    print("NUTRIENT UNIT: \n", nutrient_unit.head())

    ################ Nutrient #################
    nutrient_unit.rename(columns={"id": "nutrient_unit_id", "name": "unit_name"}, inplace=True) # Nutrient unit formatting
    nutrient = pd.merge(nutrient_temp, nutrient_unit, on="unit_name", how="left")
    nutrient.drop(columns=["unit_name"], inplace=True)
    nutrient.to_sql("nutrient", con=conn_sqlalchemy, if_exists="append", index=False)
    print("NUTRIENT: \n", nutrient.head())

    ################ Food Nutrient #################
    food_nutrient_1 = pd.read_csv("food_nutrient.csv",
                                usecols=["id", "amount", "fdc_id", "nutrient_id"],
                                dtype={"amount": float, "fdc_id": int, "nutrient_id": int})
    food_nutrient_2 = pd.merge(food_nutrient_1, foundation_food, on="fdc_id", how="inner")
    food_nutrient = food_nutrient_2[food_nutrient_2["nutrient_id"].isin(nutrient["id"])].copy()
    food_nutrient["amount"] = food_nutrient["amount"].fillna(0)
    food_nutrient["id"] = range(len(food_nutrient))
    food_nutrient.rename(columns={"fdc_id": "food_id"}, inplace=True)
    food_nutrient.to_sql("food_nutrient", con=conn_sqlalchemy, if_exists="append", index=False)
    print("FOOD NUTRIENT: \n", food_nutrient.head())

    ################ Food Portion #################
    food_portion = pd.read_csv("food_portion.csv",
                               usecols=["id", "amount", "modifier", "gram_weight", "fdc_id", "measure_unit_id"],
                               dtype={"amount": float, "modifier": str, "gram_weight": float, "fdc_id": int, "measure_unit_id": int})
    food_portion = pd.merge(food_portion, foundation_food, on="fdc_id", how="inner")
    food_portion["id"] = range(len(food_portion))
    food_portion.rename(columns={"fdc_id": "food_id"}, inplace=True)
    food_portion.to_sql("food_portion", con=conn_sqlalchemy, if_exists="append", index=False)
    print("FOOD PORTION: \n", food_portion.head())

    conn_psycopg.commit()
    conn_psycopg.close()

if __name__ == '__main__':
    main()
