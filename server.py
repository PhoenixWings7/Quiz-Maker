import os
from flask import Flask, render_template, request, redirect, url_for, flash
import data_handler
import user_functions

app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret! The app doesn't work without it.
app.secret_key = os.urandom(24)

TEMPLATES_ROUTES = {"main_page": "main.html",
                    "leaderboard": "leaderboard.html",
                    "new quiz start": "new_quiz.html",
                    "next question form": "next_question.html",
                    "quiz list": "quiz_list.html",
                    "sign_up": "sign_up.html",
                    "user page": "user_page.html"}

VALIDATION_MESSAGES = {"invalid title": '''Your title includes some special signs. You're only allowed to use
                                            letters and spaces. Try again!''',
                       "title not unique": '''There's already a quiz with that title! Try again.''',
                       "user not in database": '''You entered a wrong name or you aren't a Quiz Maker user. 
                                                    Try again or sign up!''',
                       "no user logged in": '''You're not logged in. Log in and try again.''',
                       "user already in database": '''Your login or email wasn't unique. Try again or log in.'''}


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


@app.route('/<username>/details')
def user_page(username=None):
    if (username != user_functions.user_logged_in()) or (username is None):
        flash(VALIDATION_MESSAGES["no user logged in"])
        return redirect(url_for("main_page"))
    user_info = data_handler.get_user_data(username)
    return render_template(TEMPLATES_ROUTES["user page"], user_info=user_info, username=username)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
