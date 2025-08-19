"""
データベース構造をクエリするスクリプト

機能:
- テーブル一覧の表示
- 各テーブルのスキーマ情報（カラム名、データ型、制約）
- インデックス情報
- 外部キー制約の確認
"""

import sqlite3
from pathlib import Path


def get_table_info(cursor: sqlite3.Cursor) -> None:
    """テーブル一覧とスキーマ情報を表示"""
    print("=== テーブル一覧 ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n--- {table_name} ---")
        
        # テーブルスキーマ
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("カラム:")
        for col in columns:
            cid, name, type_name, not_null, default_val, pk = col
            pk_str = " (PK)" if pk else ""
            not_null_str = " NOT NULL" if not_null else ""
            print(f"  {name}: {type_name}{pk_str}{not_null_str}")
        
        # インデックス
        cursor.execute(f"PRAGMA index_list({table_name});")
        indexes = cursor.fetchall()
        if indexes:
            print("インデックス:")
            for idx in indexes:
                idx_name = idx[1]
                print(f"  {idx_name}")


def get_foreign_keys(cursor: sqlite3.Cursor) -> None:
    """外部キー制約の情報を表示"""
    print("\n=== 外部キー制約 ===")
    
    # 外部キー制約の有効化状態を確認
    cursor.execute("PRAGMA foreign_keys;")
    fk_enabled = cursor.fetchone()[0]
    print(f"外部キー制約の有効化状態: {'有効' if fk_enabled else '無効'}")
    
    cursor.execute("PRAGMA foreign_key_list;")
    fks = cursor.fetchall()
    
    if not fks:
        print("外部キー制約は設定されていません")
        return
    
    for fk in fks:
        table_name = fk[0]
        from_col = fk[3]
        to_table = fk[2]
        to_col = fk[4]
        on_delete = fk[6]
        on_update = fk[7]
        print(f"{table_name}.{from_col} -> {to_table}.{to_col}")
        print(f"  ON DELETE: {on_delete}, ON UPDATE: {on_update}")


def main():
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "database.db"
    
    if not db_path.exists():
        print(f"データベースファイルが見つかりません: {db_path}")
        print("先に scripts/create_database.py を実行してください")
        return
    
    try:
        with sqlite3.connect(db_path.as_posix()) as conn:
            cursor = conn.cursor()
            
            # 外部キー制約を有効化
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            get_table_info(cursor)
            get_foreign_keys(cursor)
            
            # テーブル件数
            print("\n=== テーブル件数 ===")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"{table_name}: {count} 件")
                
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()
