

from datetime import date, datetime

class FoodLogRepository:
    def __init__(self, **kwargs) -> None:
        self.conn = kwargs["conn_psycopg"]
        self.cursor = self.conn.cursor()

    def get_daily_nutrients(self, date_info: date) -> list:
        try:
            self.cursor.callproc("get_daily_nutrients", date_info)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            print("Daily nutrients fetched successfully")
            return self.cursor.fetchall()

    def insert_log(self, d_time, measurement_type: str, quantifier: float, fk_id: int) -> None:
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
