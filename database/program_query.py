from .settings import select_query, insert_query
from utils.base_fuction import get_week_date_range
import environ,random,string

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


def get_week_program():
    # get week start & end date
    weelDate = get_week_date_range()
    # week program
    weekProgramQuery = f"""SELECT dashboard_screening.id as id, dashboard_program.title as title, dashboard_program.image as image, dashboard_program.description as description, dashboard_program.attached_file as attached_file, dashboard_program.teaser as teaser, dashboard_screening.date as date, dashboard_screening.start_time as start_time, dashboard_screening.end_time as end_time, dashboard_screening.status as status, dashboard_screening.fk_program_id as program_id FROM dashboard_screening JOIN dashboard_program ON dashboard_screening.fk_program_id = dashboard_program.id WHERE dashboard_screening.date BETWEEN '{weelDate[0]}' AND '{weelDate[1]}' AND dashboard_screening.publish = 1 ORDER BY dashboard_screening.date ASC;"""
    # select query
    selectStatus, error, result = select_query(dbConfig, weekProgramQuery)

    if selectStatus:
        queryResult = []
        for field in result:
            # create program json
            programJson = {
                'id': field[0],
                'title': field[1],
                'image': field[2],
                'description': field[3],
                'attached_file': field[4],
                'teaser': field[5],
                'date': field[6],
                'start_time': field[7],
                'end_time': field[8],
                'status': field[9],
                'program_id': field[10]
            }
            queryResult.append(programJson)
        
        return queryResult
    else:
        return None


def get_program_field(programID, field):
    # get program field
    getProgramFieldQuery = f"""SELECT {field} FROM dashboard_program WHERE id = {programID};"""
    # select query
    selectStatus, error, result = select_query(dbConfig, getProgramFieldQuery)

    if selectStatus:        
        return result[0][0]
    else:
        return None
    