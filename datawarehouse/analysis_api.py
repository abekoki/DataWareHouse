"""
課題分析管理API

本モジュールは、以下の3テーブルに対するCRUDおよび検証ロジックを提供します。
- analysis_result_table
- problem_table
- analysis_data_table

アプリケーションレベル検証ポリシー:
- analysis_data_isproblem が 1 のとき、problem_ID は必須（NOT NULL 相当）
- analysis_data_isproblem が 0 のとき、problem_ID は NULL を許容
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

from .exceptions import (
    DWHNotFoundError,
    DWHConstraintError,
    DWHValidationError,
)
from .connection import get_connection


def _validate_timestamp_format(timestamp_text: Optional[str]) -> None:
    """YYYY-MM-DD HH:MM:SS 形式の簡易検証"""
    if timestamp_text is None or timestamp_text == "":
        return
    try:
        datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise DWHValidationError(
            f"Invalid datetime format: {timestamp_text}. Expected YYYY-MM-DD HH:MM:SS",
            field_name="analysis_timestamp",
            field_value=timestamp_text,
        )


# =============== analysis_result_table ===============

def create_analysis_result(
    analysis_result_dir: str,
    evaluation_result_id: int,
    analysis_timestamp: Optional[str] = None,
    db_path: str = "database.db",
) -> int:
    """
    課題分析結果（1実行あたり1レコード）を登録。
    - analysis_result_dir: database.dbからの相対パス
    - analysis_timestamp: "YYYY-MM-DD HH:MM:SS"（未指定可, JST基準）
    """
    _validate_timestamp_format(analysis_timestamp)

    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_result_table
                (analysis_result_dir, analysis_timestamp, evaluation_result_ID)
                VALUES (?, ?, ?)
                """,
                (analysis_result_dir, analysis_timestamp, evaluation_result_id),
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Evaluation result not found: evaluation_result_ID={evaluation_result_id}",
                    table_name="analysis_result_table",
                    constraint_name="FK_evaluation_result",
                ) from e
            raise DWHConstraintError(
                f"Failed to create analysis result: {e}",
                table_name="analysis_result_table",
            ) from e


def get_analysis_result(analysis_result_id: int, db_path: str = "database.db") -> Dict:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT analysis_result_ID, analysis_result_dir, analysis_timestamp, evaluation_result_ID
            FROM analysis_result_table
            WHERE analysis_result_ID = ?
            """,
            (analysis_result_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Analysis result not found: analysis_result_ID={analysis_result_id}",
                table_name="analysis_result_table",
                record_id=analysis_result_id,
            )
        return dict(row)


def list_analysis_results(
    evaluation_result_id: Optional[int] = None, db_path: str = "database.db"
) -> List[Dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if evaluation_result_id is None:
            cursor.execute(
                """
                SELECT analysis_result_ID, analysis_result_dir, analysis_timestamp, evaluation_result_ID
                FROM analysis_result_table
                ORDER BY analysis_result_ID DESC
                """
            )
            return [dict(r) for r in cursor.fetchall()]
        cursor.execute(
            """
            SELECT analysis_result_ID, analysis_result_dir, analysis_timestamp, evaluation_result_ID
            FROM analysis_result_table
            WHERE evaluation_result_ID = ?
            ORDER BY analysis_result_ID DESC
            """,
            (evaluation_result_id,),
        )
        return [dict(r) for r in cursor.fetchall()]


# =============== problem_table ===============

def create_problem(
    problem_name: str,
    problem_description: str,
    problem_status: str,
    analysis_result_id: int,
    db_path: str = "database.db",
) -> int:
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO problem_table
                (problem_name, problem_description, problem_status, analysis_result_ID)
                VALUES (?, ?, ?, ?)
                """,
                (problem_name, problem_description, problem_status, analysis_result_id),
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Analysis result not found: analysis_result_ID={analysis_result_id}",
                    table_name="problem_table",
                    constraint_name="FK_analysis_result",
                ) from e
            raise DWHConstraintError(
                f"Failed to create problem: {e}",
                table_name="problem_table",
            ) from e


def get_problem(problem_id: int, db_path: str = "database.db") -> Dict:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT problem_ID, problem_name, problem_description, problem_status, analysis_result_ID
            FROM problem_table
            WHERE problem_ID = ?
            """,
            (problem_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Problem not found: problem_ID={problem_id}",
                table_name="problem_table",
                record_id=problem_id,
            )
        return dict(row)


def list_problems(
    analysis_result_id: Optional[int] = None, db_path: str = "database.db"
) -> List[Dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if analysis_result_id is None:
            cursor.execute(
                """
                SELECT problem_ID, problem_name, problem_description, problem_status, analysis_result_ID
                FROM problem_table
                ORDER BY problem_ID DESC
                """
            )
            return [dict(r) for r in cursor.fetchall()]
        cursor.execute(
            """
            SELECT problem_ID, problem_name, problem_description, problem_status, analysis_result_ID
            FROM problem_table
            WHERE analysis_result_ID = ?
            ORDER BY problem_ID DESC
            """,
            (analysis_result_id,),
        )
        return [dict(r) for r in cursor.fetchall()]


# =============== analysis_data_table ===============

def create_analysis_data(
    evaluation_data_id: int,
    analysis_result_id: int,
    analysis_data_isproblem: int,
    analysis_data_dir: str,
    analysis_data_description: str,
    problem_id: Optional[int] = None,
    db_path: str = "database.db",
) -> int:
    """
    課題分析データの登録。
    - analysis_data_isproblem: 0 or 1
    - analysis_data_isproblem == 1 の場合、problem_id は必須
    - analysis_data_dir: database.dbからの相対パス
    """
    if analysis_data_isproblem not in (0, 1):
        raise DWHValidationError(
            f"analysis_data_isproblem must be 0 or 1: {analysis_data_isproblem}",
            field_name="analysis_data_isproblem",
            field_value=analysis_data_isproblem,
        )
    if analysis_data_isproblem == 1 and not problem_id:
        raise DWHValidationError(
            "problem_ID is required when analysis_data_isproblem == 1",
            field_name="problem_ID",
            field_value=problem_id,
        )

    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_data_table
                (evaluation_data_ID, analysis_result_ID, problem_ID, analysis_data_isproblem, analysis_data_dir, analysis_data_description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation_data_id,
                    analysis_result_id,
                    problem_id,
                    analysis_data_isproblem,
                    analysis_data_dir,
                    analysis_data_description,
                ),
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    (
                        f"FK not found: evaluation_data_ID={evaluation_data_id}, "
                        f"analysis_result_ID={analysis_result_id}, problem_ID={problem_id}"
                    ),
                    table_name="analysis_data_table",
                    constraint_name="FKs_analysis_data",
                ) from e
            raise DWHConstraintError(
                f"Failed to create analysis data: {e}",
                table_name="analysis_data_table",
            ) from e


def list_analysis_data(
    analysis_result_id: Optional[int] = None,
    evaluation_data_id: Optional[int] = None,
    db_path: str = "database.db",
) -> List[Dict]:
    """分析データの一覧取得（任意フィルタ）"""
    where = []
    params: List = []
    if analysis_result_id is not None:
        where.append("ad.analysis_result_ID = ?")
        params.append(analysis_result_id)
    if evaluation_data_id is not None:
        where.append("ad.evaluation_data_ID = ?")
        params.append(evaluation_data_id)

    sql = (
        """
        SELECT ad.analysis_data_ID, ad.evaluation_data_ID, ad.analysis_result_ID, ad.problem_ID,
               ad.analysis_data_isproblem, ad.analysis_data_dir, ad.analysis_data_description
        FROM analysis_data_table ad
        """
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY ad.analysis_data_ID DESC"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return [dict(r) for r in cursor.fetchall()]


