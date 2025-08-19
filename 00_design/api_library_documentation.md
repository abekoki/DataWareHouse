# DataWareHouse API ライブラリ ドキュメント

## 概要
DataWareHouse APIライブラリは、ビデオ処理評価システムのSQLite3データベースにアクセスするための包括的なPython APIを提供します。このライブラリは、API仕様書（`api_specification.md`）およびデータベース構造詳細説明書（`database_structure_detailed.md`）に基づいて実装されています。

## インストールと設定

### 前提条件
- Python 3.10以上
- uv（パッケージ管理）
- SQLite3データベース（`database.db`）

### セットアップ
```bash
# 仮想環境の作成
uv venv .venv

# 依存関係の同期
uv sync

# データベースの初期化
uv run python scripts/create_database.py
```

## 基本的な使用方法

### インポート
```python
import datawarehouse as dwh

# または個別にインポート
from datawarehouse import create_subject, get_subject, DWHError
```

### 接続管理
```python
# 自動接続管理（推奨）
subject_id = dwh.create_subject("Subject A")

# 手動接続管理
with dwh.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subject_table")
    results = cursor.fetchall()
```

## API リファレンス

### 1. 例外クラス

#### DWHError（基底クラス）
```python
class DWHError(Exception):
    def __init__(self, message: str, error_code: str = None)
```

#### 主な例外
- `DWHConstraintError` - 制約違反（E001）
- `DWHUniqueConstraintError` - UNIQUE制約違反（E002）
- `DWHNotFoundError` - データが見つからない（E003）
- `DWHValidationError` - データ検証エラー（E004）
- `DWHConnectionError` - データベース接続エラー（E005）

### 2. 被験者管理API

#### create_subject
```python
def create_subject(subject_name: str, db_path: str = "database.db") -> int
```
新しい被験者を登録し、被験者IDを返します。

#### get_subject
```python
def get_subject(subject_id: int, db_path: str = "database.db") -> Dict
```
被験者IDで被験者情報を取得します。

#### list_subjects
```python
def list_subjects(db_path: str = "database.db") -> List[Dict]
```
全被験者の一覧を取得します。

#### その他
- `update_subject(subject_id, subject_name)` - 被験者情報を更新
- `delete_subject(subject_id)` - 被験者を削除
- `find_subject_by_name(subject_name)` - 名前で被験者を検索

### 3. タスク管理API

#### create_task
```python
def create_task(task_set: int, task_name: str, task_describe: str, 
                db_path: str = "database.db") -> int
```
新しいタスクを登録し、タスクIDを返します。

#### get_task
```python
def get_task(task_id: int, db_path: str = "database.db") -> Dict
```
タスクIDでタスク情報を取得します。

#### list_tasks
```python
def list_tasks(task_set: Optional[int] = None, 
               db_path: str = "database.db") -> List[Dict]
```
タスク一覧を取得します。`task_set`を指定すると、そのセットのタスクのみ取得します。

### 4. ビデオ管理API

#### create_video
```python
def create_video(video_dir: str, subject_id: int, video_date: str, 
                 video_length: int, db_path: str = "database.db") -> int
```
新しいビデオを登録します。
- `video_date`: YYYY-MM-DD形式
- `video_length`: 秒単位

#### get_video
```python
def get_video(video_id: int, db_path: str = "database.db") -> Dict
```
ビデオIDでビデオ情報を取得します。

#### list_videos
```python
def list_videos(subject_id: Optional[int] = None, 
                date_from: Optional[str] = None,
                date_to: Optional[str] = None, 
                db_path: str = "database.db") -> List[Dict]
```
条件に応じてビデオ一覧を取得します。

### 5. タグ管理API

#### create_tag
```python
def create_tag(video_id: int, task_id: int, start: int, end: int, 
               db_path: str = "database.db") -> int
```
新しいタグを登録します。
- `start`, `end`: フレーム番号（start < end である必要があります）

#### get_video_tags
```python
def get_video_tags(video_id: int, db_path: str = "database.db") -> List[Dict]
```
指定したビデオの全タグを取得します。

#### get_task_tags
```python
def get_task_tags(task_id: int, db_path: str = "database.db") -> List[Dict]
```
指定したタスクの全タグを取得します。

#### get_tag_duration
```python
def get_tag_duration(tag_id: int, fps: float = 30.0, 
                     db_path: str = "database.db") -> float
```
タグの時間長（秒）を計算します。

### 6. コアライブラリ管理API

#### create_core_lib_version
```python
def create_core_lib_version(version: str, update_info: str, commit_hash: str, 
                           base_version_id: Optional[int] = None,
                           db_path: str = "database.db") -> int
```
新しいコアライブラリバージョンを登録します。
- `commit_hash`: 40文字の16進数文字列
- `base_version_id`: 前のバージョンのID（自己参照）

#### get_core_lib_version_history
```python
def get_core_lib_version_history(core_lib_id: int, 
                                db_path: str = "database.db") -> List[Dict]
```
コアライブラリのバージョン履歴を古い順で取得します。

#### find_core_lib_by_version / find_core_lib_by_commit_hash
```python
def find_core_lib_by_version(version: str, db_path: str = "database.db") -> Optional[Dict]
def find_core_lib_by_commit_hash(commit_hash: str, db_path: str = "database.db") -> Optional[Dict]
```
バージョン文字列またはコミットハッシュでコアライブラリを検索します。

#### create_core_lib_output
```python
def create_core_lib_output(core_lib_id: int, video_id: int, output_dir: str,
                          db_path: str = "database.db") -> int
```
コアライブラリの評価結果を登録します。

### 7. アルゴリズム管理API

#### create_algorithm_version
```python
def create_algorithm_version(version: str, update_info: str, commit_hash: str, 
                           base_version_id: Optional[int] = None,
                           db_path: str = "database.db") -> int
```
新しいアルゴリズムバージョンを登録します。

#### get_algorithm_version_history
```python
def get_algorithm_version_history(algorithm_id: int, 
                                 db_path: str = "database.db") -> List[Dict]
```
アルゴリズムのバージョン履歴を古い順で取得します。

#### create_algorithm_output
```python
def create_algorithm_output(algorithm_id: int, core_lib_output_id: int, output_dir: str,
                           db_path: str = "database.db") -> int
```
アルゴリズムの評価結果を登録します。

#### get_latest_algorithm_version
```python
def get_latest_algorithm_version(db_path: str = "database.db") -> Optional[Dict]
```
最新のアルゴリズムバージョンを取得します。

### 8. 検索・分析API

#### search_task_executions
```python
def search_task_executions(task_set: Optional[int] = None, 
                          subject_id: Optional[int] = None,
                          date_from: Optional[str] = None, 
                          date_to: Optional[str] = None,
                          db_path: str = "database.db") -> List[Dict]
```
タスクの実行状況を複合条件で検索します。

#### get_table_statistics
```python
def get_table_statistics(db_path: str = "database.db") -> Dict[str, int]
```
全テーブルの件数統計を取得します。

#### check_data_integrity
```python
def check_data_integrity(db_path: str = "database.db") -> Dict[str, any]
```
データベースの整合性をチェックします。
- 外部キー制約違反
- フレーム区間の妥当性
- 孤立レコード
- 重複コミットハッシュ

#### get_performance_metrics
```python
def get_performance_metrics(db_path: str = "database.db") -> Dict[str, any]
```
パフォーマンスメトリクスを取得します。

#### get_processing_pipeline_summary
```python
def get_processing_pipeline_summary(video_id: Optional[int] = None, 
                                   db_path: str = "database.db") -> List[Dict]
```
処理パイプラインの概要を取得します。

## 使用例

### 基本的なワークフロー
```python
import datawarehouse as dwh

try:
    # 1. 基本データの登録
    subject_id = dwh.create_subject("Subject A")
    task_id = dwh.create_task(1, "正検知評価", "ビデオ内の正検知を評価")
    
    # 2. ビデオとタグの登録
    video_id = dwh.create_video(
        "01_mov_data/subject_a.mp4", subject_id, "2025-08-19", 120
    )
    tag_id = dwh.create_tag(video_id, task_id, 0, 30)
    
    # 3. バージョン管理
    core_lib_id = dwh.create_core_lib_version(
        "1.0.0", "初期バージョン", "a1b2c3d4e5f6..."
    )
    output_id = dwh.create_core_lib_output(
        core_lib_id, video_id, "02_core_lib_output/v1.0.0"
    )
    
    # 4. データ取得・分析
    video_tags = dwh.get_video_tags(video_id)
    stats = dwh.get_table_statistics()
    
except dwh.DWHError as e:
    print(f"エラー: {e} (コード: {e.error_code})")
```

### バージョン履歴の管理
```python
# 初期バージョン
v1_id = dwh.create_core_lib_version("1.0.0", "初期バージョン", "hash1")

# バージョンアップ（自己参照）
v2_id = dwh.create_core_lib_version("1.1.0", "バグ修正", "hash2", v1_id)
v3_id = dwh.create_core_lib_version("1.2.0", "新機能", "hash3", v2_id)

# 履歴の取得
history = dwh.get_core_lib_version_history(v3_id)
for version in history:
    print(f"v{version['core_lib_version']}: {version['core_lib_update_information']}")
```

### 複合検索
```python
# 条件を組み合わせた検索
executions = dwh.search_task_executions(
    task_set=1,
    date_from="2025-08-01",
    date_to="2025-08-31"
)

for ex in executions:
    print(f"{ex['subject_name']}: {ex['task_name']} "
          f"({ex['start']}-{ex['end']}フレーム)")
```

### バッチ処理
```python
# 複数のビデオを一括登録
video_data = [
    {"video_dir": "video1.mp4", "subject_id": 1, "video_date": "2025-08-19", "video_length": 120},
    {"video_dir": "video2.mp4", "subject_id": 1, "video_date": "2025-08-19", "video_length": 150},
]

try:
    with dwh.get_connection() as conn:
        for data in video_data:
            dwh.create_video(**data)
        # 自動的にコミットされる
except dwh.DWHError as e:
    # 自動的にロールバックされる
    print(f"バッチ処理に失敗: {e}")
```

## エラーハンドリング

### 例外の種類と対処法
```python
try:
    # API呼び出し
    result = dwh.create_video(...)
    
except dwh.DWHConstraintError as e:
    # 制約違反（外部キー、UNIQUE等）
    print(f"制約違反: {e}")
    if e.table_name:
        print(f"対象テーブル: {e.table_name}")
    
except dwh.DWHNotFoundError as e:
    # データが見つからない
    print(f"データが見つかりません: {e}")
    if e.record_id:
        print(f"対象ID: {e.record_id}")
    
except dwh.DWHValidationError as e:
    # データ検証エラー
    print(f"入力値エラー: {e}")
    if e.field_name:
        print(f"対象フィールド: {e.field_name}")
    
except dwh.DWHConnectionError as e:
    # データベース接続エラー
    print(f"接続エラー: {e}")
    
except dwh.DWHError as e:
    # その他のDataWareHouseエラー
    print(f"DataWareHouseエラー: {e} (コード: {e.error_code})")
```

## パフォーマンス考慮事項

### インデックスの活用
- バージョン検索用インデックスが自動的に使用されます
- 大量データ処理時は追加インデックスを検討してください

### バッチ処理の最適化
```python
# 推奨：トランザクション内での一括処理
with dwh.get_connection() as conn:
    for data in large_dataset:
        dwh.create_tag(**data)
    # 一括コミット

# 非推奨：個別コミット
for data in large_dataset:
    dwh.create_tag(**data)  # 毎回コミット
```

### 接続管理
- 短時間の操作には自動接続管理を使用
- 長時間の処理や複数操作には手動接続管理を使用

## トラブルシューティング

### よくある問題
1. **外部キー制約違反**: 関連データが存在しない
2. **UNIQUE制約違反**: コミットハッシュの重複
3. **データ検証エラー**: 日付形式やフレーム区間の不正
4. **接続エラー**: データベースファイルが見つからない

### デバッグ方法
```python
# データ整合性チェック
integrity = dwh.check_data_integrity()
print(integrity)

# テーブル統計
stats = dwh.get_table_statistics()
print(stats)

# 特定テーブルの内容確認
with dwh.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table_name LIMIT 10")
    print(cursor.fetchall())
```

## 今後の拡張

### 想定される機能追加
- データエクスポート機能
- バックアップ・復旧機能
- 設定ファイルによるカスタマイズ
- ログ出力機能
- パフォーマンス監視

### カスタマイズポイント
- カスタム例外クラスの追加
- 独自の検証ルールの実装
- 接続プールの導入
- キャッシュ機能の追加

---

このドキュメントは、DataWareHouse APIライブラリv0.1.0に基づいています。
最新の情報については、ソースコードおよびテストケースを参照してください。
