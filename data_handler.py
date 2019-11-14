import psycopg2, psycopg2.extras, psycopg2.errors, os
from user_functions import hash_password_with_salt

NUM_OF_QUESTIONS = 4


def create_answer_names():
    answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, NUM_OF_QUESTIONS + 1)]
    answer_names = ["correct_answer"] + answer_ids
    return answer_names

ANSWER_NAMES = create_answer_names()


def create_data_headers():

    data_headers = ["question"] + ANSWER_NAMES
    return data_headers


DATA_HEADERS = create_data_headers()



def validate_title(title):
    if title.replace(" ", "").isalpha():
        return True
    else:
        return False


def create_connection_string():
    db_url = os.environ.get("DATABASE_URLI")

    env_var_defined = db_url

    if env_var_defined:
        return db_url
    else:
        raise KeyError("Environmental variables not defined!")


def open_database():
    connection_string = create_connection_string()
    connection = psycopg2.connect(connection_string)
    connection.autocommit = True
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value

    return wrapper


@connection_handler
def get_quiz_id(cursor, title):
    statement_str = "SELECT quiz_id FROM quiz_titles WHERE title = %(title)s"
    cursor.execute(statement_str, {"title" : title})
    quiz_id = cursor.fetchone()['quiz_id']

    return quiz_id


@connection_handler
def get_question_id(cursor, quiz_id):
    statement_str = "SELECT question_id FROM quiz_questions WHERE quiz_id = %(quiz_id)s"
    cursor.execute(statement_str, {"quiz_id" : quiz_id})
    question_id = cursor.fetchone()['question_id']

    return question_id


@connection_handler
def add_quiz_title_to_database(cursor, title):
    try:
        statement_str = "INSERT INTO quiz_titles VALUES (DEFAULT , %(title)s)"
        cursor.execute(statement_str, {"title" : title})
    except psycopg2.errors.UniqueViolation:
        return False
    return True


@connection_handler
def add_question_to_database(cursor, question, quiz_id):
    statement_str = '''INSERT INTO quiz_questions 
                        VALUES (DEFAULT, %(question)s, %(quiz_id)s)'''
    cursor.execute(statement_str, {"question" : question, "quiz_id" : quiz_id})
    return


@connection_handler
def add_answers_to_db(cursor, question_data, quiz_id):
    question_id = get_question_id(quiz_id)

    for answer_name in ANSWER_NAMES:
        answer = question_data[answer_name]
        is_correct = (answer_name == 'correct_answer')
        statement_str = '''INSERT INTO answers 
        VALUES (DEFAULT, %(answer)s, %(is_correct)s, %(question_id)s)'''

        cursor.execute(statement_str, {'answer' : answer, 'is_correct' : is_correct,
                                   'question_id' : question_id})
    return


@connection_handler
def get_quiz_titles_list_form_db(cursor):
    statement_str = '''SELECT title FROM quiz_titles'''
    cursor.execute(statement_str)
    quiz_titles = cursor.fetchall()
    quiz_titles = [title['title'] for title in quiz_titles]
    return quiz_titles


@connection_handler
def get_questions_list_from_db(cursor, quiz_id):
    statement_str = '''SELECT question FROM quiz_questions 
                        WHERE question_id = %(quiz_id)s'''
    cursor.execute(statement_str, {"quiz_id" : quiz_id})
    questions = cursor.fetchall()
    questions = [question['question'] for question in questions]
    return questions


@connection_handler
def get_user_hashed_password(cursor, username):
    statement_str = '''SELECT password FROM users WHERE username = %(username)s'''
    cursor.execute(statement_str, {'username' : username})
    try:
        user_hashed_password = cursor.fetchone()['password']
    except TypeError:
        return

    return user_hashed_password


@connection_handler
def get_password_salt(cursor, username):
    statement_str = '''SELECT salt FROM users WHERE username = %(username)s'''
    cursor.execute(statement_str, {'username': username})

    salt = cursor.fetchone()['salt']
    return salt


@connection_handler
def user_sign_up(cursor, user_data):
    salt, user_data['password'] = hash_password_with_salt(user_data['password'])

    statement_str = '''INSERT INTO users VALUES (DEFAULT, %(username)s, %(nickname)s, %(password)s,
     %(salt)s, %(email)s, %(user_age)s, %(user_gender)s, %(photo_link)s, %(biography)s)'''

    cursor.execute(statement_str, {'username' : user_data['username'], 'nickname' : user_data['nickname'],
                                   'password' : user_data['password'], 'salt' : salt, 'email' : user_data['email'],
                                   'user_age' : user_data['user_age'], 'user_gender' : user_data['user_gender'],
                                   'photo_link' : user_data['photo_link'], 'biography' : user_data['biography']})
    return