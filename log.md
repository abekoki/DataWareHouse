## 2025-08-19
- 仕様書（`00_design/database_spec_with_timing.md`）を基に、SQLite スキーマを `00_design/schema.sql` として作成。
- 初期化スクリプト `scripts/create_database.py` を追加。`database.db` をプロジェクト直下に生成し、スキーマを適用する仕組み。
- `.gitignore` に `.venv/` を追記（uv 管理の仮想環境を除外）。
- 次アクション: スクリプトを実行して `database.db` を作成し、テーブル作成を確認。

## 2025-08-19
- `uv sync` のビルドエラー（hatchlingのファイル選定不可）対策として、空のパッケージ `datawarehouse/` を追加し、ビルド対象を明示。
- 次アクション: `uv sync` を再実行し、続けて `uv run python scripts/create_database.py` でDB作成。

## 2025-08-19
- データベース構造クエリスクリプト `scripts/query_db_structure.py` を作成。
- `database.db` の構造を確認: 8テーブル（task_table, subject_table, video_table, tag_table, core_lib_table, core_lib_output_table, algorithm_table, algorithm_output_table）が正しく作成済み。
- 全テーブルが0件（空の状態）、外部キー制約は未設定、バージョン検索用インデックスは作成済み。
- 仕様書通りの構造が正しく実装されていることを確認。

## 2025-08-19
- 外部キー制約の永続化を試行したが、SQLiteの制限により接続ごとの設定が必要であることを確認。
- `scripts/create_database.py` を修正し、既存データベース更新時はデータを保持するように改善。
- `.gitignore` を更新し、データベースファイル、Pythonキャッシュ、IDE設定、OS生成ファイルなどを除外。
- プロジェクト全体の整理が完了し、包括的な `README.md` を作成。セットアップ方法、使用方法、トラブルシューティングを含む。

## 2025-08-19
- API仕様書に基づいてDataWareHouse APIライブラリを完全実装。
- 8つのAPIモジュールを作成：exceptions, connection, task_api, subject_api, video_api, tag_api, core_lib_api, algorithm_api, analytics_api。
- 包括的なエラーハンドリング、データ検証、バージョン履歴管理、検索・分析機能を実装。
- 使用例（basic_usage.py, advanced_usage.py）とAPIライブラリドキュメント（api_library_documentation.md）を作成。
- 他のモジュールが簡単にDataWareHouseにアクセスできる完全なAPIライブラリが完成。

## 2025-01-15
- Serena MCPを使用してdatawarehouseパッケージの構造解析を実施。
- プロジェクトオンボーディングを実施し、メモリファイルに以下を記録：
  - project_overview.md: プロジェクト概要と主要機能
  - code_style_conventions.md: コードスタイルと規約
  - suggested_commands.md: 推奨コマンド
  - task_completion_checklist.md: タスク完了時のチェックリスト
- datawarehouseパッケージの詳細な構造解析を完了：
  - 10個のPythonモジュールからなる階層構造
  - 6つのカスタム例外クラス
  - 2つの接続管理機能
  - 8つの主要APIモジュール（タスク、被験者、ビデオ、タグ、コアライブラリ、アルゴリズム、出力、分析）
  - 合計50以上のAPI関数を提供する包括的なライブラリ構造
- 構造解析結果を00_design/ディレクトリの適切なドキュメントに追記・整理：
  - api_library_documentation.md: アーキテクチャ解析セクションを追加
  - database_structure_detailed.md: APIライブラリアーキテクチャセクションを追加
  - api_specification.md: 実装アーキテクチャセクションを追加
  - package_structure_analysis.md: 新規作成（詳細な構造解析書）
- 4層アーキテクチャ（基盤層・データ管理層・バージョン管理層・分析層・インターフェース層）の詳細解説
- モジュール間依存関係、テーブル-APIマッピング、設計原則の体系化
- 企業レベルの品質を持つAPIライブラリとしての評価と改善提案を文書化

## 2025-08-20
- パス記録仕様の明確化：すべてのディレクトリ・ファイルパスはdatabase.dbからの相対パスで記録
- 以下の仕様書に相対パス記録の詳細を追加：
  - database_spec_with_timing.md: video_dir, core_lib_output_dir, algorithm_output_dirの説明に相対パス仕様を明記
  - database_structure_detailed.md: パス記録仕様セクションを新規追加、具体例とAPIでの処理方法を説明
  - api_specification.md: パス管理仕様セクションを追加、API関数でのパス指定方法を詳説
  - api_library_documentation.md: パス管理仕様セクションを追加、実装例とプロジェクトの可搬性について説明
- プロジェクトの可搬性確保と環境間移動の容易化を図る設計思想を文書化
- pathlib.Path使用推奨とクロスプラットフォーム対応の重要性を明記

## 2025-08-26
- 評価テーブル追加の仕様反映：`00_design/ref_design_byGrok4_2.md` を更新（ER図、テーブル詳細、関係性、SQL例を追記）。
- `00_design/schema.sql` に `evaluation_result_table` と `evaluation_data_table` を追加（FKはON DELETE RESTRICT、`CHECK (correct_task_num <= total_task_num)` を追加）。
- パスはdatabase.dbからの相対パスで統一。`false_positive`は1時間当たりの過検知数[回/h]、`evaluation_timestamp`を追加。
- インデックスは現時点では追加せず。
- 注記修正：`evaluation_data_table.algorithm_output_ID` は `algorithm_output_table.algorithm_output_ID` を参照に統一（仕様とスキーマを修正）。
- 既存DB非破壊対応：`scripts/create_database.py` を既存DBにもスキーマ適用（CREATE IF NOT EXISTS）する方式に更新。
- マイグレーションスクリプトを追加：`scripts/migrate_add_evaluation_tables.py`（不足テーブルのみ作成、外部キー有効）。
 - 実行: `uv run python scripts/migrate_add_evaluation_tables.py` を実施し、`evaluation_result_table`, `evaluation_data_table` をdatabase.dbに非破壊で作成。
 - 確認: `uv run python scripts/query_db_structure.py` にてテーブル一覧・件数を確認（両テーブルとも作成済、件数0件）。
 - API仕様整備: `00_design/api_specification.md` に評価API（登録/取得/一覧/概要計算）を追加。`00_design/api_library_documentation.md` に評価APIの使用例・引数を追記。

## 2025-08-26
- 評価API実装：`datawarehouse/evaluation_api.py` を新規追加。
  - `create_evaluation_result`, `get_evaluation_result`, `list_evaluation_results`
  - `create_evaluation_data`, `list_evaluation_data`
  - `get_evaluation_overview`（派生メトリクス計算: accuracy など）
- `datawarehouse/__init__.py` に評価APIを公開追加（__all__ 更新）。
 - 簡易テスト: `uv run python scripts/test_evaluation_api.py` を実行し、評価結果と評価データの作成・概要算出を確認（overview.accuracy=0.9444..., data_count=1）。テストスクリプトはコミット前に削除。