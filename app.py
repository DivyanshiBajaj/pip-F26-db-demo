from pathlib import Path
import os

from flask import Flask, render_template
from dotenv import load_dotenv
import psycopg2

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

app = Flask(__name__)


def get_page_data():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM student ORDER BY name;")
            names = [row[0] for row in cur.fetchall()]
            cur.execute(
                """
                SELECT
                    AVG(skill_programming),
                    AVG(skill_data_stats),
                    AVG(skill_frontend_design),
                    AVG(skill_business_pitch)
                FROM student;
                """
            )
            row = cur.fetchone()
            skill_averages = {
                "programming": round(float(row[0]), 2),
                "data_stats": round(float(row[1]), 2),
                "frontend_design": round(float(row[2]), 2),
                "business_pitch": round(float(row[3]), 2),
            }
            return names, skill_averages
    finally:
        conn.close()


@app.route("/")
def index():
    names, skill_averages = get_page_data()
    return render_template(
        "index.html",
        names=names,
        skill_averages=skill_averages,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
