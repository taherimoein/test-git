from .settings import select_query, insert_query
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


def create_member(userJson):
    # generate invitation code
    invitationCode = generate_invitation_code(6)
    # create member query
    createMemberQuery = f"""INSERT INTO dashboard_member (first_name,last_name,telegram_chat_id,telegram_username,invitation_code,invitation_code_used,createdate) VALUES ('{userJson['first_name']}','{userJson['last_name']}',{userJson['telegram_chat_id']},'{userJson['telegram_username']}','{invitationCode}','{userJson['invitation_code_used']}',NOW());"""
    # insert query
    insertStatus, error = insert_query(dbConfig, createMemberQuery)

    return insertStatus


def check_existence_member(userChatID):
    # check existence member query
    checkExistenceMemberQuery = f"""SELECT EXISTS(SELECT * from dashboard_member WHERE telegram_chat_id={userChatID});"""
    # select query
    selectStatus, error, result = select_query(dbConfig, checkExistenceMemberQuery)

    if selectStatus:
        return selectStatus, bool(result[0][0]), None
    else:
        return selectStatus, None, error


def check_member_block_status(userChatID):
    # check member block status
    checkMemberBlockStatusQuery = f"""SELECT active from dashboard_member WHERE telegram_chat_id={userChatID};"""
    # select query
    selectStatus, error, result = select_query(dbConfig, checkMemberBlockStatusQuery)

    if selectStatus:
        return True, bool(result[0][0]), None
    else:
        return selectStatus, None, error


def check_invitation_code(code):
    # check user have code
    checkUserHaveCodeQuery = f"""SELECT EXISTS(SELECT * from dashboard_member WHERE invitation_code_used IS NULL);"""
    # select query
    selectStatus, error, haveCoderesult = select_query(dbConfig, checkUserHaveCodeQuery)
    # check invitation code
    checkInvitationCodeQuery = f"""SELECT EXISTS(SELECT active from dashboard_member WHERE invitation_code='{code}');"""
    # select query
    selectStatus, error, result = select_query(dbConfig, checkInvitationCodeQuery)

    if selectStatus:
        return True, bool(haveCoderesult[0][0]), bool(result[0][0]), None
    else:
        return selectStatus, None, error


def generate_invitation_code(length):
    # selcet all invitation code
    selectAllInvitationCodeQuery = """SELECT invitation_code FROM dashboard_member;"""
    # select query
    selectStatus, error, result = select_query(dbConfig, selectAllInvitationCodeQuery)

    invitationCodeList = []

    if selectStatus:
        for item in result:
            invitationCodeList.append(item[0])

    characters = string.digits
    code = ''.join(random.choice(characters) for i in range(length))
    while code in invitationCodeList:
        code = ''.join(random.choice(characters) for i in range(length))
    return code
