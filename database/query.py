from .settings import select_query
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# DataBase Config
dbConfig = {
    'name': env('db_name'),
    'user': env('db_user'),
    'password': env('db_password'),
    'host': env('db_host'),
    'port': env('db_port')
}


# select movies query
select_movies_query = """SELECT * FROM movies;"""

def select_movies():
    # execute query
    executeStatus, error, data = execute_query(dbConfig, select_movies_query)

    if executeStatus:
        queryResult = []
        for field in data:
            # create movie json
            movieJson = {
                'id': field[0],
                'title': field[1],
                'image': field[2],
                'details': field[3],
                'publish': field[4],
                'ctreate_date': field[5]
            }
            queryResult.append(movieJson)
        
        print(queryResult)
        return queryResult
    else:
        return executeStatus, error

