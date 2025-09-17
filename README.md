# DataWareHouse

[![PyPI version](https://badge.fury.io/py/datawarehouse.svg)](https://pypi.org/project/datawarehouse/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ビデオ処理評価システムのための包括的なデータウェアハウスライブラリです。

## 概要

DataWareHouseは、ビデオデータに基づくタスクのタグ付け、コアライブラリとアルゴリズムのバージョン管理、およびそれらの出力結果を管理するためのPythonライブラリです。SQLite3をベースとした軽量で使いやすいデータウェアハウスソリューションを提供します。

## 主な機能

- **タスク管理**: ビデオ内のタスク区間をタグ付け
- **バージョン管理**: コアライブラリとアルゴリズムのバージョン履歴追跡
- **出力管理**: 評価結果の格納と管理
- **データ整合性**: 外部キー制約による参照整合性の保証
- **CLIツール**: コマンドラインからのデータベース操作
- **豊富なAPI**: Pythonから簡単に操作できる包括的なAPI

## インストール

### PyPIからインストール

```bash
pip install git+https://github.com/abekoki/DataWareHouse@remake_pip_lib
```

## クイックスタート

### 基本的な使い方

```python
from datawarehouse import (
    DWHConnection,
    create_task, get_task, list_tasks,
    create_subject, get_subject,
    create_video, get_video,
    create_tag, get_tag
)

# データベース接続
with DWHConnection('my_database.db') as conn:
    # タスクの作成
    task_id = create_task(
        task_set=1,
        task_name="評価タスク1",
        task_describe="正検知評価のためのタスク"
    )

    # 被験者の作成
    subject_id = create_subject(subject_name="テスト被験者A")

    # ビデオデータの登録
    video_id = create_video(
        video_dir="/path/to/video.mp4",
        subject_id=subject_id,
        video_date="2025-01-15",
        video_length=120
    )

    # タグ付け（タスク区間の指定）
    tag_id = create_tag(
        video_id=video_id,
        task_id=task_id,
        start=30,  # 開始フレーム
        end=90     # 終了フレーム
    )

print(f"作成されたタスクID: {task_id}")
print(f"作成された被験者ID: {subject_id}")
print(f"作成されたビデオID: {video_id}")
print(f"作成されたタグID: {tag_id}")
```

### CLIツールの使用

```bash
# データベースの作成
dwh-cli create-db my_database.db

# データベース構造の確認
dwh-cli info my_database.db

# データベーススキーマ検証
dwh-cli validate my_database.db

# ヘルプ表示
dwh-cli --help
```

## API リファレンス

### 接続管理

```python
from datawarehouse import DWHConnection, get_connection

# 直接接続
conn = DWHConnection('database.db')

# コンテキストマネージャー推奨
with DWHConnection('database.db') as conn:
    # データベース操作
    pass
```

### タスク管理

```python
from datawarehouse import create_task, get_task, list_tasks, update_task, delete_task

# タスクの作成
task_id = create_task(
    task_set=1,
    task_name="評価タスク",
    task_describe="詳細な説明"
)

# タスクの取得
task = get_task(task_id)

# タスクの一覧取得
tasks = list_tasks()

# タスクの更新
update_task(task_id, task_name="新しい名前")

# タスクの削除
delete_task(task_id)
```

### 被験者管理

```python
from datawarehouse import create_subject, get_subject, list_subjects, update_subject, delete_subject

# 被験者の作成
subject_id = create_subject(subject_name="テスト被験者")

# 被験者の取得
subject = get_subject(subject_id)

# 被験者の一覧
subjects = list_subjects()
```

### ビデオ管理

```python
from datawarehouse import create_video, get_video, list_videos, update_video, delete_video

# ビデオの登録
video_id = create_video(
    video_dir="/path/to/video.mp4",
    subject_id=subject_id,
    video_date="2025-01-15",
    video_length=120
)

# ビデオの取得
video = get_video(video_id)

# 被験者別のビデオ一覧
videos = get_videos_by_subject(subject_id)
```

### タグ管理

```python
from datawarehouse import create_tag, get_tag, get_video_tags, get_task_tags, list_tags

# タグの作成（タスク区間指定）
tag_id = create_tag(
    video_id=video_id,
    task_id=task_id,
    start=30,   # 開始フレーム
    end=90      # 終了フレーム
)

# ビデオのタグ取得
video_tags = get_video_tags(video_id)

# タスクのタグ取得
task_tags = get_task_tags(task_id)
```

### バージョン管理

```python
from datawarehouse import (
    create_core_lib_version, get_core_lib_version,
    create_algorithm_version, get_algorithm_version
)

# コアライブラリバージョンの作成
core_lib_id = create_core_lib_version(
    core_lib_version="1.2.0",
    core_lib_update_information="新機能追加",
    core_lib_commit_hash="abc123def456"
)

# アルゴリズムバージョンの作成
algorithm_id = create_algorithm_version(
    algorithm_version="2.1.0",
    algorithm_update_information="性能改善",
    algorithm_commit_hash="def789ghi012"
)
```

## アーキテクチャ

### データベーススキーマ

DataWareHouseは以下の主要テーブルで構成されています：

- **task_table**: タスク情報の管理
- **subject_table**: 被験者情報の管理
- **video_table**: ビデオメタデータの管理
- **tag_table**: ビデオ内タスク区間のタグ付け
- **core_lib_table**: コアライブラリバージョン管理（自己参照）
- **core_lib_output_table**: コアライブラリ処理結果
- **algorithm_table**: アルゴリズムバージョン管理（自己参照）
- **algorithm_output_table**: アルゴリズム処理結果
- **evaluation_result_table**: 評価結果の集計
- **evaluation_data_table**: 個別データ評価結果
- **analysis_result_table**: 課題分析結果
- **problem_table**: 抽出された課題管理
- **analysis_data_table**: 課題分析データ

### 外部キー制約

SQLiteでは接続ごとに `PRAGMA foreign_keys = ON;` を有効化する必要があります：

```python
with DWHConnection('database.db') as conn:
    # 外部キー制約が自動的に有効化されます
    pass
```

## 開発・運用

### バックアップ

```bash
# データベースのバックアップ（SQLiteは単一ファイル）
cp database.db database_backup.db
```

### エラーハンドリング

```python
from datawarehouse import DWHError, DWHNotFoundError, DWHValidationError

try:
    task = get_task(task_id)
except DWHNotFoundError:
    print("タスクが見つかりません")
except DWHValidationError as e:
    print(f"検証エラー: {e}")
except DWHError as e:
    print(f"DataWareHouseエラー: {e}")
```

## 技術仕様

### 要件
- **Python**: 3.10以上
- **データベース**: SQLite3（標準ライブラリ使用）
- **依存関係**: なし（標準ライブラリのみ）

### 特徴
- **軽量**: 追加依存関係なし
- **型安全**: 完全な型ヒント対応
- **スレッドセーフ**: 接続ごとの独立性
- **ACID準拠**: SQLiteのトランザクション保証

### バージョン管理
- **形式**: セマンティックバージョニング（例: 1.0.0）
- **識別子**: Gitコミットハッシュ（SHA-1, 40文字）
- **履歴**: 自己参照によるバージョン履歴追跡

## トラブルシューティング

### よくある問題

1. **外部キー制約エラー**
   ```python
   # 解決策: 接続時に自動的に有効化されます
   with DWHConnection('database.db') as conn:
       pass
   ```

2. **データベースファイルが存在しない**
   ```bash
   # CLIでデータベースを作成
   dwh-cli create-db database.db
   ```

3. **パーミッションエラー**
   - データベースファイルの書き込み権限を確認
   - ディレクトリの作成権限を確認

### デバッグ情報取得

```python
from datawarehouse import check_data_integrity, get_table_statistics

# データ整合性チェック
integrity_result = check_data_integrity()

# テーブル統計情報
stats = get_table_statistics()
```

### スキーマ検証

```python
from datawarehouse import (
    validate_database_schema,
    get_schema_validation_report,
    check_database_compatibility
)

# 詳細なスキーマ検証
validation_result = validate_database_schema('database.db')
print(f"有効なスキーマ: {validation_result['is_valid']}")
print(f"重大問題数: {len(validation_result['issues'])}")
print(f"警告数: {len(validation_result['warnings'])}")

# 検証レポート取得
report = get_schema_validation_report('database.db')
print(report)

# 互換性チェック（True/False）
is_compatible = check_database_compatibility('database.db')
```

## ライセンス

MIT License

## 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## サポート

- **ドキュメント**: [https://datawarehouse.readthedocs.io/](https://datawarehouse.readthedocs.io/)
- **Issues**: [https://github.com/your-org/datawarehouse/issues](https://github.com/your-org/datawarehouse/issues)
- **Discussions**: [https://github.com/your-org/datawarehouse/discussions](https://github.com/your-org/datawarehouse/discussions)

---

**注意**: 本ライブラリは研究・開発用途を想定しています。本格運用前に十分なテストを行ってください。
