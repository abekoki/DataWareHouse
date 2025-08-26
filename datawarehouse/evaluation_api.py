"""
評価管理API
"""

import sqlite3
from typing import List, Dict, Optional
from .exceptions import DWHNotFoundError, DWHConstraintError, DWHValidationError
from .connection import get_connection


def create_evaluation_result(
    version: str,
    algorithm_id: int,
    true_positive: float,
    false_positive: Optional[float] = None,
    evaluation_result_dir: str = "",
    evaluation_timestamp: Optional[str] = None,
    db_path: str = "database.db",
) -> int:
    """
    評価結果（集計）のレコードを登録。

    - false_positive: 1時間当たりの過検知数 [回/h]（0.0〜上限なし、未設定可）
    - evaluation_result_dir: database.dbからの相対パス
    """
    # 値検証
    if not (0.0 <= true_positive <= 1.0):
        raise DWHValidationError(
            f"true_positive must be between 0.0 and 1.0: {true_positive}",
            field_name="true_positive",
            field_value=true_positive,
        )
    if false_positive is not None and false_positive < 0.0:
        raise DWHValidationError(
            f"false_positive must be >= 0.0: {false_positive}",
            field_name="false_positive",
            field_value=false_positive,
        )

    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO evaluation_result_table
                (version, algorithm_ID, true_positive, false_positive, evaluation_result_dir, evaluation_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (version, algorithm_id, true_positive, false_positive, evaluation_result_dir, evaluation_timestamp),
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    f"Algorithm not found: algorithm_ID={algorithm_id}",
                    table_name="evaluation_result_table",
                    constraint_name="FK_algorithm",
                ) from e
            raise DWHConstraintError(
                f"Failed to create evaluation result: {e}",
                table_name="evaluation_result_table",
            ) from e
        except sqlite3.Error as e:
            raise DWHConstraintError(
                f"Failed to create evaluation result: {e}",
                table_name="evaluation_result_table",
            ) from e


def get_evaluation_result(evaluation_result_id: int, db_path: str = "database.db") -> Dict:
    """
    評価結果の単一取得。
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT evaluation_result_ID, version, algorithm_ID, true_positive, false_positive,
                   evaluation_result_dir, evaluation_timestamp
            FROM evaluation_result_table
            WHERE evaluation_result_ID = ?
            """,
            (evaluation_result_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise DWHNotFoundError(
                f"Evaluation result not found: evaluation_result_ID={evaluation_result_id}",
                table_name="evaluation_result_table",
                record_id=evaluation_result_id,
            )
        return dict(row)


def list_evaluation_results(
    algorithm_id: Optional[int] = None,
    version: Optional[str] = None,
    db_path: str = "database.db",
) -> List[Dict]:
    """
    条件で評価結果を一覧取得。
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        conditions = []
        params = []
        if algorithm_id is not None:
            conditions.append("algorithm_ID = ?")
            params.append(algorithm_id)
        if version is not None:
            conditions.append("version = ?")
            params.append(version)

        sql = (
            "SELECT evaluation_result_ID, version, algorithm_ID, true_positive, false_positive, "
            "evaluation_result_dir, evaluation_timestamp FROM evaluation_result_table"
        )
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY evaluation_result_ID DESC"

        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def create_evaluation_data(
    evaluation_result_id: int,
    algorithm_output_id: int,
    correct_task_num: int,
    total_task_num: int,
    evaluation_data_path: str,
    db_path: str = "database.db",
) -> int:
    """
    個別データの評価結果を登録。
    - algorithm_output_id は algorithm_output_table.algorithm_output_ID を参照
    - correct_task_num <= total_task_num
    - evaluation_data_path は database.db からの相対パス
    """
    if correct_task_num < 0 or total_task_num < 0:
        raise DWHValidationError("Counts must be >= 0")
    if correct_task_num > total_task_num:
        raise DWHValidationError(
            "correct_task_num must be <= total_task_num",
            field_name="correct_task_num",
            field_value=correct_task_num,
        )

    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO evaluation_data_table
                (evaluation_result_ID, algorithm_output_ID, correct_task_num, total_task_num, evaluation_data_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    evaluation_result_id,
                    algorithm_output_id,
                    correct_task_num,
                    total_task_num,
                    evaluation_data_path,
                ),
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise DWHConstraintError(
                    (
                        f"FK not found: evaluation_result_ID={evaluation_result_id}, "
                        f"algorithm_output_ID={algorithm_output_id}"
                    ),
                    table_name="evaluation_data_table",
                    constraint_name="FK_eval_result_or_algo_output",
                ) from e
            raise DWHConstraintError(
                f"Failed to create evaluation data: {e}",
                table_name="evaluation_data_table",
            ) from e
        except sqlite3.Error as e:
            raise DWHConstraintError(
                f"Failed to create evaluation data: {e}",
                table_name="evaluation_data_table",
            ) from e


def list_evaluation_data(evaluation_result_id: int, db_path: str = "database.db") -> List[Dict]:
    """
    指定した評価結果IDに紐づく個別評価データを一覧取得。
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ed.evaluation_data_ID, ed.evaluation_result_ID, ed.algorithm_output_ID,
                   ed.correct_task_num, ed.total_task_num, ed.evaluation_data_path,
                   ao.algorithm_ID, ao.core_lib_output_ID
            FROM evaluation_data_table ed
            JOIN algorithm_output_table ao ON ed.algorithm_output_ID = ao.algorithm_output_ID
            WHERE ed.evaluation_result_ID = ?
            ORDER BY ed.evaluation_data_ID
            """,
            (evaluation_result_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_evaluation_overview(evaluation_result_id: int, db_path: str = "database.db") -> Dict:
    """
    評価概要（派生メトリクスを含む）を返す。
    accuracy = total_correct / total_items （0除算は0.0）
    """
    # ベース情報
    result = get_evaluation_result(evaluation_result_id, db_path)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(correct_task_num), 0) as total_correct,
                   COALESCE(SUM(total_task_num), 0) as total_items
            FROM evaluation_data_table
            WHERE evaluation_result_ID = ?
            """,
            (evaluation_result_id,),
        )
        row = cursor.fetchone()
        total_correct = int(row[0])
        total_items = int(row[1])

    accuracy = (total_correct / total_items) if total_items > 0 else 0.0

    return {
        "version": result["version"],
        "algorithm_ID": result["algorithm_ID"],
        "true_positive": result["true_positive"],
        "false_positive_per_hour": result["false_positive"],
        "total_items": total_items,
        "total_correct": total_correct,
        "accuracy": accuracy,
    }


