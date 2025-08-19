"""
SQLite3 データベース初期化スクリプト

役割:
- プロジェクト直下に `database.db` を作成
- `00_design/schema.sql` を読み込み、スキーマを適用

注意:
- SQLite の外部キー制約はデフォルト無効のため、接続ごとに `PRAGMA foreign_keys = ON;` を設定
"""

from pathlib import Path
import sqlite3


def load_schema_text(schema_path: Path) -> str:
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return schema_path.read_text(encoding="utf-8")


def create_database(db_path: Path, schema_sql: str) -> None:
    # DBディレクトリを作成（必要な場合）
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # 既存のデータベースが存在するかチェック
    db_exists = db_path.exists()
    
    with sqlite3.connect(db_path.as_posix()) as conn:
        # 外部キー制約を有効化
        conn.execute("PRAGMA foreign_keys = ON;")
        
        if db_exists:
            print("既存のデータベースを更新中...")
            # 既存データベースの場合は、外部キー制約の設定のみ更新
            print("外部キー制約の設定を更新しました")
        else:
            print("新しいデータベースを作成中...")
            # 新規作成の場合は、スキーマを適用
            conn.executescript(schema_sql)
            print("スキーマを適用しました")
        
        # 外部キー制約の状態を確認
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        fk_status = cursor.fetchone()[0]
        print(f"外部キー制約の状態: {'有効' if fk_status else '無効'}")
        
        conn.commit()


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "database.db"
    schema_path = project_root / "00_design" / "schema.sql"

    schema_sql = load_schema_text(schema_path)
    create_database(db_path, schema_sql)
    print(f"Created/updated SQLite database: {db_path}")


if __name__ == "__main__":
    main()


