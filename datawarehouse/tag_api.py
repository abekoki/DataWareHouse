"""
タグ管理API
"""

import sqlite3
from typing import List, Dict, Optional
from .exceptions import DWHNotFoundError, DWHConstraintError, DWHValidationError
from .connection import get_connection


def create_tag(video_id: int, task_id: int, start: int, end: int, 
               db_path: str = "database.db") -> int:
    """
    新しいタグを登録
    
    Args:
        video_id: ビデオID
        task_id: タスクID
        start: 開始フレーム
        end: 終了フレーム
        db_path: データベースファイルのパス
    
    Returns:
        tag_ID: 作成されたタグのID
    
    Raises:
        DWHValidationError: start >= end の場合
        DWHConstraintError: ビデオまたはタスクが存在しない場合
    """
    # フレーム区間の検証
    if start >= end:
        raise DWHValidationError(
            f"Start frame must be less than end frame: start={start}, end={end}",
            field_name="start/end",
            field_value=f"{start}/{end}"
        )
    
    if start < 0:
        raise DWHValidationError(
            f"Start frame must be non-negative: {start}",
            field_name="start",
            field_value=start
        )
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tag_table (video_ID, task_ID, start, end)
                VALUES (?, ?, ?, ?)
                """,
                (video_id, task_id, start, end)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Video or task not found: video_ID={video_id}, task_ID={task_id}",
                    table_name="tag_table",
                    constraint_name="FK_video_task"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to create tag: {e}", table_name="tag_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create tag: {e}", table_name="tag_table") from e


def get_tag(tag_id: int, db_path: str = "database.db") -> Dict:
    """
    タグIDでタグ情報を取得
    
    Args:
        tag_id: タグID
        db_path: データベースファイルのパス
    
    Returns:
        dict: タグ情報（tag_ID, video_ID, task_ID, start, end）
    
    Raises:
        DWHNotFoundError: タグが見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tag_ID, video_ID, task_ID, start, end
            FROM tag_table
            WHERE tag_ID = ?
            """,
            (tag_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Tag not found: tag_ID={tag_id}",
                table_name="tag_table",
                record_id=tag_id
            )
        
        return dict(row)


def get_video_tags(video_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    ビデオのタグ一覧を取得
    
    Args:
        video_id: ビデオID
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: タグ情報のリスト（tag_ID, task_ID, start, end, task_name）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.tag_ID, t.video_ID, t.task_ID, t.start, t.end,
                   tk.task_name, tk.task_set, tk.task_describe
            FROM tag_table t
            JOIN task_table tk ON t.task_ID = tk.task_ID
            WHERE t.video_ID = ?
            ORDER BY t.start
            """,
            (video_id,)
        )
        
        return [dict(row) for row in cursor.fetchall()]


def get_task_tags(task_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    タスクのタグ一覧を取得
    
    Args:
        task_id: タスクID
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: タグ情報のリスト（tag_ID, video_ID, start, end, video_dir）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.tag_ID, t.video_ID, t.task_ID, t.start, t.end,
                   v.video_dir, v.video_date, v.subject_ID
            FROM tag_table t
            JOIN video_table v ON t.video_ID = v.video_ID
            WHERE t.task_ID = ?
            ORDER BY v.video_date, t.start
            """,
            (task_id,)
        )
        
        return [dict(row) for row in cursor.fetchall()]


def list_tags(video_id: Optional[int] = None, task_id: Optional[int] = None,
              db_path: str = "database.db") -> List[Dict]:
    """
    タグ一覧を取得
    
    Args:
        video_id: ビデオID（指定時はそのビデオのみ）
        task_id: タスクID（指定時はそのタスクのみ）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: タグ情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 条件の構築
        conditions = []
        params = []
        
        if video_id is not None:
            conditions.append("t.video_ID = ?")
            params.append(video_id)
        
        if task_id is not None:
            conditions.append("t.task_ID = ?")
            params.append(task_id)
        
        # SQL構築
        sql = """
            SELECT t.tag_ID, t.video_ID, t.task_ID, t.start, t.end,
                   v.video_dir, v.video_date, v.subject_ID,
                   tk.task_name, tk.task_set, tk.task_describe
            FROM tag_table t
            JOIN video_table v ON t.video_ID = v.video_ID
            JOIN task_table tk ON t.task_ID = tk.task_ID
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY v.video_date, t.start"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def update_tag(tag_id: int, video_id: Optional[int] = None, task_id: Optional[int] = None,
               start: Optional[int] = None, end: Optional[int] = None,
               db_path: str = "database.db") -> None:
    """
    タグ情報を更新
    
    Args:
        tag_id: タグID
        video_id: ビデオID（更新する場合）
        task_id: タスクID（更新する場合）
        start: 開始フレーム（更新する場合）
        end: 終了フレーム（更新する場合）
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: タグが見つからない場合
        DWHValidationError: フレーム区間が不正な場合
        DWHConstraintError: データベース制約違反
    """
    # まずタグの存在確認と現在の値を取得
    current_tag = get_tag(tag_id, db_path)
    
    # 更新後の値を確定
    new_start = start if start is not None else current_tag['start']
    new_end = end if end is not None else current_tag['end']
    
    # フレーム区間の検証
    if new_start >= new_end:
        raise DWHValidationError(
            f"Start frame must be less than end frame: start={new_start}, end={new_end}",
            field_name="start/end",
            field_value=f"{new_start}/{new_end}"
        )
    
    if new_start < 0:
        raise DWHValidationError(
            f"Start frame must be non-negative: {new_start}",
            field_name="start",
            field_value=new_start
        )
    
    # 更新対象のフィールドを特定
    updates = []
    params = []
    
    if video_id is not None:
        updates.append("video_ID = ?")
        params.append(video_id)
    
    if task_id is not None:
        updates.append("task_ID = ?")
        params.append(task_id)
    
    if start is not None:
        updates.append("start = ?")
        params.append(start)
    
    if end is not None:
        updates.append("end = ?")
        params.append(end)
    
    if not updates:
        return  # 更新対象なし
    
    params.append(tag_id)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            sql = f"UPDATE tag_table SET {', '.join(updates)} WHERE tag_ID = ?"
            cursor.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Video or task not found: video_ID={video_id}, task_ID={task_id}",
                    table_name="tag_table",
                    constraint_name="FK_video_task"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to update tag: {e}", table_name="tag_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to update tag: {e}", table_name="tag_table") from e


def delete_tag(tag_id: int, db_path: str = "database.db") -> None:
    """
    タグを削除
    
    Args:
        tag_id: タグID
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: タグが見つからない場合
    """
    # まずタグの存在確認
    get_tag(tag_id, db_path)
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tag_table WHERE tag_ID = ?", (tag_id,))
        
        if cursor.rowcount == 0:
            raise DWHNotFoundError(
                f"Tag not found: tag_ID={tag_id}",
                table_name="tag_table",
                record_id=tag_id
            )


def get_tag_duration(tag_id: int, fps: float = 30.0, db_path: str = "database.db") -> float:
    """
    タグの時間長を計算
    
    Args:
        tag_id: タグID
        fps: フレームレート（デフォルト: 30.0）
        db_path: データベースファイルのパス
    
    Returns:
        float: タグの時間長（秒）
    
    Raises:
        DWHNotFoundError: タグが見つからない場合
    """
    tag = get_tag(tag_id, db_path)
    frame_count = tag['end'] - tag['start']
    return frame_count / fps
