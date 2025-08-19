"""
検索・分析API
"""

import sqlite3
from typing import List, Dict, Optional
from .exceptions import DWHConstraintError
from .connection import get_connection


def search_task_executions(task_set: Optional[int] = None, subject_id: Optional[int] = None,
                          date_from: Optional[str] = None, date_to: Optional[str] = None,
                          db_path: str = "database.db") -> List[Dict]:
    """
    タスク実行状況を検索
    
    Args:
        task_set: タスクセット番号
        subject_id: 被験者ID
        date_from: 開始日（YYYY-MM-DD）
        date_to: 終了日（YYYY-MM-DD）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: タスク実行情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 条件の構築
        conditions = []
        params = []
        
        if task_set is not None:
            conditions.append("tk.task_set = ?")
            params.append(task_set)
        
        if subject_id is not None:
            conditions.append("s.subject_ID = ?")
            params.append(subject_id)
        
        if date_from is not None:
            conditions.append("v.video_date >= ?")
            params.append(date_from)
        
        if date_to is not None:
            conditions.append("v.video_date <= ?")
            params.append(date_to)
        
        # SQL構築
        sql = """
            SELECT t.tag_ID, 
                   tk.task_ID, tk.task_set, tk.task_name, tk.task_describe,
                   s.subject_ID, s.subject_name,
                   v.video_ID, v.video_dir, v.video_date, v.video_length,
                   t.start, t.end,
                   (t.end - t.start) as frame_count
            FROM tag_table t
            JOIN task_table tk ON t.task_ID = tk.task_ID
            JOIN video_table v ON t.video_ID = v.video_ID
            JOIN subject_table s ON v.subject_ID = s.subject_ID
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY v.video_date, tk.task_set, tk.task_ID, t.start"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def get_version_history(table_name: str, current_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    バージョン履歴を取得（自己参照テーブル用）
    
    Args:
        table_name: テーブル名（'core_lib_table' または 'algorithm_table'）
        current_id: 現在のバージョンID
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: バージョン履歴のリスト
    
    Raises:
        DWHConstraintError: 不正なテーブル名の場合
    """
    if table_name == "core_lib_table":
        from .core_lib_api import get_core_lib_version_history
        return get_core_lib_version_history(current_id, db_path)
    elif table_name == "algorithm_table":
        from .algorithm_api import get_algorithm_version_history
        return get_algorithm_version_history(current_id, db_path)
    else:
        raise DWHConstraintError(
            f"Invalid table name: {table_name}. Expected 'core_lib_table' or 'algorithm_table'.",
            table_name=table_name
        )


def get_table_statistics(db_path: str = "database.db") -> Dict[str, int]:
    """
    全テーブルの件数統計を取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        dict: テーブル名と件数の辞書
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # テーブル一覧を取得
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        # 各テーブルの件数を取得
        statistics = {}
        for table_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            statistics[table_name] = count
        
        return statistics


def check_data_integrity(db_path: str = "database.db") -> Dict[str, any]:
    """
    データ整合性をチェック
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        dict: 整合性チェック結果
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        result = {
            "foreign_key_check": [],
            "frame_validation": [],
            "orphaned_records": {},
            "duplicate_hashes": []
        }
        
        # 外部キー制約チェック
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        result["foreign_key_check"] = [dict(row) for row in fk_violations]
        
        # フレーム区間の検証（start < end）
        cursor.execute(
            """
            SELECT tag_ID, video_ID, task_ID, start, end
            FROM tag_table
            WHERE start >= end
            """
        )
        frame_violations = cursor.fetchall()
        result["frame_validation"] = [dict(row) for row in frame_violations]
        
        # 孤立レコードの検出
        # ビデオに関連しないタグ
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM tag_table t
            LEFT JOIN video_table v ON t.video_ID = v.video_ID
            WHERE v.video_ID IS NULL
            """
        )
        result["orphaned_records"]["tags_without_video"] = cursor.fetchone()[0]
        
        # タスクに関連しないタグ
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM tag_table t
            LEFT JOIN task_table tk ON t.task_ID = tk.task_ID
            WHERE tk.task_ID IS NULL
            """
        )
        result["orphaned_records"]["tags_without_task"] = cursor.fetchone()[0]
        
        # 重複コミットハッシュの検出
        cursor.execute(
            """
            SELECT core_lib_commit_hash, COUNT(*) as count
            FROM core_lib_table
            GROUP BY core_lib_commit_hash
            HAVING COUNT(*) > 1
            """
        )
        duplicate_core_hashes = cursor.fetchall()
        
        cursor.execute(
            """
            SELECT algorithm_commit_hash, COUNT(*) as count
            FROM algorithm_table
            GROUP BY algorithm_commit_hash
            HAVING COUNT(*) > 1
            """
        )
        duplicate_algo_hashes = cursor.fetchall()
        
        result["duplicate_hashes"] = {
            "core_lib": [dict(row) for row in duplicate_core_hashes],
            "algorithm": [dict(row) for row in duplicate_algo_hashes]
        }
        
        return result


def get_processing_pipeline_summary(video_id: Optional[int] = None, 
                                   db_path: str = "database.db") -> List[Dict]:
    """
    処理パイプラインの概要を取得
    
    Args:
        video_id: ビデオID（指定時はそのビデオのみ）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: パイプライン情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 条件の構築
        where_clause = ""
        params = []
        
        if video_id is not None:
            where_clause = "WHERE v.video_ID = ?"
            params.append(video_id)
        
        # SQL実行
        sql = f"""
            SELECT v.video_ID, v.video_dir, v.video_date,
                   s.subject_name,
                   co.core_lib_output_ID, cl.core_lib_version,
                   ao.algorithm_output_ID, al.algorithm_version,
                   COUNT(t.tag_ID) as tag_count
            FROM video_table v
            JOIN subject_table s ON v.subject_ID = s.subject_ID
            LEFT JOIN core_lib_output_table co ON v.video_ID = co.video_ID
            LEFT JOIN core_lib_table cl ON co.core_lib_ID = cl.core_lib_ID
            LEFT JOIN algorithm_output_table ao ON co.core_lib_output_ID = ao.core_lib_output_ID
            LEFT JOIN algorithm_table al ON ao.algorithm_ID = al.algorithm_ID
            LEFT JOIN tag_table t ON v.video_ID = t.video_ID
            {where_clause}
            GROUP BY v.video_ID, co.core_lib_output_ID, ao.algorithm_output_ID
            ORDER BY v.video_date, v.video_ID
        """
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def get_performance_metrics(db_path: str = "database.db") -> Dict[str, any]:
    """
    パフォーマンスメトリクスを取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        dict: パフォーマンス情報
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        metrics = {}
        
        # 基本統計
        cursor.execute("SELECT COUNT(*) FROM video_table")
        metrics["total_videos"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tag_table")
        metrics["total_tags"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM core_lib_output_table")
        metrics["total_core_lib_outputs"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM algorithm_output_table")
        metrics["total_algorithm_outputs"] = cursor.fetchone()[0]
        
        # 処理効率
        cursor.execute(
            """
            SELECT AVG(tag_count) as avg_tags_per_video
            FROM (
                SELECT COUNT(*) as tag_count
                FROM tag_table
                GROUP BY video_ID
            )
            """
        )
        result = cursor.fetchone()
        metrics["avg_tags_per_video"] = result[0] if result[0] else 0
        
        # バージョン情報
        cursor.execute("SELECT COUNT(*) FROM core_lib_table")
        metrics["core_lib_versions"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM algorithm_table")
        metrics["algorithm_versions"] = cursor.fetchone()[0]
        
        return metrics
