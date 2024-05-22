from .settings import select_query, insert_query
from utils.base_fuction import get_week_date_range
import environ,random,string,json

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


def get_screening_hall(screeningID):
    # get screening hall
    getScreeningHallQuery = f"""SELECT hall FROM dashboard_screening WHERE id = {screeningID};"""
    # select query
    selectStatus, error, result = select_query(dbConfig, getScreeningHallQuery)

    if selectStatus:
        return json.loads(result[0][0])
    else:
        return None


def get_chair_status(screeningID, chairID):
    # get screening hall
    getScreeningHallQuery = f"""SELECT hall FROM dashboard_screening WHERE id = {screeningID};"""
    # select query
    selectStatus, error, result = select_query(dbConfig, getScreeningHallQuery)

    if selectStatus:
        screeningHallJson = json.loads(result[0][0])
        for chair in screeningHallJson['list']:
            if chair['id'] == chairID:
                return chair['status']
    else:
        return None


def reserve_chair(programID, field):
    # get program field
    getProgramFieldQuery = f"""SELECT {field} FROM dashboard_program WHERE id = {programID};"""
    # select query
    selectStatus, error, result = select_query(dbConfig, getProgramFieldQuery)

    if selectStatus:        
        return result[0][0]
    else:
        return None
    