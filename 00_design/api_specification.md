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

## 実装アーキテクチャ（Serena MCP構造解析）

### 4層アーキテクチャ実装
本API仕様書は、以下の4層構造で実装されています：

#### 1. 基盤層（Foundation Layer）
```python
# connection.py - データベース接続管理
class DWHConnection:
    """コンテキストマネージャーによる自動接続管理"""
    
def get_connection(db_path: str) -> DWHConnection:
    """統一された接続取得インターフェース"""

# exceptions.py - 統一例外処理
class DWHError(Exception): pass                    # 基本例外
class DWHConstraintError(DWHError): pass          # 制約違反 (E001)
class DWHUniqueConstraintError(DWHError): pass    # UNIQUE制約違反 (E002) 
class DWHNotFoundError(DWHError): pass            # データ未発見 (E003)
class DWHValidationError(DWHError): pass          # 検証エラー (E004)
class DWHConnectionError(DWHError): pass          # 接続エラー (E005)
```

#### 2. データ管理層（Data Management Layer）
```python
# 基本CRUD操作パターンの統一実装
# task_api.py (5関数), subject_api.py (6関数), 
# video_api.py (6関数), tag_api.py (8関数)

def create_{entity}(...) -> int:      # エンティティ作成
def get_{entity}(id: int) -> Dict:    # ID検索
def list_{entities}(...) -> List:    # 一覧取得
def update_{entity}(...) -> None:    # 更新
def delete_{entity}(id: int) -> None: # 削除
```

#### 3. バージョン管理層（Version Management Layer）
```python
# core_lib_api.py (10関数), algorithm_api.py (11関数)
# Gitコミットハッシュベースの厳密なバージョン管理

def _validate_commit_hash(commit_hash: str) -> None:
    """40文字SHA-1ハッシュ検証"""

def create_{lib}_version(..., commit_hash: str, base_version_id: Optional[int]) -> int:
    """自己参照によるバージョン履歴構築"""

def get_{lib}_version_history(id: int) -> List[Dict]:
    """再帰的バージョン履歴取得"""

def find_{lib}_by_commit_hash(commit_hash: str) -> Optional[Dict]:
    """コミットハッシュ検索"""
```

#### 4. 分析層（Analytics Layer）
```python
# analytics_api.py (6関数) - 横断的分析機能

def search_task_executions(...) -> List[Dict]:
    """複合条件検索"""

def check_data_integrity() -> Dict:
    """外部キー制約、孤立レコード、重複ハッシュ検証"""

def get_performance_metrics() -> Dict:
    """パフォーマンス統計"""

def get_processing_pipeline_summary(...) -> List[Dict]:
    """処理パイプライン概要"""
```

### インターフェース層（Interface Layer）
```python
# __init__.py - 統一API公開（50+関数）
__version__ = "0.1.0"
__all__ = [
    # 基盤層
    "DWHConnection", "get_connection", "DWHError", ...,
    # データ管理層  
    "create_task", "get_task", ..., "create_subject", ...,
    # バージョン管理層
    "create_core_lib_version", ..., "create_algorithm_version", ...,
    # 分析層
    "search_task_executions", "check_data_integrity", ...
]
```

### 設計パターンと実装特徴

#### 1. 統一されたエラーハンドリング
```python
try:
    result = api_function(...)
except DWHConstraintError as e:
    # 制約違反の詳細処理 (table_name, constraint_name属性)
except DWHNotFoundError as e:
    # データ未発見の詳細処理 (record_id属性)
except DWHValidationError as e:
    # 検証エラーの詳細処理 (field_name, field_value属性)
```

#### 2. コンテキスト管理パターン
```python
# 自動接続管理
with get_connection(db_path) as conn:
    # 自動的に外部キー制約有効化
    # 自動的にRow factory設定
    # 例外時自動ロールバック、正常時自動コミット
    cursor = conn.cursor()
    ...
```

#### 3. バージョン管理パターン
```python
# 自己参照による履歴追跡
v1_id = create_core_lib_version("1.0.0", "初期版", "hash1", None)
v2_id = create_core_lib_version("1.1.0", "改良版", "hash2", v1_id)
history = get_core_lib_version_history(v2_id)  # [v1.0.0, v1.1.0]順
```

### モジュール間依存関係
```
analytics_api.py ←→ core_lib_api.py, algorithm_api.py
       ↓
[8 API modules] → connection.py, exceptions.py
       ↓
SQLite3 Database (8 tables)
```

この実装により、型安全で保守性の高い、包括的なDataWareHouse APIライブラリが完成しています。
