"""
アルゴリズム管理API
"""

import sqlite3
import re
from typing import List, Dict, Optional
from .exceptions import DWHNotFoundError, DWHConstraintError, DWHValidationError, DWHUniqueConstraintError
from .connection import get_connection


def _validate_commit_hash(commit_hash: str) -> None:
    """コミットハッシュの形式を検証"""
    if not re.match(r'^[a-f0-9]{40}$', commit_hash):
        raise DWHValidationError(
            f"Invalid commit hash format: {commit_hash}. Expected 40-character hexadecimal string.",
            field_name="commit_hash",
            field_value=commit_hash
        )


def create_algorithm_version(version: str, update_info: str, commit_hash: str, 
                           base_version_id: Optional[int] = None,
                           db_path: str = "database.db") -> int:
    """
    新しいアルゴリズムバージョンを登録
    
    Args:
        version: バージョン文字列（例: 2.1.0）
        update_info: 更新内容の説明
        commit_hash: Gitコミットハッシュ（40文字）
        base_version_id: ベースバージョンのID（新規の場合はNone）
        db_path: データベースファイルのパス
    
    Returns:
        algorithm_ID: 作成されたアルゴリズムのID
    
    Raises:
        DWHValidationError: コミットハッシュの形式が不正な場合
        DWHUniqueConstraintError: コミットハッシュが重複する場合
        DWHConstraintError: ベースバージョンが存在しない場合
    """
    # コミットハッシュの形式検証
    _validate_commit_hash(commit_hash)
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO algorithm_table 
                (algorithm_version, algorithm_update_information, algorithm_base_version_ID, algorithm_commit_hash)
                VALUES (?, ?, ?, ?)
                """,
                (version, update_info, base_version_id, commit_hash)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) and "algorithm_commit_hash" in str(e):
                raise DWHUniqueConstraintError(
                    f"Commit hash already exists: {commit_hash}",
                    table_name="algorithm_table",
                    field_name="algorithm_commit_hash"
                ) from e
            elif "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Base version not found: algorithm_ID={base_version_id}",
                    table_name="algorithm_table",
                    constraint_name="FK_base_version"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to create algorithm version: {e}", table_name="algorithm_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create algorithm version: {e}", table_name="algorithm_table") from e


def get_algorithm_version(algorithm_id: int, db_path: str = "database.db") -> Dict:
    """
    アルゴリズムIDでバージョン情報を取得
    
    Args:
        algorithm_id: アルゴリズムID
        db_path: データベースファイルのパス
    
    Returns:
        dict: アルゴリズム情報
    
    Raises:
        DWHNotFoundError: アルゴリズムが見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT algorithm_ID, algorithm_version, algorithm_update_information, 
                   algorithm_base_version_ID, algorithm_commit_hash
            FROM algorithm_table
            WHERE algorithm_ID = ?
            """,
            (algorithm_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Algorithm not found: algorithm_ID={algorithm_id}",
                table_name="algorithm_table",
                record_id=algorithm_id
            )
        
        return dict(row)


def list_algorithm_versions(db_path: str = "database.db") -> List[Dict]:
    """
    アルゴリズムバージョン一覧を取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: アルゴリズム情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT algorithm_ID, algorithm_version, algorithm_update_information, 
                   algorithm_base_version_ID, algorithm_commit_hash
            FROM algorithm_table
            ORDER BY algorithm_ID
            """
        )
        
        return [dict(row) for row in cursor.fetchall()]


def get_algorithm_version_history(algorithm_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    アルゴリズムのバージョン履歴を取得（自己参照をたどる）
    
    Args:
        algorithm_id: 現在のアルゴリズムID
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: バージョン履歴のリスト（古い順）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 再帰的にバージョン履歴を取得
        history = []
        current_id = algorithm_id
        
        while current_id is not None:
            cursor.execute(
                """
                SELECT algorithm_ID, algorithm_version, algorithm_update_information, 
                       algorithm_base_version_ID, algorithm_commit_hash
                FROM algorithm_table
                WHERE algorithm_ID = ?
                """,
                (current_id,)
            )
            
            row = cursor.fetchone()
            if row is None:
                break
            
            history.append(dict(row))
            current_id = row['algorithm_base_version_ID']
        
        # 古い順に並べ替え
        return list(reversed(history))


def find_algorithm_by_version(version: str, db_path: str = "database.db") -> Optional[Dict]:
    """
    バージョン文字列でアルゴリズムを検索
    
    Args:
        version: バージョン文字列
        db_path: データベースファイルのパス
    
    Returns:
        dict or None: アルゴリズム情報（見つからない場合はNone）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT algorithm_ID, algorithm_version, algorithm_update_information, 
                   algorithm_base_version_ID, algorithm_commit_hash
            FROM algorithm_table
            WHERE algorithm_version = ?
            """,
            (version,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None


def find_algorithm_by_commit_hash(commit_hash: str, db_path: str = "database.db") -> Optional[Dict]:
    """
    コミットハッシュでアルゴリズムを検索
    
    Args:
        commit_hash: コミットハッシュ
        db_path: データベースファイルのパス
    
    Returns:
        dict or None: アルゴリズム情報（見つからない場合はNone）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT algorithm_ID, algorithm_version, algorithm_update_information, 
                   algorithm_base_version_ID, algorithm_commit_hash
            FROM algorithm_table
            WHERE algorithm_commit_hash = ?
            """,
            (commit_hash,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None


def create_algorithm_output(algorithm_id: int, core_lib_output_id: int, output_dir: str,
                           db_path: str = "database.db") -> int:
    """
    アルゴリズムの評価結果を登録
    
    Args:
        algorithm_id: アルゴリズムID
        core_lib_output_id: コアライブラリ出力ID
        output_dir: 出力ディレクトリパス
        db_path: データベースファイルのパス
    
    Returns:
        algorithm_output_ID: 作成された出力のID
    
    Raises:
        DWHConstraintError: アルゴリズムまたはコアライブラリ出力が存在しない場合
    """
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO algorithm_output_table (algorithm_ID, core_lib_output_ID, algorithm_output_dir)
                VALUES (?, ?, ?)
                """,
                (algorithm_id, core_lib_output_id, output_dir)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Algorithm or core library output not found: algorithm_ID={algorithm_id}, core_lib_output_ID={core_lib_output_id}",
                    table_name="algorithm_output_table",
                    constraint_name="FK_algorithm_core_lib_output"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to create algorithm output: {e}", table_name="algorithm_output_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create algorithm output: {e}", table_name="algorithm_output_table") from e


def get_algorithm_output(output_id: int, db_path: str = "database.db") -> Dict:
    """
    アルゴリズム出力IDで出力情報を取得
    
    Args:
        output_id: 出力ID
        db_path: データベースファイルのパス
    
    Returns:
        dict: 出力情報
    
    Raises:
        DWHNotFoundError: 出力が見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ao.algorithm_output_ID, ao.algorithm_ID, ao.core_lib_output_ID, ao.algorithm_output_dir,
                   al.algorithm_version, al.algorithm_commit_hash,
                   co.core_lib_output_dir, cl.core_lib_version,
                   v.video_dir, v.video_date
            FROM algorithm_output_table ao
            JOIN algorithm_table al ON ao.algorithm_ID = al.algorithm_ID
            JOIN core_lib_output_table co ON ao.core_lib_output_ID = co.core_lib_output_ID
            JOIN core_lib_table cl ON co.core_lib_ID = cl.core_lib_ID
            JOIN video_table v ON co.video_ID = v.video_ID
            WHERE ao.algorithm_output_ID = ?
            """,
            (output_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Algorithm output not found: algorithm_output_ID={output_id}",
                table_name="algorithm_output_table",
                record_id=output_id
            )
        
        return dict(row)


def list_algorithm_outputs(algorithm_id: Optional[int] = None, core_lib_output_id: Optional[int] = None,
                          db_path: str = "database.db") -> List[Dict]:
    """
    アルゴリズム出力一覧を取得
    
    Args:
        algorithm_id: アルゴリズムID（指定時はそのバージョンのみ）
        core_lib_output_id: コアライブラリ出力ID（指定時はその出力ベースのみ）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: 出力情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 条件の構築
        conditions = []
        params = []
        
        if algorithm_id is not None:
            conditions.append("ao.algorithm_ID = ?")
            params.append(algorithm_id)
        
        if core_lib_output_id is not None:
            conditions.append("ao.core_lib_output_ID = ?")
            params.append(core_lib_output_id)
        
        # SQL構築
        sql = """
            SELECT ao.algorithm_output_ID, ao.algorithm_ID, ao.core_lib_output_ID, ao.algorithm_output_dir,
                   al.algorithm_version, al.algorithm_commit_hash,
                   co.core_lib_output_dir, cl.core_lib_version,
                   v.video_dir, v.video_date
            FROM algorithm_output_table ao
            JOIN algorithm_table al ON ao.algorithm_ID = al.algorithm_ID
            JOIN core_lib_output_table co ON ao.core_lib_output_ID = co.core_lib_output_ID
            JOIN core_lib_table cl ON co.core_lib_ID = cl.core_lib_ID
            JOIN video_table v ON co.video_ID = v.video_ID
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY v.video_date, al.algorithm_ID"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def get_latest_algorithm_version(db_path: str = "database.db") -> Optional[Dict]:
    """
    最新のアルゴリズムバージョンを取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        dict or None: 最新のアルゴリズム情報（レコードがない場合はNone）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT algorithm_ID, algorithm_version, algorithm_update_information, 
                   algorithm_base_version_ID, algorithm_commit_hash
            FROM algorithm_table
            ORDER BY algorithm_ID DESC
            LIMIT 1
            """
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
