"""
SQLite3 非破壊マイグレーション: 評価テーブルの追加

内容:
- evaluation_result_table, evaluation_data_table を作成（存在しない場合のみ）
- 既存データには影響しない（CREATE TABLE IF NOT EXISTS とガードを併用）
"""

from pathlib import Path
import sqlite3


EVALUATION_RESULT_SQL = """
CREATE TABLE IF NOT EXISTS evaluation_result_table (
    evaluation_result_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT,
    algorithm_ID INTEGER,
    true_positive REAL,
    false_positive REAL,
    evaluation_result_dir TEXT,
    evaluation_timestamp TEXT,
    FOREIGN KEY (algorithm_ID) REFERENCES algorithm_table(algorithm_ID) ON DELETE RESTRICT
);
"""

EVALUATION_DATA_SQL = """
CREATE TABLE IF NOT EXISTS evaluation_data_table (
    evaluation_data_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_result_ID INTEGER,
    algorithm_output_ID INTEGER,
    correct_task_num INTEGER,
    total_task_num INTEGER,
    evaluation_data_path TEXT,
    FOREIGN KEY (evaluation_result_ID) REFERENCES evaluation_result_table(evaluation_result_ID) ON DELETE RESTRICT,
    FOREIGN KEY (algorithm_output_ID) REFERENCES algorithm_output_table(algorithm_output_ID) ON DELETE RESTRICT,
    CHECK (correct_task_num <= total_task_num)
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

        if not table_exists(conn, "evaluation_result_table"):
            conn.executescript(EVALUATION_RESULT_SQL)
            created.append("evaluation_result_table")

        if not table_exists(conn, "evaluation_data_table"):
            conn.executescript(EVALUATION_DATA_SQL)
            created.append("evaluation_data_table")

        conn.commit()

    if created:
        print("作成したテーブル: " + ", ".join(created))
    else:
        print("変更なし（すべての評価テーブルは既に存在）")


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


