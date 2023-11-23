import psycopg2

from datetime import date, datetime
from rich import print


class FoodLogRepository:
    def __init__(self, **kwargs) -> None:
        self.conn: psycopg2.connection = kwargs["conn_psycopg"]
        self.cursor = self.conn.cursor()

    def get_daily_nutrients(self, date_info: date) -> list:
        try:
            self.cursor.callproc("select_daily_nutrients", (date_info,))
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            print("Daily nutrients fetched successfully")
            return self.cursor.fetchall()

    def insert_log(self, d_time: datetime, measurement_type: str, quantifier: float, fk_id: int) -> None:
        try:
            self.cursor.callproc("insert_log", (d_time, measurement_type, quantifier, fk_id))
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            print("Log inserted successfully")

    def insert_logs(self, logs: list) -> None:
        for log in logs:
            date_time, measurement_type, _, _ = logs
            try:
                self.cursor.callproc("insert_log", log)
                self.conn.commit()
            except Exception as e:
                print(e, "INVALID LOG date_time: ", date_time, "measurement_type: ", measurement_type)
                self.conn.rollback()
            else:
                print("Log inserted successfully: date_time: ", date_time, "measurement_type: ", measurement_type)

    def get_categories(self) -> list:
        try:
            sql_food_categories = '''SELECT id, description FROM category ORDER BY description;'''
            self.cursor.execute(sql_food_categories)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            print("Food categories fetched successfully")
            return self.cursor.fetchall()

    def get_foods_from_category(self, category_id: int) -> list:
        try:
            self.cursor.execute(f'''SELECT id, name FROM food WHERE category_id = {category_id} ORDER BY name;''')
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            print("Foods fetched successfully")
            return self.cursor.fetchall()
