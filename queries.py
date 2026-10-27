from pathlib import Path
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

ROOT = Path(__file__).resolve().parent

QUERIES = [
    (
        "student count",
        "SELECT count(*) FROM student;",
    ),
    (
        "first 5 students (name, school_year)",
        "SELECT name, school_year FROM student LIMIT 5;",
    ),
    (
        "students per tool",
        """
        SELECT t.name, COUNT(*) AS n_students
        FROM student_tool st
        JOIN tool t ON st.tool_id = t.tool_id
        GROUP BY t.name
        ORDER BY n_students DESC;
        """,
    ),
]


def print_result(title: str, rows) -> None:
    print(f"\n=== {title} ===")
    if not rows:
        print("(no rows)")
        return
    columns = list(rows[0].keys())
    print(" | ".join(columns))
    print("-" * max(len(" | ".join(columns)), 12))
    for row in rows:
        print(" | ".join(str(row[col]) for col in columns))


def main() -> None:
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for title, sql in QUERIES:
                cur.execute(sql)
                print_result(title, cur.fetchall())
        print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
