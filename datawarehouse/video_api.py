"""
ビデオ管理API
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from .exceptions import DWHNotFoundError, DWHConstraintError, DWHValidationError
from .connection import get_connection


def create_video(video_dir: str, subject_id: int, video_date: str, video_length: int, 
                 db_path: str = "database.db") -> int:
    """
    新しいビデオを登録
    
    Args:
        video_dir: ビデオファイルのディレクトリパス
        subject_id: 被験者ID
        video_date: 取得日（YYYY-MM-DD）
        video_length: ビデオの長さ（秒）
        db_path: データベースファイルのパス
    
    Returns:
        video_ID: 作成されたビデオのID
    
    Raises:
        DWHValidationError: 日付形式が不正な場合
        DWHConstraintError: 被験者が存在しない場合やその他のデータベース制約違反
    """
    # 日付形式の検証
    try:
        datetime.strptime(video_date, "%Y-%m-%d")
    except ValueError:
        raise DWHValidationError(
            f"Invalid date format: {video_date}. Expected format: YYYY-MM-DD",
            field_name="video_date",
            field_value=video_date
        )
    
    # ビデオ長さの検証
    if video_length <= 0:
        raise DWHValidationError(
            f"Video length must be positive: {video_length}",
            field_name="video_length",
            field_value=video_length
        )
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO video_table (video_dir, subject_ID, video_date, video_length)
                VALUES (?, ?, ?, ?)
                """,
                (video_dir, subject_id, video_date, video_length)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Subject not found: subject_ID={subject_id}",
                    table_name="video_table",
                    constraint_name="FK_subject_ID"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to create video: {e}", table_name="video_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create video: {e}", table_name="video_table") from e


def get_video(video_id: int, db_path: str = "database.db") -> Dict:
    """
    ビデオIDでビデオ情報を取得
    
    Args:
        video_id: ビデオID
        db_path: データベースファイルのパス
    
    Returns:
        dict: ビデオ情報（video_ID, video_dir, subject_ID, video_date, video_length）
    
    Raises:
        DWHNotFoundError: ビデオが見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT video_ID, video_dir, subject_ID, video_date, video_length
            FROM video_table
            WHERE video_ID = ?
            """,
            (video_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Video not found: video_ID={video_id}",
                table_name="video_table",
                record_id=video_id
            )
        
        return dict(row)


def list_videos(subject_id: Optional[int] = None, date_from: Optional[str] = None,
                date_to: Optional[str] = None, db_path: str = "database.db") -> List[Dict]:
    """
    ビデオ一覧を取得
    
    Args:
        subject_id: 被験者ID（指定時はその被験者のみ）
        date_from: 開始日（YYYY-MM-DD）
        date_to: 終了日（YYYY-MM-DD）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: ビデオ情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 条件の構築
        conditions = []
        params = []
        
        if subject_id is not None:
            conditions.append("subject_ID = ?")
            params.append(subject_id)
        
        if date_from is not None:
            conditions.append("video_date >= ?")
            params.append(date_from)
        
        if date_to is not None:
            conditions.append("video_date <= ?")
            params.append(date_to)
        
        # SQL構築
        sql = """
            SELECT v.video_ID, v.video_dir, v.subject_ID, v.video_date, v.video_length,
                   s.subject_name
            FROM video_table v
            JOIN subject_table s ON v.subject_ID = s.subject_ID
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY v.video_date DESC, v.video_ID"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def get_videos_by_subject(subject_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    被験者IDでビデオ一覧を取得
    
    Args:
        subject_id: 被験者ID
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: ビデオ情報のリスト
    """
    return list_videos(subject_id=subject_id, db_path=db_path)


def update_video(video_id: int, video_dir: Optional[str] = None, 
                 subject_id: Optional[int] = None, video_date: Optional[str] = None,
                 video_length: Optional[int] = None, db_path: str = "database.db") -> None:
    """
    ビデオ情報を更新
    
    Args:
        video_id: ビデオID
        video_dir: ビデオファイルのディレクトリパス（更新する場合）
        subject_id: 被験者ID（更新する場合）
        video_date: 取得日（更新する場合）
        video_length: ビデオの長さ（更新する場合）
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: ビデオが見つからない場合
        DWHValidationError: 入力値が不正な場合
        DWHConstraintError: データベース制約違反
    """
    # まずビデオの存在確認
    get_video(video_id, db_path)
    
    # 日付形式の検証
    if video_date is not None:
        try:
            datetime.strptime(video_date, "%Y-%m-%d")
        except ValueError:
            raise DWHValidationError(
                f"Invalid date format: {video_date}. Expected format: YYYY-MM-DD",
                field_name="video_date",
                field_value=video_date
            )
    
    # ビデオ長さの検証
    if video_length is not None and video_length <= 0:
        raise DWHValidationError(
            f"Video length must be positive: {video_length}",
            field_name="video_length",
            field_value=video_length
        )
    
    # 更新対象のフィールドを特定
    updates = []
    params = []
    
    if video_dir is not None:
        updates.append("video_dir = ?")
        params.append(video_dir)
    
    if subject_id is not None:
        updates.append("subject_ID = ?")
        params.append(subject_id)
    
    if video_date is not None:
        updates.append("video_date = ?")
        params.append(video_date)
    
    if video_length is not None:
        updates.append("video_length = ?")
        params.append(video_length)
    
    if not updates:
        return  # 更新対象なし
    
    params.append(video_id)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            sql = f"UPDATE video_table SET {', '.join(updates)} WHERE video_ID = ?"
            cursor.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Subject not found: subject_ID={subject_id}",
                    table_name="video_table",
                    constraint_name="FK_subject_ID"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to update video: {e}", table_name="video_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to update video: {e}", table_name="video_table") from e


def delete_video(video_id: int, db_path: str = "database.db") -> None:
    """
    ビデオを削除
    
    Args:
        video_id: ビデオID
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: ビデオが見つからない場合
        DWHConstraintError: 外部キー制約違反（タグや出力が存在する場合）
    """
    # まずビデオの存在確認
    get_video(video_id, db_path)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM video_table WHERE video_ID = ?", (video_id,))
            
            if cursor.rowcount == 0:
                raise DWHNotFoundError(
                    f"Video not found: video_ID={video_id}",
                    table_name="video_table",
                    record_id=video_id
                )
        except sqlite3.IntegrityError as e:
            raise DWHConstraintError(
                f"Cannot delete video: referenced by other records. {e}",
                table_name="video_table"
            ) from e
