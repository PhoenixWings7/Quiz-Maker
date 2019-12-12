import os, secrets
import data_handler
import user_functions
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret! The app doesn't work without it.
app.secret_key = os.urandom(24)

TEMPLATES_ROUTES = {"main_page": "main.html",
                    "leaderboard": "leaderboard.html",
                    "new quiz start": "new_quiz.html",
                    "next question form": "next_question.html",
                    "quiz list": "quiz_list.html",
                    "sign_up": "sign_up.html",
                    "user page": "user_page.html",
                    "account": "account.html"}

VALIDATION_MESSAGES = {"invalid title": '''Your title includes some special signs. You're only allowed to use
                                            letters and spaces. Try again!''',
                       "title not unique": '''There's already a quiz with that title! Try again.''',
                       "user not in database": '''You entered a wrong name or you aren't a Quiz Maker user. 
                                                    Try again or sign up!''',
                       "no user logged in": '''You're not logged in. Log in and try again.''',
                       "user already in database": '''Your login or email wasn't unique. Try again or log in.''',
                       "username taken": '''The username you chose is already taken, choose another one'''}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/profile_pictures') # photos will be stored here
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER   # SET THE CONFIGURATIONS FOR ACCEPTING FILES


# these functions require app which i can't import due to circular references
def check_photo_extension(filename: 'photo\'s file name from the profile page') -> 'True for yes otherwise False':
    """
    this function takes in the file uploaded and checks if it's extension is in the allowed set of
    extensions declared in the program
    """
    _, file_ext = os.path.splitext(filename)
    # remove the dot from the extension
    file_ext = file_ext.replace('.', "")
    return file_ext in ALLOWED_EXTENSIONS


def save_picture(form_photo: 'file object: a photo uploaded from a form') -> 'name of the photo to use in the database':
    """
    this function takes a photo uploaded by the user, renames it to a random 8 bit hex digits to avoid name collisions
    resizes the photo to save on speed and space, saves the photo in the folder static/profile_pictures and returns
    the name of the photo as we shall use it to get the appropriate photo assigned to user.
    """
    # renaming the photo
    random_hex_name = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_photo.filename)
    photo_name = random_hex_name + file_extension
    # making the path to the folder to save the photo in
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_name)
    # resizing the photo
    photo_size = (300, 300) # pixels
    created_image = Image.open(form_photo)
    created_image.thumbnail(photo_size, Image.ANTIALIAS)
    # saving the photo
    created_image.save(photo_path)
    return photo_name


@app.route('/', methods=["GET"])
def main_page():
    if request.method == "GET":
        username = user_functions.user_logged_in()
        return render_template(TEMPLATES_ROUTES["main_page"], username=username)


@app.route('/sign_up', methods=["GET", "POST"])
def sign_up():
    story_to_edit = {}
    if request.method == "GET":
        pass

    if request.method == "POST":
        user_data = dict(request.form)
        sign_up_successful = data_handler.user_sign_up(user_data)
        if not sign_up_successful:
            flash(VALIDATION_MESSAGES["user already in database"])
            return redirect(url_for("main_page"))

    return render_template(TEMPLATES_ROUTES["sign_up"], story_to_edit=story_to_edit)


@app.route('/log-in', methods=["POST"])
def log_in():
    username = request.form['username']
    entered_password = request.form['password']

    db_password = data_handler.get_user_hashed_password(username)
    if db_password:
        # retrieved password is memoryview so it has to be converted to bytes before hashing it in log_in function
        user_password = db_password.tobytes()

        is_logged_in = user_functions.log_in(username, entered_password, user_password)
        if not is_logged_in:
            flash(VALIDATION_MESSAGES["user not in database"])
    else:
        flash(VALIDATION_MESSAGES["user not in database"])

    return redirect(url_for("main_page"))


@app.route('/log-out', methods=["GET"])
def log_out():
    user_functions.log_out()
    # if request method is "GET", you can find your form data only in request.args.get not in request.form
    original_url = request.args.get('original url')
    if original_url == "user_page":
        flash(VALIDATION_MESSAGES["no user logged in"])
        return redirect(url_for("main_page"))
    return redirect(url_for(original_url))


@app.route('/new-quiz', methods=["GET", "POST"])
def new_quiz_route():
    if request.method == "GET":
        username = user_functions.user_logged_in()
        if not username:
            flash(VALIDATION_MESSAGES["no user logged in"])
            return redirect(url_for("main_page"))
        answer_ids = data_handler.ANSWER_NAMES
        return render_template(TEMPLATES_ROUTES["new quiz start"], answer_ids=answer_ids, username=username)

    if request.method == "POST":
        quiz_title = request.form["quiz_title"]

        username = user_functions.user_logged_in()
        if not username:
            flash(VALIDATION_MESSAGES["no user logged in"])
            return redirect(url_for("main_page"))

        if not data_handler.validate_title(quiz_title):
            flash(VALIDATION_MESSAGES["invalid title"])
            return redirect(url_for("new_quiz_route"))

        user_id = data_handler.get_user_id(username)
        if not user_id:
            flash(VALIDATION_MESSAGES["user not in database"])
            return redirect(url_for("main_page"))
        title_uniqueness_validation = data_handler.add_quiz_title_to_database(quiz_title, user_id)

        if not title_uniqueness_validation:
            flash(VALIDATION_MESSAGES["title not unique"])
            return redirect(url_for("new_quiz_route"))

        quiz_id = data_handler.get_quiz_id(quiz_title)

        return redirect(url_for("next_question_form", quiz_title=quiz_title, quiz_id=quiz_id))


@app.route('/new-quiz-next/<quiz_id>', methods=["GET", "POST"])
def next_question_form(quiz_id):
    if request.method == "GET":
        answer_ids = data_handler.ANSWER_NAMES
        return render_template(TEMPLATES_ROUTES["next question form"],
                               answer_ids=answer_ids,
                               quiz_id=quiz_id)

    if request.method == "POST":
        question = request.form["question"]

        data_handler.add_question_to_database(question, quiz_id)

        question_data = dict(request.form)
        question_data.pop("quiz_title")
        data_handler.add_answers_to_db(question_data, quiz_id)

        answer_ids = data_handler.ANSWER_NAMES
        return render_template(TEMPLATES_ROUTES["next question form"],
                               answer_ids=answer_ids, quiz_id=quiz_id)


@app.route('/quiz-list', methods=["GET"])
def quiz_list():
    if request.method == "GET":
        username = user_functions.user_logged_in()
        quiz_list = data_handler.get_quiz_titles_list_from_db()
        return render_template(TEMPLATES_ROUTES["quiz list"], username=username, quiz_list=quiz_list)


@app.route('/<username>/', methods=['GET', 'POST'])
def user_page(username=None):
    if (username != user_functions.user_logged_in()) or (username is None):
        flash(VALIDATION_MESSAGES["no user logged in"])
        return redirect(url_for("main_page"))
    else:
        photo_name = data_handler.get_photo_name_from_db(username)['photo_link']  # data_handler.(username)  # get the photo
        filepath = url_for('static', filename=f'profile_pictures/{photo_name}')
        old_user_data = data_handler.get_user_data(username)
        if request.method == 'POST':
            new_user_data = dict(request.form)
            if new_user_data['username'] != old_user_data['username']:
                # new user name --> check availability --> update changes
                if data_handler.check_if_username_available(new_user_data['username']):
                    user_functions.update_details(old_user_data, new_user_data)
                    # remove the old invalid as of now username
                    session.pop('username', None)
                    # open a session for the new username, no need to redirect to log in
                    user_functions.set_session_var('username', new_user_data['username'])
                    return redirect(url_for('user_page', username=new_user_data['username']))
                else: # username is not available
                    flash(VALIDATION_MESSAGES["username taken"])
                    return redirect(url_for('user_page', username=username))
            else:
                # username unchanged, others may have changed or not, call the function to update just incase it did
                user_functions.update_details(old_user_data, new_user_data)
                return redirect(url_for('user_page', username=new_user_data['username']))
        elif request.method == 'GET':
            return render_template(TEMPLATES_ROUTES["account"], old_user_data=old_user_data,
                                   filepath=filepath, username=username)


@app.route('/<username>/profile-picture-upload', methods=['GET','POST'])
def profile_picture_upload(username):
    if (username != user_functions.user_logged_in()) or (username is None):
        flash(VALIDATION_MESSAGES["no user logged in"])
        return redirect(url_for("main_page"))

    photo_name = data_handler.get_photo_name_from_db(username)['photo_link']  # data_handler.(username)  # get the photo
    print(photo_name)
    filepath = url_for('static', filename=f'profile_pictures/{photo_name}')
    print(filepath)

    if request.method == 'GET':
        return render_template('profile_picture.html', filepath=filepath)

    elif request.method == 'POST':
        file = request.files['image']
        # CHECK FOR THE PHOTO
        if file:
            if check_photo_extension(file.filename): # CHECK THE EXTENSION
                # SAVE THE PHOTO IF EXTENSION ALLOWED
                photo_name = save_picture(file)
                # LINK TO DATABASE
                data_handler.update_photo_name_in_db(photo_name, username)
                # CREATE FILE PATH
                # filepath = url_for('static', filename=f'profile_pictures/{photo_name}')
                return redirect(url_for('user_page', username = username))

            else: # EXTENSION NOT ALLOWED
                flash('please choose a correct file with the correct extension')
                return render_template('profile_picture.html', filepath=filepath)

        else: # PHOTO WASN'T DETECTED
            flash('No file was uploaded')
            return render_template('profile_picture.html', filepath=filepath)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
