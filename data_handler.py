import psycopg2, psycopg2.extras, os

NUM_OF_QUESTIONS = 4

def create_data_headers():
    answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, NUM_OF_QUESTIONS + 1)]
    data_headers = ["question", "correct_answer"] + answer_ids
    return data_headers


DATA_HEADERS = create_data_headers()


def create_data_headers_and_data_sort_dict():
    headers_dict = {}
    for header in DATA_HEADERS:
        headers_dict[header] = "TEXT NOT NULL"
    return headers_dict


def create_database_column_titles():
    headers_dict = create_data_headers_and_data_sort_dict()
    column_titles = ""
    for header in DATA_HEADERS:
        column_titles+=header + " " + headers_dict[header]
        if header == DATA_HEADERS[-1]:
            return column_titles
        column_titles+=", "
    return column_titles


def validate_title(title):
    if title.replace(" ", "").isalpha():
        return True
    else:
        return False


def create_connection_string():
    user_name = os.environ.get("PSQL_USER_NAME")
    password = os.environ.get("PSQL_PASSWORD")
    host = os.environ.get("PSQL_HOST")
    database_name = os.environ.get("PSQL_DB_NAME")

    env_var_defined = user_name and password and host and database_name

    if env_var_defined:
        return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
            user_name=user_name,
            password=password,
            host=host,
            database_name=database_name)
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
def get_new_id(cursor, table = "quiz_titles"):
    statement_str = "SELECT MAX(id) FROM {table}".format(table = table)
    cursor.execute(statement_str)
    max_existing_id_num = cursor.fetchone()['max']
    return max_existing_id_num + 1


@connection_handler
def create_new_db_table(cursor, table_name):
    column_titles = create_database_column_titles()
    statement_str = "CREATE TABLE {table_name} ".format(table_name = table_name) + "(" + column_titles + ")"
    cursor.execute(statement_str)
    return


@connection_handler
def add_quiz_title_to_database(cursor, id_, title, filename):
    statement_str = "INSERT INTO quiz_titles VALUES ({}, '{}', '{}')".format(id_, title, filename)
    cursor.execute(statement_str)
    return


def add_question_to_db():
    pass