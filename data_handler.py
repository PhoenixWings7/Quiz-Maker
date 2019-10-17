import csv

NUM_OF_QUESTIONS = 4
def create_data_headers():
    answer_ids = ["answer_" + str(ord_num) for ord_num in range(2, NUM_OF_QUESTIONS + 1)]
    data_headers = ["question", "correct_answer"] + answer_ids
    return data_headers


DATA_HEADERS = create_data_headers()


def create_new_csv_file(filename, headers=DATA_HEADERS):
    with open(filename, "w") as file:
        data_dict = csv.DictWriter(file, headers)
        data_dict.writeheader()
    return


def create_new_quiz_file(quiz_data, quiz_title):
    filename = quiz_title.lower()
    create_new_csv_file(filename, DATA_HEADERS)
    with open(filename, "a") as file:
        data = csv.DictWriter(file, DATA_HEADERS)
        data.writerow(quiz_data)
    return


def save_dict_data_to_file(filename, dict_data):
    with open(filename, "a") as file:
        data = csv.DictWriter(file, DATA_HEADERS)
        data.writerow(dict_data)
    return


def add_question_to_file(question_data, quiz_title):
    filename = quiz_title.lower()
    try:
        save_dict_data_to_file(filename, question_data)
    except FileNotFoundError:
        create_new_quiz_file(question_data, quiz_title)
    return