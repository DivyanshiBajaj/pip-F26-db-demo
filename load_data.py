import csv
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "data" / "class_dataset.csv"
SCHEMA_PATH = ROOT / "schema.sql"

INTRO_ALLOWED = {"took_it", "equivalent", "neither"}
# CSV values already match the CHECK constraint; no remapping needed.
INTRO_PROGRAMMING_MAP = {}

SKIP_TOOLS = {"none yet"}

TABLES = [
    "student",
    "tool",
    "availability_slot",
    "student_tool",
    "student_availability",
]


def split_semicolon(value: str) -> list[str]:
    parts = []
    seen = set()
    for part in value.split(";"):
        item = part.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        parts.append(item)
    return parts


def map_intro_programming(raw: str) -> str:
    value = raw.strip()
    if value in INTRO_ALLOWED:
        return value
    if value in INTRO_PROGRAMMING_MAP:
        return INTRO_PROGRAMMING_MAP[value]
    raise ValueError(f"Unexpected intro_programming value: {raw!r}")


def main() -> None:
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    conn = psycopg2.connect(database_url)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DROP TABLE IF EXISTS student_tool;
                    DROP TABLE IF EXISTS student_availability;
                    DROP TABLE IF EXISTS student;
                    DROP TABLE IF EXISTS tool;
                    DROP TABLE IF EXISTS availability_slot;
                    """
                )
                cur.execute(schema_sql)

                tool_ids: dict[str, int] = {}
                slot_ids: dict[str, int] = {}

                with CSV_PATH.open(newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        intro = map_intro_programming(row["intro_programming"])
                        cur.execute(
                            """
                            INSERT INTO student (
                                netid, name, school_year, intro_programming,
                                skill_programming, skill_data_stats,
                                skill_frontend_design, skill_business_pitch,
                                working_style, interests, semester_goal,
                                submitted_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING student_id
                            """,
                            (
                                row["netid"].strip(),
                                row["name"].strip(),
                                row["school_year"].strip(),
                                intro,
                                int(row["skill_programming"]),
                                int(row["skill_data_stats"]),
                                int(row["skill_frontend_design"]),
                                int(row["skill_business_pitch"]),
                                row["working_style"],
                                row["interests"],
                                row["semester_goal"],
                                row["submitted_at"].strip(),
                            ),
                        )
                        student_id = cur.fetchone()[0]

                        for tool_name in split_semicolon(row["tools"]):
                            if tool_name.lower() in SKIP_TOOLS:
                                continue
                            if tool_name not in tool_ids:
                                cur.execute(
                                    """
                                    INSERT INTO tool (name)
                                    VALUES (%s)
                                    RETURNING tool_id
                                    """,
                                    (tool_name,),
                                )
                                tool_ids[tool_name] = cur.fetchone()[0]
                            cur.execute(
                                """
                                INSERT INTO student_tool (student_id, tool_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                                """,
                                (student_id, tool_ids[tool_name]),
                            )

                        for slot_name in split_semicolon(row["availability"]):
                            if slot_name not in slot_ids:
                                cur.execute(
                                    """
                                    INSERT INTO availability_slot (name)
                                    VALUES (%s)
                                    RETURNING slot_id
                                    """,
                                    (slot_name,),
                                )
                                slot_ids[slot_name] = cur.fetchone()[0]
                            cur.execute(
                                """
                                INSERT INTO student_availability (student_id, slot_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                                """,
                                (student_id, slot_ids[slot_name]),
                            )

                print("Table row counts:")
                for table in TABLES:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"  {table}: {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
