import mysql.connector
from myenv import Myenv

class Db:

    def __init__(self):
        self._init_connection()

    def _init_connection(self):
        self.connection = mysql.connector.connect(
            user=Myenv.DB_USER,
            password=Myenv.DB_PASSWORD,
            host=Myenv.DB_HOST,
            database=Myenv.DB_DATABASE)

    def _destroy_connection(self):
        self.connection.close()

    def _rows(self, q, is_dictionary=True):
        cursor = self.connection.cursor(dictionary=is_dictionary)
        cursor.execute(q)
        rows = [row for row in cursor]
        self.connection.commit()
        cursor.close()
        return rows

    def get_html_ids(self):
        print(self._rows('select id from amazonproductlandingpageraw limit 1'))

    def execute_query(self, q):
        return self._rows(q)
