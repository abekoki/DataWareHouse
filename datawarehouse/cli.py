#!/usr/bin/env python3
"""
DataWareHouse CLI - コマンドラインインターフェース

このモジュールは、DataWareHouseライブラリのコマンドラインインターフェースを提供します。
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .connection import DWHConnection
from . import exceptions
from .validation import get_schema_validation_report, check_database_compatibility


def create_database(db_path: str, schema_path: Optional[str] = None) -> None:
    """
    データベースを作成・初期化する

    Args:
        db_path: データベースファイルのパス
        schema_path: スキーマファイルのパス（オプション）
    """
    try:
        # デフォルトのスキーマファイルを使用
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "00_design" / "schema.sql"

        if not schema_path.exists():
            print(f"エラー: スキーマファイルが見つかりません: {schema_path}")
            return

        # データベース接続
        with DWHConnection(db_path) as conn:
            # スキーマ読み込みと実行
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # SQL文を分割して実行
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

            for statement in statements:
                if statement:
                    conn.execute(statement)

        print(f"データベースを作成しました: {db_path}")

    except exceptions.DWHError as e:
        print(f"DataWareHouseエラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        sys.exit(1)


def show_database_info(db_path: str) -> None:
    """
    データベースの構造情報を表示する

    Args:
        db_path: データベースファイルのパス
    """
    try:
        with DWHConnection(db_path) as conn:
            # テーブル一覧を取得
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)

            tables = cursor.fetchall()

            if not tables:
                print("データベースにテーブルが見つかりません。")
                return

            print("=== DataWareHouse データベース構造 ===")
            print(f"データベース: {db_path}")
            print()

            for table_row in tables:
                table_name = table_row[0]
                print(f"テーブル: {table_name}")

                # カラム情報を取得
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                if columns:
                    print("  カラム:")
                    for col in columns:
                        col_name = col[1]
                        col_type = col[2]
                        is_pk = " (PK)" if col[5] else ""
                        print(f"    - {col_name} ({col_type}){is_pk}")

                # 外部キー情報を取得
                cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
                fks = cursor.fetchall()

                if fks:
                    print("  外部キー:")
                    for fk in fks:
                        fk_col = fk[3]
                        ref_table = fk[2]
                        ref_col = fk[4]
                        print(f"    - {fk_col} -> {ref_table}.{ref_col}")

                print()

    except exceptions.DWHError as e:
        print(f"DataWareHouseエラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        sys.exit(1)


def validate_schema(db_path: str) -> None:
    """
    データベーススキーマを検証する

    Args:
        db_path: データベースファイルのパス
    """
    try:
        print(f"データベーススキーマ検証中: {db_path}")
        print()

        # スキーマ検証レポートを取得
        report = get_schema_validation_report(db_path)
        print(report)

        # 互換性チェック
        is_compatible = check_database_compatibility(db_path)
        if is_compatible:
            print("✅ このデータベースはDataWareHouseと互換性があります")
            sys.exit(0)
        else:
            print("❌ このデータベースはDataWareHouseと互換性がありません")
            sys.exit(1)

    except exceptions.DWHError as e:
        print(f"DataWareHouseエラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        sys.exit(1)


def main() -> None:
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="DataWareHouse CLI - ビデオ処理評価システムのデータウェアハウス管理ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # データベースの作成
  dwh-cli create-db database.db

  # データベース構造の表示
  dwh-cli info database.db

  # データベーススキーマ検証
  dwh-cli validate database.db

  # ヘルプ表示
  dwh-cli --help
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='DataWareHouse CLI 0.1.0'
    )

    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')

    # create-db コマンド
    create_parser = subparsers.add_parser(
        'create-db',
        help='データベースを作成・初期化する'
    )
    create_parser.add_argument(
        'db_path',
        help='作成するデータベースファイルのパス'
    )
    create_parser.add_argument(
        '--schema',
        help='使用するスキーマファイルのパス（デフォルト: 00_design/schema.sql）'
    )

    # info コマンド
    info_parser = subparsers.add_parser(
        'info',
        help='データベースの構造情報を表示する'
    )
    info_parser.add_argument(
        'db_path',
        help='確認するデータベースファイルのパス'
    )

    # validate コマンド
    validate_parser = subparsers.add_parser(
        'validate',
        help='データベーススキーマを検証する'
    )
    validate_parser.add_argument(
        'db_path',
        help='検証するデータベースファイルのパス'
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == 'create-db':
        create_database(args.db_path, args.schema)
    elif args.command == 'info':
        show_database_info(args.db_path)
    elif args.command == 'validate':
        validate_schema(args.db_path)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
