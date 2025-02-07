import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from app.config import log_config

logger = log_config()

load_dotenv(override=True)

def connect_to_database():
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            user="postgres",
            host="localhost",
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT")
        )

        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        logger.info("Conectado: %s", cursor.fetchone())

    except (Exception, psycopg2.Error) as e:
        logger.error("Erro ao conectar-se ao Postgres: %s", e)
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        return None, None

    return cursor, connection
    
    
def create_table(table_name, columns):
    cursor, connection = connect_to_database()

    if not cursor or not connection:
        logger.error("Conexão falhou. Tabela não criada")
        return

    query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join([sql.SQL(column) for column in columns])
    )

    query_string = query.as_string(connection)
    logger.info("Criando tabela %s. Query: %s", table_name, query_string)

    try:
        cursor.execute(query)
        connection.commit()
    
    except (Exception, psycopg2.Error) as error:
        logger.error("Erro ao criar '%s': %s", table_name, error)
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def insert_values(table_name, rows):
    """
    rows deve ser uma lista de listas
    """
    cursor, connection = connect_to_database()

    if not cursor or not connection:
        logger.error("Não foi possível inserir valores na tabela pois a conexão falhou.")
        return
    
    rows_sql = []
    for row in rows:
        row_sql = sql.SQL('(DEFAULT,') + sql.SQL(', ').join(sql.Literal(v) for v in row) + sql.SQL(')')
        rows_sql.append(row_sql)

    all_values_sql = sql.SQL(', ').join(rows_sql)

    query = sql.SQL("INSERT INTO {} VALUES {}").format(
        sql.Identifier(table_name),
        all_values_sql
    )

    query_string = query.as_string(connection)
    logger.info("Inserindo valores na tabela '%s' com a query: %s", table_name, query_string)

    try:
        cursor.execute(query)
        connection.commit()
        logger.info("Inserção concluída com sucesso.")
    except (Exception, psycopg2.Error) as error:
        logger.error("Erro ao inserir valores na tabela '%s': %s", table_name, error)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()