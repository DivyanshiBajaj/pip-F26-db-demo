from pathlib import Path
import os

from flask import Flask, render_template
from dotenv import load_dotenv
import psycopg2

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

app = Flask(__name__)


def get_student_names():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM student ORDER BY name;")
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


@app.route("/")
def index():
    names = get_student_names()
    return render_template("index.html", names=names)


if __name__ == "__main__":
    app.run(debug=True)
