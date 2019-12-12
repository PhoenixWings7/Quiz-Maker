from flask import session
from PIL import Image
import bcrypt, data_handler
import os, secrets

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def user_logged_in():
    '''
    Check if any user is logged in and return his/her username. If not logged in, return None.
    :return string or None
    '''
    if 'username' in session:
        return session['username']
    else:
        return


def generate_salt():
    return bcrypt.gensalt()


def hash_password_with_salt(password, salt=generate_salt()):
    '''
    Hashes password using random salt
    :param password:
    :return: salt, hashed_password
    '''
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return salt, hashed_password


def set_session_var(var, value):
    session[var] = value


def log_in(username, input_password, user_password):
    '''
    Logs the user in.
    :param input_password:
    :return: True if password correct, False if incorrect
    '''
    input_password = bytes(input_password, 'utf-8')
    login_successful = bcrypt.checkpw(input_password, user_password)
    if login_successful:
        set_session_var('username', username)

    return login_successful


def log_out():
    # None after the comma prevents KeyError from happening if there's no username in session
    session.pop('username', None)


def update_details(old_user_data, new_user_data):
    data_handler.update_db(
        old_user_data['username'],
        new_user_data['username'],
        new_user_data['email'],
        new_user_data['biography'],
        new_user_data['nickname'])


def check_photo_extension(filename: 'photo\'s file name from the profile page') -> 'True for yes otherwise False':
    """
    this function takes in the file uploaded and checks if it's extension is in the allowed set of
    extensions declared in the program
    """
    _, file_ext = os.path.splitext(filename)
    # remove the dot from the extension
    file_ext = file_ext.replace('.', "")
    return file_ext in ALLOWED_EXTENSIONS


def save_picture(form_photo: 'file object: a photo uploaded from a form',
                 location: 'where the files are stored') -> 'name of the photo to use in the database':
    """
    this function takes a photo uploaded by the user, renames it to a random 8 bit hex digits to avoid name collisions
    re-sizes the photo to save on speed and space, saves the photo in the folder static/profile_pictures and returns
    the name of the photo as we shall use it to get the appropriate photo assigned to user.
    """
    # renaming the photo
    random_hex_name = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_photo.filename)
    photo_name = random_hex_name + file_extension
    # making the path to the folder to save the photo in
    photo_path = os.path.join(location, photo_name)
    # resizing the photo
    photo_size = (150, 150)  # pixels
    created_image = Image.open(form_photo)
    created_image = created_image.resize(photo_size)
    # created_image.thumbnail(photo_size, Image.ANTIALIAS)
    # saving the photo
    created_image.save(photo_path)
    return photo_name
