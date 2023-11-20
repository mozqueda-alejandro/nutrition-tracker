import os
import psycopg2 as psycopg

from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.prompt import *
from rich.table import Table
from rich.traceback import install
from sqlalchemy import create_engine

from DbManager import DbManager
from DIContainer import DIContainer
from FoodLogRepository import FoodLogRepository
from SeedData import seed_data
from Utils import Utils


class App:
    def __init__(self):
        self.conn_sqlalchemy = None
        self.conn_psycopg = None

    def configure_db_connection(self):
        load_dotenv()
        # In the form: postgresql://username:password@localhost:port/database_name
        database_url = os.getenv("database_url")
        db = create_engine(database_url)
        self.conn_sqlalchemy = db.connect()

        self.conn_psycopg = psycopg.connect(database_url)
        self.conn_psycopg.autocommit = True

    def register_services(self) -> DIContainer:
        container = DIContainer()
        utils: Utils = Utils(conn_psycopg=self.conn_psycopg)
        container.add_singleton(DbManager, utils=utils, conn_sqlalchemy=self.conn_sqlalchemy)
        container.add_singleton(FoodLogRepository, conn_psycopg=self.conn_psycopg)
        return container

    def run(self):
        container = self.register_services()
        db_manager: DbManager = container.get_instance("DbManager")
        food_log_repository: FoodLogRepository = container.get_instance("FoodLogRepository")

        db_manager.configure_database()
        seed_data(food_log_repository)

        install()
        console = Console()

        console.print("Nutrition Tracker", style="bold red")


if __name__ == '__main__':
    App().run()
