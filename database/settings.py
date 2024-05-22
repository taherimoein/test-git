from mysql.connector import Error
from mysql import connector
import json


def insert_query(dbConfig, query):
    connection = None
    try:
        connection = connector.connect(
            db=dbConfig['name'],
            user=dbConfig['user'],
            passwd=dbConfig['password'],
            host=dbConfig['host'],
            port=dbConfig['port']
        )

        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        
        cursor.close()

        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if connection is not None:
            connection.close()


def select_query(dbConfig, query):
    connection = None
    try:
        connection = connector.connect(
            db=dbConfig['name'],
            user=dbConfig['user'],
            passwd=dbConfig['password'],
            host=dbConfig['host'],
            port=dbConfig['port']
        )

        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        
        cursor.close()

        return True, None, data
    except Exception as e:
        return False, str(e), None
    finally:
        if connection is not None:
            connection.close()

