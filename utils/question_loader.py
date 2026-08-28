import json
import random


def load_questions():

    with open("data/questions.json", "r") as file:
        data = json.load(file)

    return data


def get_questions(subject, difficulty):

    data = load_questions()

    questions = data.get(subject, {}).get(difficulty, [])

    questions = random.sample(questions, min(10, len(questions)))

    return questions