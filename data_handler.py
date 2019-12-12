import psycopg2, psycopg2.extras, psycopg2.errors

import db_connection
from user_functions import hash_password_with_salt

NUM_OF_POSSIBLE_ANSW = 4


def create_answer_names():
    '''
    Create dictionary labels for one correct answer and a few possible answers ("answer_1", "answer_2"...) for a form
    :return: list of string labels
    '''
    answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, NUM_OF_POSSIBLE_ANSW + 1)]
    answer_names = ["correct_answer"] + answer_ids
    return answer_names


def create_data_headers():
    '''
    Create dictionary labels with question label for a form
    :return: list of string labels
    '''

    data_headers = ["question"] + ANSWER_NAMES
    return data_headers


ANSWER_NAMES = create_answer_names()
DATA_HEADERS = create_data_headers()


def validate_title(title):
    '''
    Checks if title is just letters and spaces
    :param title:
    :return: True or False
    '''
    return title.replace(" ", "").isalpha()


@db_connection.connection_handler
def get_quiz_id(cursor, title):
    statement_str = "SELECT quiz_id FROM quiz_titles WHERE title = %(title)s"
    cursor.execute(statement_str, {"title": title})
    quiz_id = cursor.fetchone()['quiz_id']

    return quiz_id


@db_connection.connection_handler
def get_question_id(cursor, quiz_id):
    statement_str = "SELECT question_id FROM quiz_questions WHERE quiz_id = %(quiz_id)s"
    cursor.execute(statement_str, {"quiz_id": quiz_id})
    question_id = cursor.fetchone()['question_id']

    return question_id


@db_connection.connection_handler
def get_user_id(cursor, username):
    statement_str = '''SELECT user_id FROM users WHERE username = %(username)s'''
    cursor.execute(statement_str, {"username": username})
    try:
        user_id = cursor.fetchone()['user_id']
    except TypeError:
        return

    return user_id


@db_connection.connection_handler
def add_quiz_title_to_database(cursor, title, user_id):
    try:
        statement_str = "INSERT INTO quiz_titles VALUES (DEFAULT , %(title)s, %(user_id)s)"
        cursor.execute(statement_str, {"title": title, "user_id": user_id})
    except psycopg2.errors.UniqueViolation:
        return False
    return True


@db_connection.connection_handler
def add_question_to_database(cursor, question, quiz_id):
    statement_str = '''INSERT INTO quiz_questions 
                        VALUES (DEFAULT, %(question)s, %(quiz_id)s)'''
    cursor.execute(statement_str, {"question": question, "quiz_id": quiz_id})
    return


@db_connection.connection_handler
def add_answers_to_db(cursor, question_data, quiz_id):
    question_id = get_question_id(quiz_id)

    for answer_name in ANSWER_NAMES:
        answer = question_data[answer_name]
        is_correct = (answer_name == 'correct_answer')
        statement_str = '''INSERT INTO answers 
        VALUES (DEFAULT, %(answer)s, %(is_correct)s, %(question_id)s)'''

        cursor.execute(statement_str, {'answer': answer, 'is_correct': is_correct,
                                       'question_id': question_id})
    return


@db_connection.connection_handler
def get_quiz_titles_list_from_db(cursor):
    '''Returns list of dictionaries with keys: "quiz_id" and "question"'''
    statement_str = '''SELECT quiz_id, title FROM quiz_titles'''
    cursor.execute(statement_str)
    quiz_titles = cursor.fetchall()
    return quiz_titles


@db_connection.connection_handler
def get_questions_list_from_db(cursor, quiz_id):
    statement_str = '''SELECT question_id, question FROM quiz_questions 
                        WHERE quiz_id = %(quiz_id)s'''
    cursor.execute(statement_str, {"quiz_id": quiz_id})
    questions = cursor.fetchall()
    return questions


@db_connection.connection_handler
def get_user_hashed_password(cursor, username):
    statement_str = '''SELECT password FROM users WHERE username = %(username)s'''
    cursor.execute(statement_str, {'username': username})
    try:
        user_hashed_password = cursor.fetchone()['password']
    except TypeError:
        return

    return user_hashed_password


@db_connection.connection_handler
def get_password_salt(cursor, username):
    statement_str = '''SELECT salt FROM users WHERE username = %(username)s'''
    cursor.execute(statement_str, {'username': username})

    salt = cursor.fetchone()['salt']
    return salt


@db_connection.connection_handler
def user_sign_up(cursor, user_data):
    salt, user_data['password'] = hash_password_with_salt(user_data['password'])

    try:
        statement_str = '''INSERT INTO users VALUES (DEFAULT, %(username)s, %(nickname)s, %(password)s,
         %(salt)s, %(email)s, %(user_age)s, %(user_gender)s, %(photo_link)s, %(biography)s)'''

        cursor.execute(statement_str, {'username': user_data['username'], 'nickname': user_data['nickname'],
                                       'password': user_data['password'], 'salt': salt, 'email': user_data['email'],
                                       'user_age': user_data['user_age'], 'user_gender': user_data['user_gender'],
                                       'photo_link': user_data['photo_link'], 'biography': user_data['biography']})
    except psycopg2.errors.UniqueViolation:
        return False


@db_connection.connection_handler
def get_user_data(cursor, username):
    query = '''SELECT username, nickname, email, user_age AS age, user_gender AS gender, biography AS "about me"
    FROM users WHERE username = %(username)s'''
    cursor.execute(query, {'username': username})
    results = cursor.fetchall()
    return results


@db_connection.connection_handler
def get_answers_for_question(cursor, question_id):
    statement_str = '''SELECT answer_id, answer FROM answers
                        WHERE question_id = %(question_id)s'''
    cursor.execute(statement_str, {"question_id": question_id})
    answers = cursor.fetchall()
    return answers


def get_questions_and_answers(quiz_id):
    data = get_questions_list_from_db(quiz_id)
    for dict_index in range(len(data)):
        question_id = data[dict_index]["question_id"]
        answers = get_answers_for_question(question_id)
        data[dict_index]["answers"] = answers
    return data


@db_connection.connection_handler
def get_correct_answers(cursor, quiz_id):
    statement_str = '''SELECT answers.question_id, answers.answer_id FROM answers 
                        JOIN (SELECT question_id FROM quiz_questions WHERE quiz_id = %(quiz_id)s) questions_ids 
                        ON questions_ids.question_id = answers.question_id
                        WHERE is_correct = TRUE'''
    cursor.execute(statement_str, {"quiz_id": quiz_id})
    correct_answers = cursor.fetchall()
    return correct_answers