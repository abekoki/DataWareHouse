"""
タスク管理API
"""

import sqlite3
from typing import List, Dict, Optional
from .exceptions import DWHNotFoundError, DWHConstraintError
from .connection import get_connection


def create_task(task_set: int, task_name: str, task_describe: str, db_path: str = "database.db") -> int:
    """
    新しいタスクを登録
    
    Args:
        task_set: タスクセット番号
        task_name: タスク名
        task_describe: タスクの説明
        db_path: データベースファイルのパス
    
    Returns:
        task_ID: 作成されたタスクのID
    
    Raises:
        DWHConstraintError: データベース制約違反
    """
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO task_table (task_set, task_name, task_describe)
                VALUES (?, ?, ?)
                """,
                (task_set, task_name, task_describe)
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create task: {e}", table_name="task_table") from e


def get_task(task_id: int, db_path: str = "database.db") -> Dict:
    """
    タスクIDでタスク情報を取得
    
    Args:
        task_id: タスクID
        db_path: データベースファイルのパス
    
    Returns:
        dict: タスク情報（task_ID, task_set, task_name, task_describe）
    
    Raises:
        DWHNotFoundError: タスクが見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT task_ID, task_set, task_name, task_describe
            FROM task_table
            WHERE task_ID = ?
            """,
            (task_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Task not found: task_ID={task_id}",
                table_name="task_table",
                record_id=task_id
            )
        
        return dict(row)


def list_tasks(task_set: Optional[int] = None, db_path: str = "database.db") -> List[Dict]:
    """
    タスク一覧を取得
    
    Args:
        task_set: タスクセット番号（指定時はそのセットのみ）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: タスク情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        if task_set is not None:
            cursor.execute(
                """
                SELECT task_ID, task_set, task_name, task_describe
                FROM task_table
                WHERE task_set = ?
                ORDER BY task_ID
                """,
                (task_set,)
            )
        else:
            cursor.execute(
                """
                SELECT task_ID, task_set, task_name, task_describe
                FROM task_table
                ORDER BY task_set, task_ID
                """
            )
        
        return [dict(row) for row in cursor.fetchall()]


def update_task(task_id: int, task_set: Optional[int] = None, 
                task_name: Optional[str] = None, task_describe: Optional[str] = None,
                db_path: str = "database.db") -> None:
    """
    タスク情報を更新
    
    Args:
        task_id: タスクID
        task_set: タスクセット番号（更新する場合）
        task_name: タスク名（更新する場合）
        task_describe: タスクの説明（更新する場合）
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: タスクが見つからない場合
        DWHConstraintError: データベース制約違反
    """
    # まずタスクの存在確認
    get_task(task_id, db_path)
    
    # 更新対象のフィールドを特定
    updates = []
    params = []
    
    if task_set is not None:
        updates.append("task_set = ?")
        params.append(task_set)
    
    if task_name is not None:
        updates.append("task_name = ?")
        params.append(task_name)
    
    if task_describe is not None:
        updates.append("task_describe = ?")
        params.append(task_describe)
    
    if not updates:
        return  # 更新対象なし
    
    params.append(task_id)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            sql = f"UPDATE task_table SET {', '.join(updates)} WHERE task_ID = ?"
            cursor.execute(sql, params)
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to update task: {e}", table_name="task_table") from e


def delete_task(task_id: int, db_path: str = "database.db") -> None:
    """
    タスクを削除
    
    Args:
        task_id: タスクID
        db_path: データベースファイルのパス
    
    Raises:
        DWHNotFoundError: タスクが見つからない場合
        DWHConstraintError: 外部キー制約違反（タグが存在する場合）
    """
    # まずタスクの存在確認
    get_task(task_id, db_path)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM task_table WHERE task_ID = ?", (task_id,))
            
            if cursor.rowcount == 0:
                raise DWHNotFoundError(
                    f"Task not found: task_ID={task_id}",
                    table_name="task_table",
                    record_id=task_id
                )
        except sqlite3.IntegrityError as e:
            raise DWHConstraintError(
                f"Cannot delete task: referenced by other records. {e}",
                table_name="task_table"
            ) from e
