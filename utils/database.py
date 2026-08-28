import sqlite3


# ---------------- CREATE DATABASE ----------------

def create_database():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER,
            subject TEXT,
            difficulty TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- REGISTER USER ----------------

def register_user(username, email, password):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (?, ?, ?)
        """,
        (username, email, password)
    )

    conn.commit()
    conn.close()


# ---------------- LOGIN USER ----------------

def login_user(username, password):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=? AND password=?
        """,
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# ---------------- SAVE SCORE ----------------

def save_score(username, score, subject, difficulty):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO leaderboard
        (username, score, subject, difficulty)
        VALUES (?, ?, ?, ?)
        """,
        (username, score, subject, difficulty)
    )

    conn.commit()
    conn.close()


# ---------------- GET OVERALL LEADERBOARD ----------------

def get_leaderboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            username,

            SUM(
                score *
                CASE
                    WHEN LOWER(difficulty) = 'easy'
                        THEN 1

                    WHEN LOWER(difficulty) = 'medium'
                        THEN 2

                    WHEN LOWER(difficulty) = 'hard'
                        THEN 3

                    ELSE 1
                END
            ) AS total_points,

            COUNT(*) AS quizzes_played

        FROM leaderboard

        GROUP BY username

        ORDER BY total_points DESC

        LIMIT 10
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ---------------- GET USER HISTORY ----------------

def get_history(username):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            subject,
            difficulty,
            score
        FROM leaderboard
        WHERE username=?
        ORDER BY id DESC
    """, (username,))

    history = cursor.fetchall()

    conn.close()

    return history