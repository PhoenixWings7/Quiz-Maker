import os
from flask import session
import bcrypt


def user_logged_in():
    '''
    Check if any user is logged in and return his/her username. If not logged in, return None.
    '''
    if 'username' in session:
        return session['username']
    else:
        return


def generate_salt():
    return bcrypt.gensalt()


def hash_password_with_salt(password, salt = generate_salt()):
    '''
    Hashes password using random salt
    :param password:
    :return: salt, hashed_password
    '''
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return salt, hashed_password


def log_in(input_password, user_password, salt):
    '''
    Logs the user in.
    :param input_password:
    :return: True if password correct, False if incorrect
    '''
    input_password = bytes(input_password, 'utf-8')

    if bcrypt.checkpw(input_password, user_password):
        return True
    else:
        return False


def log_out():
    session.pop('username')