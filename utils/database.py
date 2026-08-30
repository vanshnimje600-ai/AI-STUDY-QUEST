import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not set")

    return psycopg2.connect(database_url)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard(
            id SERIAL PRIMARY KEY,
            username TEXT,
            score INTEGER,
            subject TEXT,
            difficulty TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (%s, %s, %s)
        """,
        (username, email, password)
    )

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# LOGIN USER
# ============================================================

def login_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=%s AND password=%s
        """,
        (username, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


# ============================================================
# SAVE SCORE
# ============================================================

def save_score(username, score, subject, difficulty):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO leaderboard
        (username, score, subject, difficulty)
        VALUES (%s, %s, %s, %s)
        """,
        (username, score, subject, difficulty)
    )

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# GET OVERALL LEADERBOARD
# ============================================================

def get_leaderboard():

    conn = get_connection()
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

    cursor.close()
    conn.close()

    return data


# ============================================================
# GET USER HISTORY
# ============================================================

def get_history(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            subject,
            difficulty,
            score
            FROM leaderboard
            WHERE username=%s
            ORDER BY id DESC
            """,
            (username,)
    )

    history = cursor . fetchall()

    cursor . close()
    conn . close()

    return history