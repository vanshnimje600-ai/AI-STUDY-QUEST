from flask import Flask, render_template, request, session, redirect
import time

from utils.database import (
    create_database,
    register_user,
    login_user,
    save_score,
    get_leaderboard,
    get_history
)

from utils.quiz_generator import get_questions


app = Flask(__name__)

app.secret_key = "AIStudyQuest2026"

create_database()


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = login_user(username, password)

        if user:

            session["username"] = username

            return redirect("/home")

        return "Invalid Username or Password"

    return render_template("login.html")


# ============================================================
# HOME
# ============================================================

@app.route("/home")
def home():

    username = session.get("username")

    if not username:
        return redirect("/")

    return render_template(
        "home.html",
        username=username
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        register_user(
            username,
            email,
            password
        )

        return redirect("/")

    return render_template("register.html")


# ============================================================
# SUBJECTS
# ============================================================

@app.route("/subjects")
def subjects():

    if "username" not in session:
        return redirect("/")

    return render_template("subjects.html")


# ============================================================
# DIFFICULTY
# ============================================================

@app.route("/difficulty", methods=["POST"])
def difficulty():

    subject = request.form.get("subject")

    if not subject:
        return redirect("/subjects")

    return render_template(
        "difficulty.html",
        subject=subject
    )


# ============================================================
# START QUIZ
# ============================================================

@app.route("/start_quiz", methods=["POST"])
def start_quiz():

    try:

        subject = request.form.get("subject")
        difficulty_level = request.form.get("difficulty")

        if not subject or not difficulty_level:
            return redirect("/subjects")


        # ----------------------------------------------------
        # RESET QUIZ DATA
        # ----------------------------------------------------

        session["subject"] = subject
        session["difficulty"] = difficulty_level

        session["score"] = 0
        session["current_question"] = 0
        session["wrong_answers"] = []


        # ----------------------------------------------------
        # LOAD QUESTIONS
        # ----------------------------------------------------

        questions = get_questions(
            subject,
            difficulty_level
        )


        print("SUBJECT:", subject)
        print("DIFFICULTY:", difficulty_level)
        print("QUESTIONS:", questions)


        if not questions:

            return (
                "No questions available for the selected "
                "subject and difficulty."
            )


        session["questions"] = questions


        # ----------------------------------------------------
        # TOTAL QUIZ TIMER
        # ----------------------------------------------------
        # 5 minutes = 300 seconds
        # Timer starts only ONCE when quiz starts.

        session["quiz_start_time"] = time.time()
        session["quiz_time_limit"] = 300


        # ----------------------------------------------------
        # FIRST QUESTION
        # ----------------------------------------------------

        return render_template(
            "quiz.html",
            question=questions[0],
            qno=1,
            total=len(questions),
            subject=subject,
            difficulty=difficulty_level,
            remaining_time=300
        )


    except Exception as e:

        return f"ERROR: {e}"


# ============================================================
# QUIZ
# ============================================================

@app.route("/quiz", methods=["POST"])
def quiz():

    questions_list = session.get(
        "questions",
        []
    )

    current = session.get(
        "current_question",
        0
    )

    score = session.get(
        "score",
        0
    )


    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if not questions_list:

        return redirect("/subjects")


    if current >= len(questions_list):

        return redirect("/result")


    # --------------------------------------------------------
    # TIMER CHECK
    # --------------------------------------------------------

    start_time = session.get(
        "quiz_start_time"
    )

    time_limit = session.get(
        "quiz_time_limit",
        300
    )


    if start_time:

        elapsed_time = (
            time.time() - start_time
        )


        # ----------------------------------------------------
        # TIME OVER
        # ----------------------------------------------------

        if elapsed_time >= time_limit:

            total = len(questions_list)


            save_score(
                session.get("username"),
                score,
                session.get("subject"),
                session.get("difficulty")
            )


            percentage = (
                (score / total) * 100
                if total > 0
                else 0
            )


            return render_template(
                "result.html",
                score=score,
                total=total,
                percentage=round(
                    percentage,
                    2
                ),
                wrong=total - score,
                wrong_answers=session.get(
                    "wrong_answers",
                    []
                )
            )


    # --------------------------------------------------------
    # GET ANSWER
    # --------------------------------------------------------

    selected = request.form.get(
        "answer"
    )


    correct_answer = questions_list[
        current
    ]["answer"]


    # --------------------------------------------------------
    # CHECK ANSWER
    # --------------------------------------------------------

    if selected == correct_answer:

        score += 1

    else:

        wrong_answers = session.get(
            "wrong_answers",
            []
        )


        wrong_answers.append({

            "question":
                questions_list[current]["question"],

            "your_answer":
                selected,

            "correct_answer":
                correct_answer

        })


        session["wrong_answers"] = (
            wrong_answers
        )


    session["score"] = score


    # --------------------------------------------------------
    # MOVE TO NEXT QUESTION
    # --------------------------------------------------------

    current += 1

    session["current_question"] = current


    # --------------------------------------------------------
    # QUIZ FINISHED
    # --------------------------------------------------------

    if current >= len(questions_list):

        total = len(questions_list)


        percentage = (
            (score / total) * 100
            if total > 0
            else 0
        )


        save_score(
            session.get("username"),
            score,
            session.get("subject"),
            session.get("difficulty")
        )


        return render_template(
            "result.html",
            score=score,
            total=total,
            percentage=round(
                percentage,
                2
            ),
            wrong=total - score,
            wrong_answers=session.get(
                "wrong_answers",
                []
            )
        )


    # --------------------------------------------------------
    # CALCULATE REMAINING TIME
    # --------------------------------------------------------

    remaining_time = 0


    if start_time:

        elapsed_time = (
            time.time() - start_time
        )


        remaining_time = max(
            0,
            int(
                time_limit -
                elapsed_time
            )
        )


    # --------------------------------------------------------
    # NEXT QUESTION
    # --------------------------------------------------------

    return render_template(
        "quiz.html",

        question=questions_list[current],

        qno=current + 1,

        total=len(questions_list),

        subject=session.get(
            "subject"
        ),

        difficulty=session.get(
            "difficulty"
        ),

        remaining_time=remaining_time
    )


# ============================================================
# QUIZ CANCEL
# ============================================================

@app.route("/quiz_cancel")
def quiz_cancel():

    session.pop(
        "questions",
        None
    )

    session.pop(
        "current_question",
        None
    )

    session.pop(
        "score",
        None
    )

    session.pop(
        "wrong_answers",
        None
    )

    session.pop(
        "quiz_start_time",
        None
    )

    session.pop(
        "quiz_time_limit",
        None
    )

    session.pop(
        "subject",
        None
    )

    session.pop(
        "difficulty",
        None
    )

    return redirect("/subjects")


# ============================================================
# RESULT
# ============================================================

@app.route("/result")
def result():

    score = session.get(
        "score",
        0
    )

    questions_list = session.get(
        "questions",
        []
    )

    total = len(
        questions_list
    )


    percentage = (
        (score / total) * 100
        if total > 0
        else 0
    )


    wrong = total - score


    wrong_answers = session.get(
        "wrong_answers",
        []
    )


    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=round(
            percentage,
            2
        ),
        wrong=wrong,
        wrong_answers=wrong_answers
    )


# ============================================================
# LEADERBOARD
# ============================================================

@app.route("/leaderboard")
def leaderboard():

    leaderboard_data = (
        get_leaderboard()
    )


    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard_data
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    username = session.get(
        "username"
    )


    if not username:

        return redirect("/")


    history_data = get_history(
        username
    )


    return render_template(
        "history.html",
        history=history_data,
        username=username
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )