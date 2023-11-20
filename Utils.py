
class Utils:
    def __init__(self, **kwargs):
        self.conn_psycopg = kwargs["conn_psycopg"]
        self.cursor = self.conn_psycopg.cursor()

    def run_sql(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.conn_psycopg.commit()
        except Exception as e:
            print("run_sql error: ", e)
            self.conn_psycopg.rollback()
        else:
            print("SQL executed successfully")

    def run_sql_file(self, file_path: str):
        with open(file_path, "r") as f:
            sql = f.read()
            self.run_sql(sql)

    def run_proc(self, proc_name: str, args: tuple):
        try:
            self.cursor.callproc(proc_name, args)
            self.conn_psycopg.commit()
        except Exception as e:
            print(e)
            self.conn_psycopg.rollback()
        else:
            print(f"Procedure {proc_name} executed successfully")

    def is_empty(self, table_name: str) -> bool:
        sql = f"SELECT EXISTS (SELECT 1 FROM {table_name})"
        self.cursor.execute(sql)
        return not self.cursor.fetchone()[0]