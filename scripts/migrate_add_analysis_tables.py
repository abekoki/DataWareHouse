"""
SQLite3 非破壊マイグレーション: 課題分析関連テーブルの追加

内容:
- analysis_result_table, problem_table, analysis_data_table を作成（存在しない場合のみ）
- 既存データには影響しない（CREATE TABLE IF NOT EXISTS と存在確認を併用）
"""

from pathlib import Path
import sqlite3


ANALYSIS_RESULT_SQL = """
CREATE TABLE IF NOT EXISTS analysis_result_table (
    analysis_result_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_result_dir TEXT,
    analysis_timestamp TEXT,
    evaluation_result_ID INTEGER,
    FOREIGN KEY (evaluation_result_ID) REFERENCES evaluation_result_table(evaluation_result_ID) ON DELETE RESTRICT
);
"""


PROBLEM_SQL = """
CREATE TABLE IF NOT EXISTS problem_table (
    problem_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_name TEXT,
    problem_description TEXT,
    problem_status TEXT,
    analysis_result_ID INTEGER,
    FOREIGN KEY (analysis_result_ID) REFERENCES analysis_result_table(analysis_result_ID) ON DELETE RESTRICT
);
"""


ANALYSIS_DATA_SQL = """
CREATE TABLE IF NOT EXISTS analysis_data_table (
    analysis_data_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_data_ID INTEGER,
    analysis_result_ID INTEGER,
    problem_ID INTEGER,
    analysis_data_isproblem INTEGER CHECK (analysis_data_isproblem IN (0,1)),
    analysis_data_dir TEXT,
    analysis_data_description TEXT,
    FOREIGN KEY (evaluation_data_ID) REFERENCES evaluation_data_table(evaluation_data_ID) ON DELETE RESTRICT,
    FOREIGN KEY (analysis_result_ID) REFERENCES analysis_result_table(analysis_result_ID) ON DELETE RESTRICT,
    FOREIGN KEY (problem_ID) REFERENCES problem_table(problem_ID) ON DELETE RESTRICT
);
"""


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    return cur.fetchone() is not None


def migrate(db_path: Path) -> None:
    with sqlite3.connect(db_path.as_posix()) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        created = []

        if not table_exists(conn, "analysis_result_table"):
            conn.executescript(ANALYSIS_RESULT_SQL)
            created.append("analysis_result_table")

        if not table_exists(conn, "problem_table"):
            conn.executescript(PROBLEM_SQL)
            created.append("problem_table")

        if not table_exists(conn, "analysis_data_table"):
            conn.executescript(ANALYSIS_DATA_SQL)
            created.append("analysis_data_table")

        conn.commit()

    if created:
        print("作成したテーブル: " + ", ".join(created))
    else:
        print("変更なし（すべての課題分析テーブルは既に存在）")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "database.db"
    if not db_path.exists():
        print(f"データベースファイルが見つかりません: {db_path}")
        print("先に scripts/create_database.py を実行してください")
        return
    migrate(db_path)


if __name__ == "__main__":
    main()


