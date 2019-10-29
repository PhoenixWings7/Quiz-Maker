from flask import Flask, render_template, request, redirect, url_for, flash
import data_handler

app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret! The app doesn't work without it.
app.secret_key = b'_5#y2L"F4Quwsn/uwsj]/'

TEMPLATES_ROUTES = {"main_page" : "main.html",
                    "leaderboard" : "leaderboard.html",
                    "new quiz start" : "new_quiz.html",
                    "next question form" : "next_question.html",
                    "quiz list" : "quiz_list.html"}

VALIDATION_MESSAGES = {"invalid title" : '''Your title includes some special signs. You're only allowed to use
                                            letters and spaces. Try again!''',
                       "title not unique" : '''There's already a quiz with that title! Try again.'''}



@app.route('/', methods=["GET", "POST"])
def main_page():
    return render_template(TEMPLATES_ROUTES["main_page"])


@app.route('/new-quiz', methods = ["GET", "POST"])
def new_quiz_route():
    if request.method == "GET":
        answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, data_handler.NUM_OF_QUESTIONS + 1)]
        return render_template(TEMPLATES_ROUTES["new quiz start"], answer_ids = answer_ids)

    if request.method == "POST":
        quiz_title = request.form["quiz_title"]
        if not data_handler.validate_title(quiz_title):
            flash(VALIDATION_MESSAGES["invalid title"])
            return redirect(url_for("new_quiz_route"))
        id_ = data_handler.get_new_id()
        filename = "abdc7"
        title_uniqueness_validation = data_handler.add_quiz_title_to_database(id_, quiz_title, filename)
        if not title_uniqueness_validation:
            flash(VALIDATION_MESSAGES["title not unique"])
            return redirect(url_for("new_quiz_route"))
        data_handler.create_new_db_table(filename)
        return redirect(url_for("next_question_form", quiz_title = quiz_title))


@app.route('/new-quiz-next/<quiz_title>', methods = ["GET", "POST"])
def next_question_form(quiz_title=None):
    if request.method == "GET":
        answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, data_handler.NUM_OF_QUESTIONS + 1)]
        return render_template(TEMPLATES_ROUTES["next question form"],
                               answer_ids = answer_ids,
                               quiz_title = quiz_title)

    if request.method == "POST":
        quiz_title = request.form["quiz_title"]
        question_data = dict(request.form)
        question_data.pop("quiz_title")
        data_handler.add_question_to_file(question_data, quiz_title)
        answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, data_handler.NUM_OF_QUESTIONS + 1)]
        return render_template(TEMPLATES_ROUTES["next question form"], answer_ids = answer_ids, quiz_title = quiz_title)


@app.route('/quiz-list', methods = ["GET"])
def quiz_list():
    if request.method == "GET":
        return render_template(TEMPLATES_ROUTES["quiz list"])


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )