from flask import session

def user_logged_in():
    '''
    Check if any user is logged in and return his/her username. If not logged in, return None.
    '''
    if 'username' in session:
        return session['username']
    else:
        return


def log_in(username, password):
    pass


def log_out(username):
    pass