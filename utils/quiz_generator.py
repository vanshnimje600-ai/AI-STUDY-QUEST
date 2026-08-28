import json
import random
import os


# ============================================================
# PROJECT BASE FOLDER
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# QUESTION BANK FILES
# ============================================================

QUESTION_FILES = {

    "C Programming":
        "c_programming_questions.json",

    "C++":
        "cpp_questions.json",

    "Python":
        "python_questions.json",

    "Data Structures":
        "data_structure_questions.json",

    "Aptitude":
        "aptitude_questions_300.json",

    "Java":
        "java_questions.json",

    "DBMS":
        "dbms_questions.json",

    "Operating System":
        "operating_system_questions.json",

    # Files baad me banayenge
    "Computer Networks":
        "computer_network_questions.json",

    "AI & ML":
        "ai_ml_questions.json"
}


# ============================================================
# GET QUESTIONS
# ============================================================

def get_questions(subject, difficulty):

    try:

        # ----------------------------------------------------
        # CHECK SUBJECT
        # ----------------------------------------------------

        if subject not in QUESTION_FILES:

            print(
                f"No question bank configured for: {subject}"
            )

            return None


        # ----------------------------------------------------
        # GET FILE NAME
        # ----------------------------------------------------

        file_name = QUESTION_FILES[subject]

        file_path = os.path.join(
            BASE_DIR,
            file_name
        )


        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if not os.path.exists(file_path):

            print(
                f"Question bank file not found: {file_path}"
            )

            return None


        # ----------------------------------------------------
        # LOAD JSON
        # ----------------------------------------------------

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        # ----------------------------------------------------
        # SUPPORT DIFFERENT JSON FORMATS
        # ----------------------------------------------------

        questions = []


        # Format 1:
        # {
        #   "questions": [...]
        # }

        if isinstance(data, dict) and "questions" in data:

            questions = data["questions"]


        # Format 2:
        # {
        #   "Subject": {
        #       "Easy": [...]
        #   }
        # }

        elif (
            isinstance(data, dict)
            and subject in data
            and isinstance(data[subject], dict)
        ):

            if difficulty in data[subject]:

                questions = data[subject][difficulty]

            else:

                print(
                    f"Difficulty '{difficulty}' "
                    f"not found for {subject}"
                )

                return None


        # Format 3:
        # Direct list

        elif isinstance(data, list):

            questions = data


        else:

            print(
                f"Unsupported JSON format for {subject}"
            )

            return None


        # ----------------------------------------------------
        # CHECK QUESTIONS
        # ----------------------------------------------------

        if not questions:

            print(
                f"No questions available for "
                f"{subject}"
            )

            return None


        # ----------------------------------------------------
        # FILTER BY DIFFICULTY
        # ----------------------------------------------------

        difficulty_questions = [

            q for q in questions

            if isinstance(q, dict)
            and q.get("difficulty", "").lower()
            == difficulty.lower()

        ]


        # ----------------------------------------------------
        # IF DIFFICULTY EXISTS
        # ----------------------------------------------------

        if difficulty_questions:

            questions = difficulty_questions


        # ----------------------------------------------------
        # VALIDATE QUESTIONS
        # ----------------------------------------------------

        valid_questions = []


        for q in questions:

            if not isinstance(q, dict):
                continue


            if "question" not in q:
                continue


            if "options" not in q:
                continue


            if not isinstance(q["options"], list):
                continue


            if len(q["options"]) < 4:
                continue


            valid_questions.append(q)


        # ----------------------------------------------------
        # NO VALID QUESTIONS
        # ----------------------------------------------------

        if not valid_questions:

            print(
                f"No valid questions found for "
                f"{subject} - {difficulty}"
            )

            return None


        # ----------------------------------------------------
        # RANDOM 10 QUESTIONS
        # ----------------------------------------------------

        number_of_questions = min(
            10,
            len(valid_questions)
        )


        selected_questions = random.sample(
            valid_questions,
            number_of_questions
        )


        # ----------------------------------------------------
        # SHUFFLE OPTIONS
        # ----------------------------------------------------

        for question in selected_questions:

            random.shuffle(
                question["options"]
            )


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        print(
            f"Loaded {len(selected_questions)} "
            f"questions for "
            f"{subject} - {difficulty}"
        )


        return selected_questions


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except FileNotFoundError:

        print(
            f"Question bank file not found "
            f"for {subject}"
        )

        return None


    except json.JSONDecodeError as e:

        print(
            f"Invalid JSON file for {subject}"
        )

        print(
            f"JSON Error: {e}"
        )

        return None


    except Exception as e:

        print(
            f"Question Bank Error: {e}"
        )

        return None