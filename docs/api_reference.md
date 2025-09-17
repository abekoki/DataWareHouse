# DataWareHouse API リファレンス

## 概要

DataWareHouseはビデオ処理評価システムのための包括的なデータウェアハウスライブラリです。このドキュメントでは、利用可能なすべてのAPI関数について詳しく説明します。

## インストール

```bash
pip install datawarehouse
```

## 基本的な使用方法

```python
import datawarehouse as dwh

# データベース接続
with dwh.DWHConnection('my_database.db') as conn:
    # API関数の使用
    pass
```

## API 関数一覧

### 接続管理

#### `DWHConnection(db_path: str)`

DataWareHouseデータベースへの接続を管理するクラス。

**パラメータ:**
- `db_path` (str): データベースファイルのパス

**使用例:**
```python
conn = dwh.DWHConnection('database.db')
# または
with dwh.DWHConnection('database.db') as conn:
    pass
```

#### `get_connection(db_path: str = "database.db") -> DWHConnection`

データベース接続を取得する関数。

**パラメータ:**
- `db_path` (str, optional): データベースファイルのパス。デフォルトは"database.db"

**戻り値:**
- `DWHConnection`: データベース接続オブジェクト

### タスク管理

#### `create_task(task_set: int, task_name: str, task_describe: str) -> int`

新しいタスクを作成します。

**パラメータ:**
- `task_set` (int): タスクのセット番号
- `task_name` (str): タスク名
- `task_describe` (str): タスクの説明

**戻り値:**
- `int`: 作成されたタスクのID

#### `get_task(task_id: int) -> dict`

指定されたIDのタスクを取得します。

**パラメータ:**
- `task_id` (int): タスクID

**戻り値:**
- `dict`: タスク情報

#### `list_tasks() -> list`

すべてのタスクを取得します。

**戻り値:**
- `list`: タスク情報のリスト

#### `update_task(task_id: int, **kwargs) -> bool`

タスク情報を更新します。

**パラメータ:**
- `task_id` (int): 更新するタスクID
- `**kwargs`: 更新するフィールド（task_name, task_describeなど）

**戻り値:**
- `bool`: 更新成功の場合True

#### `delete_task(task_id: int) -> bool`

タスクを削除します。

**パラメータ:**
- `task_id` (int): 削除するタスクID

**戻り値:**
- `bool`: 削除成功の場合True

### 被験者管理

#### `create_subject(subject_name: str) -> int`

新しい被験者を作成します。

**パラメータ:**
- `subject_name` (str): 被験者名

**戻り値:**
- `int`: 作成された被験者のID

#### `get_subject(subject_id: int) -> dict`

指定されたIDの被験者を取得します。

**パラメータ:**
- `subject_id` (int): 被験者ID

**戻り値:**
- `dict`: 被験者情報

#### `list_subjects() -> list`

すべての被験者を取得します。

**戻り値:**
- `list`: 被験者情報のリスト

#### `update_subject(subject_id: int, subject_name: str) -> bool`

被験者情報を更新します。

**パラメータ:**
- `subject_id` (int): 更新する被験者ID
- `subject_name` (str): 新しい被験者名

**戻り値:**
- `bool`: 更新成功の場合True

#### `delete_subject(subject_id: int) -> bool`

被験者を削除します。

**パラメータ:**
- `subject_id` (int): 削除する被験者ID

**戻り値:**
- `bool`: 削除成功の場合True

#### `find_subject_by_name(subject_name: str) -> dict`

名前で被験者を検索します。

**パラメータ:**
- `subject_name` (str): 検索する被験者名

**戻り値:**
- `dict`: 被験者情報、見つからない場合はNone

### ビデオ管理

#### `create_video(video_dir: str, subject_id: int, video_date: str, video_length: int) -> int`

新しいビデオを作成します。

**パラメータ:**
- `video_dir` (str): ビデオファイルのディレクトリパス
- `subject_id` (int): 被験者ID
- `video_date` (str): 撮影日（YYYY-MM-DD形式）
- `video_length` (int): ビデオの長さ（秒）

**戻り値:**
- `int`: 作成されたビデオのID

#### `get_video(video_id: int) -> dict`

指定されたIDのビデオを取得します。

**パラメータ:**
- `video_id` (int): ビデオID

**戻り値:**
- `dict`: ビデオ情報

#### `list_videos() -> list`

すべてのビデオを取得します。

**戻り値:**
- `list`: ビデオ情報のリスト

#### `get_videos_by_subject(subject_id: int) -> list`

指定された被験者のすべてのビデオを取得します。

**パラメータ:**
- `subject_id` (int): 被験者ID

**戻り値:**
- `list`: ビデオ情報のリスト

#### `update_video(video_id: int, **kwargs) -> bool`

ビデオ情報を更新します。

**パラメータ:**
- `video_id` (int): 更新するビデオID
- `**kwargs`: 更新するフィールド

**戻り値:**
- `bool`: 更新成功の場合True

#### `delete_video(video_id: int) -> bool`

ビデオを削除します。

**パラメータ:**
- `video_id` (int): 削除するビデオID

**戻り値:**
- `bool`: 削除成功の場合True

### タグ管理

#### `create_tag(video_id: int, task_id: int, start: int, end: int) -> int`

新しいタグを作成します。

**パラメータ:**
- `video_id` (int): ビデオID
- `task_id` (int): タスクID
- `start` (int): タスク開始フレーム
- `end` (int): タスク終了フレーム

**戻り値:**
- `int`: 作成されたタグのID

#### `get_tag(tag_id: int) -> dict`

指定されたIDのタグを取得します。

**パラメータ:**
- `tag_id` (int): タグID

**戻り値:**
- `dict`: タグ情報

#### `get_video_tags(video_id: int) -> list`

指定されたビデオのすべてのタグを取得します。

**パラメータ:**
- `video_id` (int): ビデオID

**戻り値:**
- `list`: タグ情報のリスト

#### `get_task_tags(task_id: int) -> list`

指定されたタスクのすべてのタグを取得します。

**パラメータ:**
- `task_id` (int): タスクID

**戻り値:**
- `list`: タグ情報のリスト

#### `list_tags() -> list`

すべてのタグを取得します。

**戻り値:**
- `list`: タグ情報のリスト

#### `update_tag(tag_id: int, **kwargs) -> bool`

タグ情報を更新します。

**パラメータ:**
- `tag_id` (int): 更新するタグID
- `**kwargs`: 更新するフィールド

**戻り値:**
- `bool`: 更新成功の場合True

#### `delete_tag(tag_id: int) -> bool`

タグを削除します。

**パラメータ:**
- `tag_id` (int): 削除するタグID

**戻り値:**
- `bool`: 削除成功の場合True

#### `get_tag_duration(tag_id: int) -> int`

タグの継続時間を取得します。

**パラメータ:**
- `tag_id` (int): タグID

**戻り値:**
- `int`: 継続時間（フレーム数）

### コアライブラリ管理

#### `create_core_lib_version(version: str, update_info: str, commit_hash: str, base_version_id: int = None) -> int`

新しいコアライブラリバージョンを作成します。

**パラメータ:**
- `version` (str): バージョン番号
- `update_info` (str): 更新情報
- `commit_hash` (str): コミットハッシュ
- `base_version_id` (int, optional): ベースバージョンID

**戻り値:**
- `int`: 作成されたコアライブラリバージョンのID

#### `get_core_lib_version(core_lib_id: int) -> dict`

指定されたIDのコアライブラリバージョンを取得します。

**パラメータ:**
- `core_lib_id` (int): コアライブラリバージョンID

**戻り値:**
- `dict`: コアライブラリバージョン情報

#### `list_core_lib_versions() -> list`

すべてのコアライブラリバージョンを取得します。

**戻り値:**
- `list`: コアライブラリバージョン情報のリスト

#### `get_core_lib_version_history(core_lib_id: int) -> list`

指定されたコアライブラリバージョンの履歴を取得します。

**パラメータ:**
- `core_lib_id` (int): コアライブラリバージョンID

**戻り値:**
- `list`: バージョン履歴のリスト

#### `find_core_lib_by_version(version: str) -> dict`

バージョン番号でコアライブラリを検索します。

**パラメータ:**
- `version` (str): バージョン番号

**戻り値:**
- `dict`: コアライブラリバージョン情報

#### `find_core_lib_by_commit_hash(commit_hash: str) -> dict`

コミットハッシュでコアライブラリを検索します。

**パラメータ:**
- `commit_hash` (str): コミットハッシュ

**戻り値:**
- `dict`: コアライブラリバージョン情報

### コアライブラリ出力管理

#### `create_core_lib_output(core_lib_id: int, video_id: int, output_dir: str) -> int`

新しいコアライブラリ出力を作成します。

**パラメータ:**
- `core_lib_id` (int): コアライブラリバージョンID
- `video_id` (int): ビデオID
- `output_dir` (str): 出力ディレクトリ

**戻り値:**
- `int`: 作成されたコアライブラリ出力のID

#### `get_core_lib_output(core_lib_output_id: int) -> dict`

指定されたIDのコアライブラリ出力を取得します。

**パラメータ:**
- `core_lib_output_id` (int): コアライブラリ出力ID

**戻り値:**
- `dict`: コアライブラリ出力情報

#### `list_core_lib_outputs() -> list`

すべてのコアライブラリ出力を取得します。

**戻り値:**
- `list`: コアライブラリ出力情報のリスト

### アルゴリズム管理

#### `create_algorithm_version(version: str, update_info: str, commit_hash: str, base_version_id: int = None) -> int`

新しいアルゴリズムバージョンを作成します。

**パラメータ:**
- `version` (str): バージョン番号
- `update_info` (str): 更新情報
- `commit_hash` (str): コミットハッシュ
- `base_version_id` (int, optional): ベースバージョンID

**戻り値:**
- `int`: 作成されたアルゴリズムバージョンのID

#### `get_algorithm_version(algorithm_id: int) -> dict`

指定されたIDのアルゴリズムバージョンを取得します。

**パラメータ:**
- `algorithm_id` (int): アルゴリズムバージョンID

**戻り値:**
- `dict`: アルゴリズムバージョン情報

#### `list_algorithm_versions() -> list`

すべてのアルゴリズムバージョンを取得します。

**戻り値:**
- `list`: アルゴリズムバージョン情報のリスト

#### `get_algorithm_version_history(algorithm_id: int) -> list`

指定されたアルゴリズムバージョンの履歴を取得します。

**パラメータ:**
- `algorithm_id` (int): アルゴリズムバージョンID

**戻り値:**
- `list`: バージョン履歴のリスト

#### `find_algorithm_by_version(version: str) -> dict`

バージョン番号でアルゴリズムを検索します。

**パラメータ:**
- `version` (str): バージョン番号

**戻り値:**
- `dict`: アルゴリズムバージョン情報

#### `find_algorithm_by_commit_hash(commit_hash: str) -> dict`

コミットハッシュでアルゴリズムを検索します。

**パラメータ:**
- `commit_hash` (str): コミットハッシュ

**戻り値:**
- `dict`: アルゴリズムバージョン情報

#### `get_latest_algorithm_version() -> dict`

最新のアルゴリズムバージョンを取得します。

**戻り値:**
- `dict`: 最新のアルゴリズムバージョン情報

### アルゴリズム出力管理

#### `create_algorithm_output(algorithm_id: int, core_lib_output_id: int, output_dir: str) -> int`

新しいアルゴリズム出力を作成します。

**パラメータ:**
- `algorithm_id` (int): アルゴリズムバージョンID
- `core_lib_output_id` (int): コアライブラリ出力ID
- `output_dir` (str): 出力ディレクトリ

**戻り値:**
- `int`: 作成されたアルゴリズム出力のID

#### `get_algorithm_output(algorithm_output_id: int) -> dict`

指定されたIDのアルゴリズム出力を取得します。

**パラメータ:**
- `algorithm_output_id` (int): アルゴリズム出力ID

**戻り値:**
- `dict`: アルゴリズム出力情報

#### `list_algorithm_outputs() -> list`

すべてのアルゴリズム出力を取得します。

**戻り値:**
- `list`: アルゴリズム出力情報のリスト

## 例外クラス

### `DWHError`

DataWareHouse関連の基本例外クラス。

### `DWHConnectionError`

データベース接続エラー。

### `DWHNotFoundError`

データが見つからないエラー。

### `DWHValidationError`

データ検証エラー。

### `DWHConstraintError`

制約違反エラー。

### `DWHUniqueConstraintError`

UNIQUE制約違反エラー。

## CLI ツール

### `dwh-cli create-db <db_path>`

データベースを作成・初期化します。

### `dwh-cli info <db_path>`

データベース構造情報を表示します。

### `dwh-cli --help`

ヘルプを表示します。

## スキーマ検証

### `validate_database_schema(db_path: str) -> Dict`

データベーススキーマを検証し、詳細な検証結果を返します。

**パラメータ:**
- `db_path` (str): データベースファイルのパス

**戻り値:**
- `Dict`: 検証結果
  ```python
  {
      'is_valid': bool,           # スキーマが有効かどうか
      'issues': List[Dict],       # 重大な問題のリスト
      'warnings': List[Dict],     # 警告のリスト
      'tables_found': List[str],  # 検出されたテーブルのリスト
      'tables_missing': List[str], # 欠落テーブルのリスト
      'indexes_found': List[str], # 検出されたインデックスのリスト
      'indexes_missing': List[str], # 欠落インデックスのリスト
      'summary': Dict             # サマリー情報
  }
  ```

**使用例:**
```python
result = validate_database_schema('database.db')
if result['is_valid']:
    print("スキーマは有効です")
else:
    print(f"問題が見つかりました: {len(result['issues'])}件")
```

### `get_schema_validation_report(db_path: str) -> str`

データベーススキーマ検証の詳細レポートを文字列形式で返します。

**パラメータ:**
- `db_path` (str): データベースファイルのパス

**戻り値:**
- `str`: 人間可読な検証レポート

**使用例:**
```python
report = get_schema_validation_report('database.db')
print(report)
```

### `check_database_compatibility(db_path: str) -> bool`

データベースがDataWareHouseと互換性があるかを簡易的にチェックします。

**パラメータ:**
- `db_path` (str): データベースファイルのパス

**戻り値:**
- `bool`: 互換性がある場合True

**使用例:**
```python
is_compatible = check_database_compatibility('database.db')
if is_compatible:
    print("データベースは互換性があります")
else:
    print("データベースに互換性の問題があります")
```

### `SchemaValidator`

スキーマ検証を行うクラスです。上記の関数はこのクラスのインスタンスメソッドを使用しています。

**メソッド:**
- `validate_schema() -> Dict`: スキーマ検証を実行
- `get_validation_report(validation_result: Dict) -> str`: 検証結果からレポートを生成

**使用例:**
```python
from datawarehouse import SchemaValidator

validator = SchemaValidator('database.db')
result = validator.validate_schema()
report = validator.get_validation_report(result)
```

## CLI ツール

### `dwh-cli validate <db_path>`

データベーススキーマを検証し、詳細なレポートを表示します。

**引数:**
- `db_path`: 検証するデータベースファイルのパス

**使用例:**
```bash
# データベーススキーマ検証
dwh-cli validate database.db

# 検証結果の例
============================================================
DataWareHouse データベーススキーマ検証レポート
============================================================
データベース: database.db

サマリー:
  想定テーブル数: 13
  検出テーブル数: 13
  欠落テーブル数: 0
  検出インデックス数: 2
  欠落インデックス数: 0
  重大問題数: 0
  警告数: 0

✅ 検証結果: 有効なDataWareHouseスキーマです

📋 検出されたテーブル:
  • algorithm_output_table
  • algorithm_table
  • analysis_data_table
  • analysis_result_table
  • core_lib_output_table
  • core_lib_table
  • evaluation_data_table
  • evaluation_result_table
  • problem_table
  • subject_table
  • tag_table
  • task_table
  • video_table

🔍 検出されたインデックス:
  • idx_algorithm_version
  • idx_core_lib_version
============================================================
✅ このデータベースはDataWareHouseと互換性があります
```

## ライセンス

MIT License
