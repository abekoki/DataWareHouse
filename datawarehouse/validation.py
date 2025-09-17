"""
DataWareHouse データベーススキーマ検証モジュール

このモジュールは、既存のデータベースがDataWareHouseが想定する
正しいスキーマ構造を持っているかを検証する機能を提供します。
"""

import sqlite3
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from .connection import get_connection
from .exceptions import DWHError, DWHValidationError


class SchemaValidator:
    """データベーススキーマ検証クラス"""

    # 想定されるテーブル構造定義
    EXPECTED_TABLES = {
        'task_table': {
            'columns': {
                'task_ID': ('INTEGER', True, True),  # (type, not_null, primary_key)
                'task_set': ('INTEGER', False, False),
                'task_name': ('TEXT', False, False),
                'task_describe': ('TEXT', False, False)
            },
            'foreign_keys': []
        },
        'subject_table': {
            'columns': {
                'subject_ID': ('INTEGER', True, True),
                'subject_name': ('TEXT', False, False)
            },
            'foreign_keys': []
        },
        'video_table': {
            'columns': {
                'video_ID': ('INTEGER', True, True),
                'video_dir': ('TEXT', False, False),
                'subject_ID': ('INTEGER', False, False),
                'video_date': ('TEXT', False, False),
                'video_length': ('INTEGER', False, False)
            },
            'foreign_keys': [
                ('subject_ID', 'subject_table', 'subject_ID')
            ]
        },
        'tag_table': {
            'columns': {
                'tag_ID': ('INTEGER', True, True),
                'video_ID': ('INTEGER', False, False),
                'task_ID': ('INTEGER', False, False),
                'start': ('INTEGER', False, False),
                'end': ('INTEGER', False, False)
            },
            'foreign_keys': [
                ('video_ID', 'video_table', 'video_ID'),
                ('task_ID', 'task_table', 'task_ID')
            ]
        },
        'core_lib_table': {
            'columns': {
                'core_lib_ID': ('INTEGER', True, True),
                'core_lib_version': ('TEXT', False, False),
                'core_lib_update_information': ('TEXT', False, False),
                'core_lib_base_version_ID': ('INTEGER', False, False),
                'core_lib_commit_hash': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('core_lib_base_version_ID', 'core_lib_table', 'core_lib_ID')
            ]
        },
        'core_lib_output_table': {
            'columns': {
                'core_lib_output_ID': ('INTEGER', True, True),
                'core_lib_ID': ('INTEGER', False, False),
                'video_ID': ('INTEGER', False, False),
                'core_lib_output_dir': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('core_lib_ID', 'core_lib_table', 'core_lib_ID'),
                ('video_ID', 'video_table', 'video_ID')
            ]
        },
        'algorithm_table': {
            'columns': {
                'algorithm_ID': ('INTEGER', True, True),
                'algorithm_version': ('TEXT', False, False),
                'algorithm_update_information': ('TEXT', False, False),
                'algorithm_base_version_ID': ('INTEGER', False, False),
                'algorithm_commit_hash': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('algorithm_base_version_ID', 'algorithm_table', 'algorithm_ID')
            ]
        },
        'algorithm_output_table': {
            'columns': {
                'algorithm_output_ID': ('INTEGER', True, True),
                'algorithm_ID': ('INTEGER', False, False),
                'core_lib_output_ID': ('INTEGER', False, False),
                'algorithm_output_dir': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('algorithm_ID', 'algorithm_table', 'algorithm_ID'),
                ('core_lib_output_ID', 'core_lib_output_table', 'core_lib_output_ID')
            ]
        },
        'evaluation_result_table': {
            'columns': {
                'evaluation_result_ID': ('INTEGER', True, True),
                'version': ('TEXT', False, False),
                'algorithm_ID': ('INTEGER', False, False),
                'true_positive': ('REAL', False, False),
                'false_positive': ('REAL', False, False),
                'evaluation_result_dir': ('TEXT', False, False),
                'evaluation_timestamp': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('algorithm_ID', 'algorithm_table', 'algorithm_ID')
            ]
        },
        'evaluation_data_table': {
            'columns': {
                'evaluation_data_ID': ('INTEGER', True, True),
                'evaluation_result_ID': ('INTEGER', False, False),
                'algorithm_output_ID': ('INTEGER', False, False),
                'correct_task_num': ('INTEGER', False, False),
                'total_task_num': ('INTEGER', False, False),
                'evaluation_data_path': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('evaluation_result_ID', 'evaluation_result_table', 'evaluation_result_ID'),
                ('algorithm_output_ID', 'algorithm_output_table', 'algorithm_output_ID')
            ]
        },
        'analysis_result_table': {
            'columns': {
                'analysis_result_ID': ('INTEGER', True, True),
                'analysis_result_dir': ('TEXT', False, False),
                'analysis_timestamp': ('TEXT', False, False),
                'evaluation_result_ID': ('INTEGER', False, False)
            },
            'foreign_keys': [
                ('evaluation_result_ID', 'evaluation_result_table', 'evaluation_result_ID')
            ]
        },
        'problem_table': {
            'columns': {
                'problem_ID': ('INTEGER', True, True),
                'problem_name': ('TEXT', False, False),
                'problem_description': ('TEXT', False, False),
                'problem_status': ('TEXT', False, False),
                'analysis_result_ID': ('INTEGER', False, False)
            },
            'foreign_keys': [
                ('analysis_result_ID', 'analysis_result_table', 'analysis_result_ID')
            ]
        },
        'analysis_data_table': {
            'columns': {
                'analysis_data_ID': ('INTEGER', True, True),
                'evaluation_data_ID': ('INTEGER', False, False),
                'analysis_result_ID': ('INTEGER', False, False),
                'problem_ID': ('INTEGER', False, False),
                'analysis_data_isproblem': ('INTEGER', False, False),
                'analysis_data_dir': ('TEXT', False, False),
                'analysis_data_description': ('TEXT', False, False)
            },
            'foreign_keys': [
                ('evaluation_data_ID', 'evaluation_data_table', 'evaluation_data_ID'),
                ('analysis_result_ID', 'analysis_result_table', 'analysis_result_ID'),
                ('problem_ID', 'problem_table', 'problem_ID')
            ]
        }
    }

    # 推奨インデックス
    EXPECTED_INDEXES = {
        'idx_core_lib_version': 'core_lib_table(core_lib_version)',
        'idx_algorithm_version': 'algorithm_table(algorithm_version)'
    }

    def __init__(self, db_path: str):
        """
        初期化

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []

    def validate_schema(self) -> Dict:
        """
        データベーススキーマを検証する

        Returns:
            Dict: 検証結果
                {
                    'is_valid': bool,
                    'issues': List[Dict],      # 重大な問題
                    'warnings': List[Dict],    # 警告
                    'tables_found': List[str],
                    'tables_missing': List[str],
                    'indexes_found': List[str],
                    'indexes_missing': List[str]
                }
        """
        try:
            with get_connection(self.db_path) as conn:
                return self._validate_schema_internal(conn)
        except Exception as e:
            raise DWHError(f"スキーマ検証中にエラーが発生しました: {e}")

    def _validate_schema_internal(self, conn: sqlite3.Connection) -> Dict:
        """内部検証処理"""
        self.issues = []
        self.warnings = []

        # 既存テーブルの取得
        existing_tables = self._get_existing_tables(conn)
        existing_indexes = self._get_existing_indexes(conn)

        # 欠落テーブルのチェック
        missing_tables = []
        found_tables = []

        for expected_table in self.EXPECTED_TABLES.keys():
            if expected_table in existing_tables:
                found_tables.append(expected_table)
                # テーブル構造の検証
                self._validate_table_structure(conn, expected_table)
            else:
                missing_tables.append(expected_table)
                self.issues.append({
                    'type': 'missing_table',
                    'table': expected_table,
                    'message': f"テーブル '{expected_table}' が存在しません"
                })

        # インデックスのチェック
        missing_indexes = []
        found_indexes = []

        for index_name, index_def in self.EXPECTED_INDEXES.items():
            if index_name in existing_indexes:
                found_indexes.append(index_name)
            else:
                missing_indexes.append(index_name)
                self.warnings.append({
                    'type': 'missing_index',
                    'index': index_name,
                    'table': index_def.split('(')[0],
                    'message': f"推奨インデックス '{index_name}' が存在しません"
                })

        # 外部キー制約の有効性チェック
        self._validate_foreign_keys(conn)

        # 結果の整理
        result = {
            'is_valid': len(self.issues) == 0,
            'issues': self.issues,
            'warnings': self.warnings,
            'tables_found': found_tables,
            'tables_missing': missing_tables,
            'indexes_found': found_indexes,
            'indexes_missing': missing_indexes,
            'summary': {
                'total_tables_expected': len(self.EXPECTED_TABLES),
                'total_tables_found': len(found_tables),
                'total_tables_missing': len(missing_tables),
                'total_indexes_expected': len(self.EXPECTED_INDEXES),
                'total_indexes_found': len(found_indexes),
                'total_indexes_missing': len(missing_indexes),
                'total_issues': len(self.issues),
                'total_warnings': len(self.warnings)
            }
        }

        return result

    def _get_existing_tables(self, conn: sqlite3.Connection) -> List[str]:
        """既存テーブルの一覧を取得"""
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        return [row[0] for row in cursor.fetchall()]

    def _get_existing_indexes(self, conn: sqlite3.Connection) -> List[str]:
        """既存インデックスの一覧を取得"""
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        return [row[0] for row in cursor.fetchall()]

    def _validate_table_structure(self, conn: sqlite3.Connection, table_name: str):
        """テーブル構造を検証"""
        try:
            # 実際のカラム情報を取得
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            actual_columns = {}
            for row in cursor.fetchall():
                col_name = row[1]
                col_type = row[2].upper()
                not_null = bool(row[3])
                primary_key = bool(row[5])
                actual_columns[col_name] = (col_type, not_null, primary_key)

            expected_table = self.EXPECTED_TABLES[table_name]

            # 欠落カラムのチェック
            for expected_col, (exp_type, exp_not_null, exp_pk) in expected_table['columns'].items():
                if expected_col not in actual_columns:
                    self.issues.append({
                        'type': 'missing_column',
                        'table': table_name,
                        'column': expected_col,
                        'message': f"テーブル '{table_name}' にカラム '{expected_col}' が存在しません"
                    })
                else:
                    # 型と制約のチェック
                    act_type, act_not_null, act_pk = actual_columns[expected_col]

                    # 型の互換性チェック（SQLiteは動的型付けなので柔軟に）
                    if not self._is_type_compatible(exp_type, act_type):
                        self.warnings.append({
                            'type': 'type_mismatch',
                            'table': table_name,
                            'column': expected_col,
                            'expected': exp_type,
                            'actual': act_type,
                            'message': f"テーブル '{table_name}' のカラム '{expected_col}' の型が期待値と異なります (期待: {exp_type}, 実際: {act_type})"
                        })

                    # 主キーのチェック
                    if exp_pk != act_pk:
                        self.issues.append({
                            'type': 'primary_key_mismatch',
                            'table': table_name,
                            'column': expected_col,
                            'message': f"テーブル '{table_name}' のカラム '{expected_col}' の主キー設定が正しくありません"
                        })

            # 余分なカラムの警告
            expected_columns = set(expected_table['columns'].keys())
            actual_columns_set = set(actual_columns.keys())

            extra_columns = actual_columns_set - expected_columns
            if extra_columns:
                for extra_col in extra_columns:
                    self.warnings.append({
                        'type': 'extra_column',
                        'table': table_name,
                        'column': extra_col,
                        'message': f"テーブル '{table_name}' に予期しないカラム '{extra_col}' が存在します"
                    })

        except Exception as e:
            self.issues.append({
                'type': 'table_validation_error',
                'table': table_name,
                'message': f"テーブル '{table_name}' の検証中にエラーが発生しました: {e}"
            })

    def _validate_foreign_keys(self, conn: sqlite3.Connection):
        """外部キー制約を検証"""
        try:
            # 外部キー制約が有効化されているかチェック
            cursor = conn.execute("PRAGMA foreign_keys")
            fk_enabled = cursor.fetchone()[0]

            if not fk_enabled:
                self.warnings.append({
                    'type': 'foreign_keys_disabled',
                    'message': "外部キー制約が無効化されています。PRAGMA foreign_keys = ON; を実行してください"
                })
                return

            # 各テーブルの外部キー制約をチェック
            for table_name, table_info in self.EXPECTED_TABLES.items():
                try:
                    cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
                    actual_fks = []
                    for row in cursor.fetchall():
                        actual_fks.append((row[3], row[2], row[4]))  # (from_col, to_table, to_col)

                    expected_fks = table_info['foreign_keys']

                    # 欠落外部キーのチェック
                    for exp_fk in expected_fks:
                        exp_from, exp_to_table, exp_to_col = exp_fk
                        if exp_fk not in actual_fks:
                            self.issues.append({
                                'type': 'missing_foreign_key',
                                'table': table_name,
                                'from_column': exp_from,
                                'to_table': exp_to_table,
                                'to_column': exp_to_col,
                                'message': f"テーブル '{table_name}' の外部キー制約が欠落しています: {exp_from} -> {exp_to_table}.{exp_to_col}"
                            })

                except Exception as e:
                    self.warnings.append({
                        'type': 'fk_validation_error',
                        'table': table_name,
                        'message': f"テーブル '{table_name}' の外部キー検証中にエラーが発生しました: {e}"
                    })

        except Exception as e:
            self.warnings.append({
                'type': 'foreign_key_check_error',
                'message': f"外部キー制約の検証中にエラーが発生しました: {e}"
            })

    def _is_type_compatible(self, expected_type: str, actual_type: str) -> bool:
        """型の互換性をチェック（SQLiteの動的型付けを考慮）"""
        # SQLiteは動的型付けなので、基本的にTEXTとINTEGER/REALは互換性がある
        if expected_type == actual_type:
            return True

        # 互換性のある型の組み合わせ
        compatible_types = {
            'INTEGER': ['TEXT', 'REAL'],
            'REAL': ['TEXT', 'INTEGER'],
            'TEXT': ['INTEGER', 'REAL']
        }

        return actual_type in compatible_types.get(expected_type, [])

    def get_validation_report(self, validation_result: Dict) -> str:
        """検証結果を人間可読なレポート形式で返す"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DataWareHouse データベーススキーマ検証レポート")
        report_lines.append("=" * 60)
        report_lines.append(f"データベース: {self.db_path}")
        report_lines.append("")

        # サマリー
        summary = validation_result['summary']
        report_lines.append("サマリー:")
        report_lines.append(f"  想定テーブル数: {summary['total_tables_expected']}")
        report_lines.append(f"  検出テーブル数: {summary['total_tables_found']}")
        report_lines.append(f"  欠落テーブル数: {summary['total_tables_missing']}")
        report_lines.append(f"  検出インデックス数: {summary['total_indexes_found']}")
        report_lines.append(f"  欠落インデックス数: {summary['total_indexes_missing']}")
        report_lines.append(f"  重大問題数: {summary['total_issues']}")
        report_lines.append(f"  警告数: {summary['total_warnings']}")
        report_lines.append("")

        # 全体的なステータス
        if validation_result['is_valid']:
            report_lines.append("✅ 検証結果: 有効なDataWareHouseスキーマです")
        else:
            report_lines.append("❌ 検証結果: スキーマに問題があります")
        report_lines.append("")

        # 重大問題
        if validation_result['issues']:
            report_lines.append("🚨 重大問題:")
            for issue in validation_result['issues']:
                report_lines.append(f"  • {issue['message']}")
            report_lines.append("")

        # 警告
        if validation_result['warnings']:
            report_lines.append("⚠️  警告:")
            for warning in validation_result['warnings']:
                report_lines.append(f"  • {warning['message']}")
            report_lines.append("")

        # 検出されたテーブル
        if validation_result['tables_found']:
            report_lines.append("📋 検出されたテーブル:")
            for table in sorted(validation_result['tables_found']):
                report_lines.append(f"  • {table}")
            report_lines.append("")

        # 欠落テーブル
        if validation_result['tables_missing']:
            report_lines.append("❓ 欠落テーブル:")
            for table in sorted(validation_result['tables_missing']):
                report_lines.append(f"  • {table}")
            report_lines.append("")

        # 検出されたインデックス
        if validation_result['indexes_found']:
            report_lines.append("🔍 検出されたインデックス:")
            for index in sorted(validation_result['indexes_found']):
                report_lines.append(f"  • {index}")
            report_lines.append("")

        # 欠落インデックス
        if validation_result['indexes_missing']:
            report_lines.append("📎 欠落インデックス:")
            for index in sorted(validation_result['indexes_missing']):
                report_lines.append(f"  • {index}")
            report_lines.append("")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)


def validate_database_schema(db_path: str) -> Dict:
    """
    データベーススキーマを検証する

    Args:
        db_path: データベースファイルのパス

    Returns:
        Dict: 検証結果
    """
    validator = SchemaValidator(db_path)
    return validator.validate_schema()


def get_schema_validation_report(db_path: str) -> str:
    """
    データベーススキーマ検証レポートを取得する

    Args:
        db_path: データベースファイルのパス

    Returns:
        str: 検証レポート
    """
    validator = SchemaValidator(db_path)
    result = validator.validate_schema()
    return validator.get_validation_report(result)


def check_database_compatibility(db_path: str) -> bool:
    """
    データベースがDataWareHouseと互換性があるかをチェックする

    Args:
        db_path: データベースファイルのパス

    Returns:
        bool: 互換性がある場合True
    """
    try:
        result = validate_database_schema(db_path)
        return result['is_valid']
    except Exception:
        return False
