"""
コアライブラリ管理API
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


def create_core_lib_version(version: str, update_info: str, commit_hash: str, 
                          base_version_id: Optional[int] = None,
                          db_path: str = "database.db") -> int:
    """
    新しいコアライブラリバージョンを登録
    
    Args:
        version: バージョン文字列（例: 1.0.0）
        update_info: 更新内容の説明
        commit_hash: Gitコミットハッシュ（40文字）
        base_version_id: ベースバージョンのID（新規の場合はNone）
        db_path: データベースファイルのパス
    
    Returns:
        core_lib_ID: 作成されたコアライブラリのID
    
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
                INSERT INTO core_lib_table 
                (core_lib_version, core_lib_update_information, core_lib_base_version_ID, core_lib_commit_hash)
                VALUES (?, ?, ?, ?)
                """,
                (version, update_info, base_version_id, commit_hash)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) and "core_lib_commit_hash" in str(e):
                raise DWHUniqueConstraintError(
                    f"Commit hash already exists: {commit_hash}",
                    table_name="core_lib_table",
                    field_name="core_lib_commit_hash"
                ) from e
            elif "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Base version not found: core_lib_ID={base_version_id}",
                    table_name="core_lib_table",
                    constraint_name="FK_base_version"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to create core library version: {e}", table_name="core_lib_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create core library version: {e}", table_name="core_lib_table") from e


def get_core_lib_version(core_lib_id: int, db_path: str = "database.db") -> Dict:
    """
    コアライブラリIDでバージョン情報を取得
    
    Args:
        core_lib_id: コアライブラリID
        db_path: データベースファイルのパス
    
    Returns:
        dict: コアライブラリ情報
    
    Raises:
        DWHNotFoundError: コアライブラリが見つからない場合
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT core_lib_ID, core_lib_version, core_lib_update_information, 
                   core_lib_base_version_ID, core_lib_commit_hash
            FROM core_lib_table
            WHERE core_lib_ID = ?
            """,
            (core_lib_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Core library not found: core_lib_ID={core_lib_id}",
                table_name="core_lib_table",
                record_id=core_lib_id
            )
        
        return dict(row)


def list_core_lib_versions(db_path: str = "database.db") -> List[Dict]:
    """
    コアライブラリバージョン一覧を取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: コアライブラリ情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT core_lib_ID, core_lib_version, core_lib_update_information, 
                   core_lib_base_version_ID, core_lib_commit_hash
            FROM core_lib_table
            ORDER BY core_lib_ID
            """
        )
        
        return [dict(row) for row in cursor.fetchall()]


def get_core_lib_version_history(core_lib_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    コアライブラリのバージョン履歴を取得（自己参照をたどる）
    
    Args:
        core_lib_id: 現在のコアライブラリID
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: バージョン履歴のリスト（古い順）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 再帰的にバージョン履歴を取得
        history = []
        current_id = core_lib_id
        
        while current_id is not None:
            cursor.execute(
                """
                SELECT core_lib_ID, core_lib_version, core_lib_update_information, 
                       core_lib_base_version_ID, core_lib_commit_hash
                FROM core_lib_table
                WHERE core_lib_ID = ?
                """,
                (current_id,)
            )
            
            row = cursor.fetchone()
            if row is None:
                break
            
            history.append(dict(row))
            current_id = row['core_lib_base_version_ID']
        
        # 古い順に並べ替え
        return list(reversed(history))


def find_core_lib_by_version(version: str, db_path: str = "database.db") -> Optional[Dict]:
    """
    バージョン文字列でコアライブラリを検索
    
    Args:
        version: バージョン文字列
        db_path: データベースファイルのパス
    
    Returns:
        dict or None: コアライブラリ情報（見つからない場合はNone）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT core_lib_ID, core_lib_version, core_lib_update_information, 
                   core_lib_base_version_ID, core_lib_commit_hash
            FROM core_lib_table
            WHERE core_lib_version = ?
            """,
            (version,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None


def find_core_lib_by_commit_hash(commit_hash: str, db_path: str = "database.db") -> Optional[Dict]:
    """
    コミットハッシュでコアライブラリを検索
    
    Args:
        commit_hash: コミットハッシュ
        db_path: データベースファイルのパス
    
    Returns:
        dict or None: コアライブラリ情報（見つからない場合はNone）
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT core_lib_ID, core_lib_version, core_lib_update_information, 
                   core_lib_base_version_ID, core_lib_commit_hash
            FROM core_lib_table
            WHERE core_lib_commit_hash = ?
            """,
            (commit_hash,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None


def create_core_lib_output(core_lib_id: int, video_id: int, output_dir: str,
                          db_path: str = "database.db") -> int:
    """
    コアライブラリの評価結果を登録
    
    Args:
        core_lib_id: コアライブラリID
        video_id: ビデオID
        output_dir: 出力ディレクトリパス
        db_path: データベースファイルのパス
    
    Returns:
        core_lib_output_ID: 作成された出力のID
    
    Raises:
        DWHConstraintError: コアライブラリまたはビデオが存在しない場合
    """
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO core_lib_output_table (core_lib_ID, video_ID, core_lib_output_dir)
                VALUES (?, ?, ?)
                """,
                (core_lib_id, video_id, output_dir)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Core library or video not found: core_lib_ID={core_lib_id}, video_ID={video_id}",
                    table_name="core_lib_output_table",
                    constraint_name="FK_core_lib_video"
                ) from e
            else:
                raise DWHConstraintError(f"Failed to create core library output: {e}", table_name="core_lib_output_table") from e
        except sqlite3.Error as e:
            raise DWHConstraintError(f"Failed to create core library output: {e}", table_name="core_lib_output_table") from e


def get_core_lib_output(output_id: int, db_path: str = "database.db") -> Dict:
    """
    コアライブラリ出力IDで出力情報を取得
    
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
            SELECT co.core_lib_output_ID, co.core_lib_ID, co.video_ID, co.core_lib_output_dir,
                   cl.core_lib_version, cl.core_lib_commit_hash,
                   v.video_dir, v.video_date
            FROM core_lib_output_table co
            JOIN core_lib_table cl ON co.core_lib_ID = cl.core_lib_ID
            JOIN video_table v ON co.video_ID = v.video_ID
            WHERE co.core_lib_output_ID = ?
            """,
            (output_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Core library output not found: core_lib_output_ID={output_id}",
                table_name="core_lib_output_table",
                record_id=output_id
            )
        
        return dict(row)


def list_core_lib_outputs(core_lib_id: Optional[int] = None, video_id: Optional[int] = None,
                         db_path: str = "database.db") -> List[Dict]:
    """
    コアライブラリ出力一覧を取得
    
    Args:
        core_lib_id: コアライブラリID（指定時はそのバージョンのみ）
        video_id: ビデオID（指定時はそのビデオのみ）
        db_path: データベースファイルのパス
    
    Returns:
        List[dict]: 出力情報のリスト
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 条件の構築
        conditions = []
        params = []
        
        if core_lib_id is not None:
            conditions.append("co.core_lib_ID = ?")
            params.append(core_lib_id)
        
        if video_id is not None:
            conditions.append("co.video_ID = ?")
            params.append(video_id)
        
        # SQL構築
        sql = """
            SELECT co.core_lib_output_ID, co.core_lib_ID, co.video_ID, co.core_lib_output_dir,
                   cl.core_lib_version, cl.core_lib_commit_hash,
                   v.video_dir, v.video_date
            FROM core_lib_output_table co
            JOIN core_lib_table cl ON co.core_lib_ID = cl.core_lib_ID
            JOIN video_table v ON co.video_ID = v.video_ID
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY v.video_date, cl.core_lib_ID"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
