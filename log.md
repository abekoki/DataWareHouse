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

