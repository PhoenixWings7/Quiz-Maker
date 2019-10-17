from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

TEMPLATES_ROUTES = {"main_page" : "main.html",
                    "leaderboard" : "leaderboard.html",
                    "new quiz start" : "new_quiz.html",
                    "new quiz form" : "new_quiz_form.html",
                    "quiz list": "quiz_list.html"}

@app.route('/')
def main_page():
    return render_template(TEMPLATES_ROUTES["main_page"])


@app.route('/new-quiz', methods = ["GET"])
def new_quiz_route():
    if request.method == "GET":
        return render_template(TEMPLATES_ROUTES["new quiz start"])


@app.route('/new-quiz-form', methods = ["GET", "POST"])
def new_quiz_form():
    if request.method == "GET":
        return render_template(TEMPLATES_ROUTES["new quiz form"])
    if request.method == "POST":
        pass


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