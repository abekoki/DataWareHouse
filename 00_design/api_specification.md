# DataWareHouse API仕様書

## 概要
他のモジュールがDataWareHouseにアクセスし、データの出し入れを行うためのAPI仕様書です。Python標準ライブラリのsqlite3を使用し、外部キー制約を適切に管理します。

## 基本設計原則

### 1. 接続管理
- 各モジュールは独立したデータベース接続を作成
- 接続ごとに外部キー制約を有効化
- 接続終了時は適切にクローズ

### 2. エラーハンドリング
- SQLiteエラーを適切にキャッチ
- 外部キー制約違反の詳細なエラーメッセージ
- ロールバック機能の提供

### 3. データ整合性
- トランザクション管理による一貫性保証
- 外部キー制約による参照整合性
- データ検証機能

## データベース接続クラス

### DWHConnection クラス
```python
class DWHConnection:
    """DataWareHouseへの接続を管理するクラス"""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.connection = None
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        self.connection = sqlite3.connect(self.db_path)
        # 外部キー制約を有効化
        self.connection.execute("PRAGMA foreign_keys = ON;")
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        if self.connection:
            self.connection.close()
```

## 主要API関数

### 1. タスク管理API

#### タスクの登録
```python
def create_task(task_set: int, task_name: str, task_describe: str) -> int:
    """
    新しいタスクを登録
    
    Args:
        task_set: タスクセット番号
        task_name: タスク名
        task_describe: タスクの説明
    
    Returns:
        task_ID: 作成されたタスクのID
    
    Raises:
        sqlite3.Error: データベースエラー
    """
```

#### タスクの取得
```python
def get_task(task_id: int) -> dict:
    """
    タスクIDでタスク情報を取得
    
    Args:
        task_id: タスクID
    
    Returns:
        dict: タスク情報（task_ID, task_set, task_name, task_describe）
    
    Raises:
        ValueError: タスクが見つからない場合
    """
```

#### タスク一覧の取得
```python
def list_tasks(task_set: int = None) -> List[dict]:
    """
    タスク一覧を取得
    
    Args:
        task_set: タスクセット番号（指定時はそのセットのみ）
    
    Returns:
        List[dict]: タスク情報のリスト
    """
```

### 2. 被験者管理API

#### 被験者の登録
```python
def create_subject(subject_name: str) -> int:
    """
    新しい被験者を登録
    
    Args:
        subject_name: 被験者名
    
    Returns:
        subject_ID: 作成された被験者のID
    """
```

#### 被験者情報の取得
```python
def get_subject(subject_id: int) -> dict:
    """
    被験者IDで被験者情報を取得
    
    Args:
        subject_id: 被験者ID
    
    Returns:
        dict: 被験者情報（subject_ID, subject_name）
    """
```

### 3. ビデオ管理API

#### ビデオの登録
```python
def create_video(video_dir: str, subject_id: int, video_date: str, video_length: int) -> int:
    """
    新しいビデオを登録
    
    Args:
        video_dir: ビデオファイルのディレクトリパス
        subject_id: 被験者ID
        video_date: 取得日（YYYY-MM-DD）
        video_length: ビデオの長さ（秒）
    
    Returns:
        video_ID: 作成されたビデオのID
    
    Raises:
        ValueError: 被験者が存在しない場合
    """
```

#### ビデオ情報の取得
```python
def get_video(video_id: int) -> dict:
    """
    ビデオIDでビデオ情報を取得
    
    Args:
        video_id: ビデオID
    
    Returns:
        dict: ビデオ情報（video_ID, video_dir, subject_ID, video_date, video_length）
    """
```

### 4. タグ管理API

#### タグの登録
```python
def create_tag(video_id: int, task_id: int, start: int, end: int) -> int:
    """
    新しいタグを登録
    
    Args:
        video_id: ビデオID
        task_id: タスクID
        start: 開始フレーム
        end: 終了フレーム
    
    Returns:
        tag_ID: 作成されたタグのID
    
    Raises:
        ValueError: ビデオまたはタスクが存在しない場合
        ValueError: start >= end の場合
    """
```

#### ビデオのタグ一覧取得
```python
def get_video_tags(video_id: int) -> List[dict]:
    """
    ビデオのタグ一覧を取得
    
    Args:
        video_id: ビデオID
    
    Returns:
        List[dict]: タグ情報のリスト（tag_ID, task_ID, start, end, task_name）
    """
```

### 5. コアライブラリ管理API

#### コアライブラリバージョンの登録
```python
def create_core_lib_version(
    version: str, 
    update_info: str, 
    commit_hash: str, 
    base_version_id: int = None
) -> int:
    """
    新しいコアライブラリバージョンを登録
    
    Args:
        version: バージョン文字列（例: 1.0.0）
        update_info: 更新内容の説明
        commit_hash: Gitコミットハッシュ（40文字）
        base_version_id: ベースバージョンのID（新規の場合はNone）
    
    Returns:
        core_lib_ID: 作成されたコアライブラリのID
    
    Raises:
        ValueError: コミットハッシュが重複する場合
    """
```

#### コアライブラリの評価結果登録
```python
def create_core_lib_output(
    core_lib_id: int, 
    video_id: int, 
    output_dir: str
) -> int:
    """
    コアライブラリの評価結果を登録
    
    Args:
        core_lib_id: コアライブラリID
        video_id: ビデオID
        output_dir: 出力ディレクトリパス
    
    Returns:
        core_lib_output_ID: 作成された出力のID
    """
```

### 6. アルゴリズム管理API

#### アルゴリズムバージョンの登録
```python
def create_algorithm_version(
    version: str, 
    update_info: str, 
    commit_hash: str, 
    base_version_id: int = None
) -> int:
    """
    新しいアルゴリズムバージョンを登録
    
    Args:
        version: バージョン文字列（例: 2.1.0）
        update_info: 更新内容の説明
        commit_hash: Gitコミットハッシュ（40文字）
        base_version_id: ベースバージョンのID（新規の場合はNone）
    
    Returns:
        algorithm_ID: 作成されたアルゴリズムのID
    """
```

#### アルゴリズムの評価結果登録
```python
def create_algorithm_output(
    algorithm_id: int, 
    core_lib_output_id: int, 
    output_dir: str
) -> int:
    """
    アルゴリズムの評価結果を登録
    
    Args:
        algorithm_id: アルゴリズムID
        core_lib_output_id: コアライブラリ出力ID
        output_dir: 出力ディレクトリパス
    
    Returns:
        algorithm_output_ID: 作成された出力のID
    """
```

## 検索・分析API

### 1. 複合検索API

#### タスク実行状況の検索
```python
def search_task_executions(
    task_set: int = None,
    subject_id: int = None,
    date_from: str = None,
    date_to: str = None
) -> List[dict]:
    """
    タスク実行状況を検索
    
    Args:
        task_set: タスクセット番号
        subject_id: 被験者ID
        date_from: 開始日（YYYY-MM-DD）
        date_to: 終了日（YYYY-MM-DD）
    
    Returns:
        List[dict]: タスク実行情報のリスト
    """
```

#### バージョン履歴の取得
```python
def get_version_history(table_name: str, current_id: int) -> List[dict]:
    """
    バージョン履歴を取得（自己参照テーブル用）
    
    Args:
        table_name: テーブル名（'core_lib_table' または 'algorithm_table'）
        current_id: 現在のバージョンID
    
    Returns:
        List[dict]: バージョン履歴のリスト
    """
```

### 2. 統計情報API

#### テーブル件数統計
```python
def get_table_statistics() -> dict:
    """
    全テーブルの件数統計を取得
    
    Returns:
        dict: テーブル名と件数の辞書
    """
```

#### データ整合性チェック
```python
def check_data_integrity() -> dict:
    """
    データ整合性をチェック
    
    Returns:
        dict: 整合性チェック結果
    """
```

## エラーハンドリング

### カスタム例外クラス
```python
class DWHError(Exception):
    """DataWareHouse関連の基本例外クラス"""
    pass

class DWHConstraintError(DWHError):
    """制約違反エラー"""
    pass

class DWHNotFoundError(DWHError):
    """データが見つからないエラー"""
    pass

class DWHValidationError(DWHError):
    """データ検証エラー"""
    pass
```

### エラーコード
- `E001`: 外部キー制約違反
- `E002`: UNIQUE制約違反
- `E003`: データが見つからない
- `E004`: データ検証エラー
- `E005`: データベース接続エラー

## 使用例

### 基本的な使用パターン
```python
from datawarehouse.api import DWHConnection, create_task, create_subject

# 被験者とタスクの登録
with DWHConnection() as conn:
    # 被験者を登録
    subject_id = create_subject("Subject A")
    
    # タスクを登録
    task_id = create_task(1, "Task 1", "Evaluate positive detection")
    
    print(f"Created subject: {subject_id}, task: {task_id}")
```

### バッチ処理の例
```python
def batch_register_videos(video_data_list: List[dict]):
    """ビデオデータを一括登録"""
    with DWHConnection() as conn:
        try:
            for video_data in video_data_list:
                create_video(**video_data)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
```

## パフォーマンス考慮事項

### 1. インデックス活用
- バージョン検索用インデックスが既に作成済み
- 必要に応じて追加インデックスを作成

### 2. バッチ処理
- 大量データ投入時はトランザクション内で一括処理
- 適切なバッチサイズの設定

### 3. 接続プール
- 高頻度アクセス時は接続プールの検討
- 現在は単純な接続管理

## セキュリティ考慮事項

### 1. SQLインジェクション対策
- パラメータ化クエリの使用
- 入力値の検証

### 2. アクセス制御
- ファイルシステムレベルでのアクセス制御
- 必要に応じて認証・認可機能の追加

## 拡張性

### 1. プラグイン対応
- 新しいテーブルやAPIの追加が容易
- 設定ファイルによる動作カスタマイズ

### 2. 監査ログ
- データ変更履歴の記録
- 必要に応じて監査テーブルの追加

---

このAPI仕様書に基づいて、各モジュールはDataWareHouseに安全かつ効率的にアクセスできます。
