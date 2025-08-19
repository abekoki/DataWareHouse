"""
被験者管理API
"""

import sqlite3
from typing import List, Dict, Optional
from .exceptions import DWHNotFoundError, DWHConstraintError
from .connection import get_connection


def create_subject(subject_name: str, db_path: str = "database.db") -> int:
    """
    新しい被験者を登録
    
    Args:
        subject_name: 被験者名
        db_path: データベースファイルのパス
    
    Returns:
        subject_ID: 作成された被験者のID
    
    Raises:
        DWHConstraintError: データベース制約違反
    """
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO subject_table (subject_name) VALUES (?)",
                (subject_name,)
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create subject: {e}", table_name="subject_table") from e


def get_subject(subject_id: int, db_path: str = "database.db") -> Dict:
    """
    被験者IDで被験者情報を取得
    
    Args:
        subject_id: 被験者ID
        db_path: データベースファイルのパス
    
    Returns:
        dict: 被験者情報（subject_ID, subject_name）
    
    Raises:
        DWHNotFoundError: 被験者が見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject_ID, subject_name FROM subject_table WHERE subject_ID = ?",
            (subject_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Subject not found: subject_ID={subject_id}",
                table_name="subject_table",
                record_id=subject_id
            )
        
        return dict(row)


def list_subjects(db_path: str = "database.db") -> List[Dict]:
    """
    被験者一覧を取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: 被験者情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject_ID, subject_name FROM subject_table ORDER BY subject_ID"
        )
        
        return [dict(row) for row in cursor.fetchall()]


def update_subject(subject_id: int, subject_name: str, db_path: str = "database.db") -> None:
    """
    被験者情報を更新
    
    Args:
        subject_id: 被験者ID
        subject_name: 被験者名
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: 被験者が見つからない場合
        DWHConstraintError: データベース制約違反
    """
    # まず被験者の存在確認
    get_subject(subject_id, db_path)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subject_table SET subject_name = ? WHERE subject_ID = ?",
                (subject_name, subject_id)
            )
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to update subject: {e}", table_name="subject_table") from e


def delete_subject(subject_id: int, db_path: str = "database.db") -> None:
    """
    被験者を削除
    
    Args:
        subject_id: 被験者ID
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: 被験者が見つからない場合
        DWHConstraintError: 外部キー制約違反（ビデオが存在する場合）
    """
    # まず被験者の存在確認
    get_subject(subject_id, db_path)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subject_table WHERE subject_ID = ?", (subject_id,))
            
            if cursor.rowcount == 0:
                raise DWHNotFoundError(
                    f"Subject not found: subject_ID={subject_id}",
                    table_name="subject_table",
                    record_id=subject_id
                )
        except sqlite3.IntegrityError as e:
            raise DWHConstraintError(
                f"Cannot delete subject: referenced by other records. {e}",
                table_name="subject_table"
            ) from e


def find_subject_by_name(subject_name: str, db_path: str = "database.db") -> Optional[Dict]:
    """
    被験者名で被験者情報を検索
    
    Args:
        subject_name: 被験者名
        db_path: データベースファイルのパス
    
    Returns:
        dict or None: 被験者情報（見つからない場合はNone）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject_ID, subject_name FROM subject_table WHERE subject_name = ?",
            (subject_name,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
