import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from app.config import log_config

logger = log_config()

load_dotenv(override=True)
        
class Database:
    def __init__(self):
        self.conn = psycopg2.connect(user="postgres",
                                     host="localhost",
                                     password=os.getenv("DB_PASSWORD"),
                                     dbname=os.getenv("DB_NAME"),
                                     port=os.getenv("DB_PORT")
                                    )
        self._cursor = self.conn.cursor()
        self._cursor.execute("SELECT version();")
        logger.info("Conectado: %s", self._cursor.fetchone())
    
    def __enter__(self):
        return self
    
    #bloco with tratando o commit e close
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        self._cursor.close()
        self.conn.close()
    
    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        return self._cursor
    
    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()
    
    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()
    
    def insert_values(self, table_name, columns, rows, logging=False):
            """
            rows deve ser uma lista de listas
            """
            rows_sql = []
            for row in rows:
                row_sql = sql.SQL('(') + sql.SQL(', ').join(sql.Literal(v) for v in row) + sql.SQL(')')
                rows_sql.append(row_sql)

            all_values_sql = sql.SQL(', ').join(rows_sql)

            columns_insert = sql.SQL('(') + sql.SQL(', '.join(columns)) + sql.SQL(')')

            query = sql.SQL("INSERT INTO {} {} VALUES {}").format(
                sql.Identifier(table_name),
                columns_insert,
                all_values_sql
            )
            
            self._cursor.execute(query)

            if logging:
                query_string = query.as_string(self.conn)
                logger.info("Inserido na tabela '%s' com a query: %s", table_name, query_string)

    def create_table(self, table_name, columns, logging=False):
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join([sql.SQL(column) for column in columns])
        )

        if logging:
            query_string = query.as_string(self.conn)
            logger.info("Criando tabela %s. Query: %s", table_name, query_string)

        self._cursor.execute(query)