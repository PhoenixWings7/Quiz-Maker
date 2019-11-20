import os

import psycopg2, psycopg2.extras, psycopg2.errors


def create_connection_string():
    db_url = os.environ.get("DATABASE_URL")

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
