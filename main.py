import os
import pandas as pd
import psycopg2 as psycopg

from datetime import datetime, date

import sqlalchemy
from dotenv import load_dotenv
from rich.prompt import *
from rich.table import Table
from rich.traceback import install
from sqlalchemy import create_engine

from DbManager import DbManager
from DIContainer import DIContainer
from FoodLogRepository import FoodLogRepository
from MenuHandler import print_menu, get_choice, in_range
from SeedData import seed_data
from Utils import Utils

def get_date() -> date:
    console = Console()
    while True:
        date_input = Prompt.ask("Enter date (YYYY-MM-DD) or use 't' for today's date")
        if date_input == 't':
            date_obj = datetime.now().date()
            break
        else:
            try:
                date_obj = datetime.strptime(date_input, "%Y-%m-%d").date()
                break
            except ValueError:
                console.print("Invalid date format. Please enter time in YYYY-MM-DD format.", style="bold red")
    return date_obj

def get_datetime() -> datetime:
    console = Console()
    date_obj = get_date()

    while True:
        time_input = Prompt.ask("Enter time (HH:MM) or use 'n' for now")
        if time_input == 'n':
            time_obj = datetime.now().time()
            break
        else:
            try:
                time_obj = datetime.strptime(time_input, "%H:%M").time()
                break
            except ValueError:
                console.print("Invalid time format. Please enter time in HH:MM format.", style="bold red")

    return datetime.combine(date_obj, time_obj)

def get_category_id(food_log_repository: FoodLogRepository) -> int:
    while True:
        console = Console()
        categories = pd.DataFrame(food_log_repository.get_categories(), columns=["id", "description"])
        categories["ID"] = range(len(categories))
        categories_table = Table(title="Food Categories")
        categories_table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        categories_table.add_column("Description", style="magenta")
        for _, row in categories.iterrows():
            categories_table.add_row(str(row["ID"]), row["description"])
        console.print(categories_table)

        console.print("Select from a food category")
        while True:
            selection_range = 0, len(categories) - 1
            category_id = get_choice(selection_range,"Enter category ID [#]")
            real_category_id = categories.loc[categories["ID"] == category_id, "id"].values[0]
            food_id = get_food_id(food_log_repository, real_category_id)
            if food_id == -1:
                continue
            elif food_id == -2:
                break
            else:
                return food_id

def get_food_id(food_log_repository: FoodLogRepository, category_id: int) -> int:
    console = Console()
    foods_temp = food_log_repository.get_foods_from_category(category_id)
    if len(foods_temp) == 0:
        console.print("No foods found in this category", style="bold red")
        return -1
    foods = pd.DataFrame(foods_temp, columns=["id", "name"])
    foods["ID"] = range(len(foods))
    foods_table = Table(title="Foods")
    foods_table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    foods_table.add_column("Name", style="magenta")
    for _, row in foods.iterrows():
        foods_table.add_row(str(row["ID"]), row["name"])
    console.print(foods_table)
    while True:
        user_input = Prompt.ask("Enter food ID [#] or use 'b' to go back")
        if user_input == 'b':
            return -2
        low, high = 0, len(foods) - 1
        if in_range(user_input, low, high) == -1:
            console.print(f"Please enter a number between {low} and {high}.", style="bold red")
            continue
        food_id = int(user_input)
        break

    real_food_id = int(foods.loc[foods["ID"] == food_id, "id"].values[0])
    return real_food_id

def convert_dataframe_to_table(df: pd.DataFrame, title: str) -> Table:
    table = Table(title=title)
    for column in df.columns:
        table.add_column(column, justify="right", style="cyan", no_wrap=True)
    for _, row in df.iterrows():
        table.add_row(*row)
    return table


class App:
    def __init__(self):
        self.food_log_repository: FoodLogRepository = None
        self.conn_sqlalchemy: sqlalchemy.Connection = None
        self.conn_psycopg: psycopg.connection = None
        self.console = Console()

    def configure_db_connection(self) -> None:
        load_dotenv()
        # In the form: postgresql://username:password@localhost:port/database_name
        database_url = os.getenv("database_url")
        db = create_engine(database_url)
        self.conn_sqlalchemy = db.connect()

        self.conn_psycopg = psycopg.connect(database_url)
        self.conn_psycopg.autocommit = True

    def register_services(self) -> DIContainer:
        utils: Utils = Utils(conn_psycopg=self.conn_psycopg)
        container = DIContainer()
        container.add_singleton(DbManager, conn_sqlalchemy=self.conn_sqlalchemy, utils=utils)
        container.add_singleton(FoodLogRepository, conn_psycopg=self.conn_psycopg)
        return container

    def run(self) -> None:
        self.configure_db_connection()
        container = self.register_services()

        db_manager: DbManager = container.get_instance(DbManager.__name__)
        self.food_log_repository: FoodLogRepository = container.get_instance(FoodLogRepository.__name__)

        db_manager.drop_all()
        db_manager.configure_database()
        seed_data(self.food_log_repository)

        self.console.print("-- Nutrition Tracker --", style="bold cyan")
        while True:
            main_menu_items = ["Add food log", "View daily nutrients"]
            choice = get_choice(print_menu(main_menu_items, has_exit=True))
            if choice == 1:
                self.add_food_log()
            elif choice == 2:
                self.view_daily_nutrients()
            elif choice == 0:
                break
            else:
                print("Invalid choice")

    def add_food_log(self):
        food_id = get_category_id(self.food_log_repository)
        date_time = get_datetime()
        measurement_type = 'g'
        gram_amount = get_choice((0, 1000), "Enter gram amount (0-1000)")

        if Confirm.ask("Do you want to add this log?"):
            self.food_log_repository.insert_log(date_time, measurement_type, gram_amount, food_id)

    def view_daily_nutrients(self):
        console = Console()
        date_info = get_date()
        daily_nutrients_temp = self.food_log_repository.get_daily_nutrients(date_info)
        daily_nutrients = pd.DataFrame(daily_nutrients_temp, columns=["food_name", "nutrient_name", "nutrient_amount", "nutrient_unit"])
        daily_nutrients["ID"] = range(len(daily_nutrients))
        daily_nutrients_table = Table(title="Food Categories")
        daily_nutrients_table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        daily_nutrients_table.add_column("Description", style="magenta")
        for _, row in daily_nutrients.iterrows():
            daily_nutrients_table.add_row(str(row["ID"]), row["food_name"], row["nutrient_name"], str(row["nutrient_amount"]), row["nutrient_unit"])
        console.print(daily_nutrients_table)

if __name__ == '__main__':
    install() # Rich traceback handler
    App().run()
