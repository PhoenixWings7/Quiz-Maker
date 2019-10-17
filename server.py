from flask import Flask, render_template, request, redirect, url_for
import data_handler

app = Flask(__name__)

TEMPLATES_ROUTES = {"main_page" : "main.html",
                    "leaderboard" : "leaderboard.html",
                    "new quiz start" : "new_quiz.html",
                    "next question form" : "next_question.html",
                    "quiz list": "quiz_list.html"}



@app.route('/')
def main_page():
    return render_template(TEMPLATES_ROUTES["main_page"])


@app.route('/new-quiz', methods = ["GET", "POST"])
def new_quiz_route():
    if request.method == "GET":
        answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, data_handler.NUM_OF_QUESTIONS + 1)]
        return render_template(TEMPLATES_ROUTES["new quiz start"], answer_ids = answer_ids)

    if request.method == "POST":
        quiz_title = request.form["quiz_title"]
        question_data = dict(request.form)
        question_data.pop("quiz_title")

        data_handler.add_question_to_file(question_data, quiz_title)
        return redirect(url_for("next_question_form"))


@app.route('/new-quiz-next', methods = ["GET", "POST"])
def next_question_form():
    if request.method == "GET":
        quiz_title =
        answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, data_handler.NUM_OF_QUESTIONS + 1)]
        return render_template(TEMPLATES_ROUTES["next question form"],quiz_title = quiz_title, answer_ids = answer_ids)
    if request.method == "POST":
        answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, data_handler.NUM_OF_QUESTIONS + 1)]
        return render_template(TEMPLATES_ROUTES["next question form"], answer_ids = answer_ids)


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