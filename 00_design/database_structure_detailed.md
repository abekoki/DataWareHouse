# DataWareHouse データベース構造詳細説明書

## 概要
この文書は、DataWareHouseのデータベース構造について詳細に説明します。SQLite3を使用し、8つのテーブルで構成される正規化されたデータベース設計です。

## データベース概要

### 基本情報
- **データベースエンジン**: SQLite3
- **ファイル名**: `database.db`
- **文字エンコーディング**: UTF-8
- **外部キー制約**: 有効（接続ごとに設定が必要）

### テーブル構成
- **基本テーブル**: 4テーブル（タスク、被験者、ビデオ、タグ）
- **バージョン管理テーブル**: 2テーブル（コアライブラリ、アルゴリズム）
- **出力管理テーブル**: 2テーブル（コアライブラリ出力、アルゴリズム出力）

## テーブル詳細

### 1. task_table（タスクテーブル）

#### 目的
ビデオ内で実行されるタスクの定義を管理します。

#### スキーマ
```sql
CREATE TABLE task_table (
    task_ID INTEGER PRIMARY KEY AUTOINCREMENT,  -- タスクの一意識別子
    task_set INTEGER,                           -- タスクセット番号
    task_name TEXT,                             -- タスク名
    task_describe TEXT                           -- タスクの詳細説明
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `task_ID` | INTEGER | PK, AUTOINCREMENT | タスクの一意識別子 | 1, 2, 3... |
| `task_set` | INTEGER | - | タスクのセット番号 | 1（正検知評価用1） |
| `task_name` | TEXT | - | タスクの名前 | "Task 1", "正検知評価" |
| `task_describe` | TEXT | - | タスクの詳細説明 | "ビデオ内の正検知を評価する" |

#### データ例
```sql
INSERT INTO task_table (task_set, task_name, task_describe) VALUES
(1, '正検知評価', 'ビデオ内の正検知を評価するタスク'),
(1, '誤検知評価', 'ビデオ内の誤検知を評価するタスク'),
(2, '動作分析', '被験者の動作パターンを分析するタスク');
```

### 2. subject_table（被験者テーブル）

#### 目的
ビデオデータの被験者情報を管理します。

#### スキーマ
```sql
CREATE TABLE subject_table (
    subject_ID INTEGER PRIMARY KEY AUTOINCREMENT,  -- 被験者の一意識別子
    subject_name TEXT                              -- 被験者名
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `subject_ID` | INTEGER | PK, AUTOINCREMENT | 被験者の一意識別子 | 1, 2, 3... |
| `subject_name` | TEXT | - | 被験者の名前 | "Subject A", "被験者1" |

#### データ例
```sql
INSERT INTO subject_table (subject_name) VALUES
('Subject A'),
('Subject B'),
('被験者1');
```

### 3. video_table（ビデオテーブル）

#### 目的
ビデオファイルのメタデータを管理します。

#### スキーマ
```sql
CREATE TABLE video_table (
    video_ID INTEGER PRIMARY KEY AUTOINCREMENT,    -- ビデオの一意識別子
    video_dir TEXT,                                -- ビデオファイルのディレクトリパス
    subject_ID INTEGER,                            -- 被験者ID（外部キー）
    video_date TEXT,                               -- ビデオ取得日
    video_length INTEGER,                          -- ビデオの長さ（秒）
    FOREIGN KEY (subject_ID) REFERENCES subject_table(subject_ID) ON DELETE RESTRICT
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `video_ID` | INTEGER | PK, AUTOINCREMENT | ビデオの一意識別子 | 1, 2, 3... |
| `video_dir` | TEXT | - | ビデオファイルのパス | "01_mov_data/subject_a.mp4" |
| `subject_ID` | INTEGER | FK | 被験者ID | 1（subject_table.subject_IDを参照） |
| `video_date` | TEXT | - | 取得日（YYYY-MM-DD） | "2025-08-19" |
| `video_length` | INTEGER | - | ビデオの長さ（秒） | 120, 300 |

#### 外部キー制約
- `subject_ID` → `subject_table.subject_ID`
- `ON DELETE RESTRICT`: 被験者を削除する際、関連するビデオがある場合は削除を拒否

#### データ例
```sql
INSERT INTO video_table (video_dir, subject_ID, video_date, video_length) VALUES
('01_mov_data/subject_a_task1.mp4', 1, '2025-08-19', 120),
('01_mov_data/subject_a_task2.mp4', 1, '2025-08-19', 180),
('01_mov_data/subject_b_task1.mp4', 2, '2025-08-19', 150);
```

### 4. tag_table（タグテーブル）

#### 目的
ビデオ内のタスク実行区間をタグ付けします。

#### スキーマ
```sql
CREATE TABLE tag_table (
    tag_ID INTEGER PRIMARY KEY AUTOINCREMENT,      -- タグの一意識別子
    video_ID INTEGER,                              -- ビデオID（外部キー）
    task_ID INTEGER,                               -- タスクID（外部キー）
    start INTEGER,                                 -- 開始フレーム
    end INTEGER,                                   -- 終了フレーム
    FOREIGN KEY (video_ID) REFERENCES video_table(video_ID) ON DELETE RESTRICT,
    FOREIGN KEY (task_ID) REFERENCES task_table(task_ID) ON DELETE RESTRICT
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `tag_ID` | INTEGER | PK, AUTOINCREMENT | タグの一意識別子 | 1, 2, 3... |
| `video_ID` | INTEGER | FK | ビデオID | 1（video_table.video_IDを参照） |
| `task_ID` | INTEGER | FK | タスクID | 1（task_table.task_IDを参照） |
| `start` | INTEGER | - | 開始フレーム番号 | 0, 30, 60 |
| `end` | INTEGER | - | 終了フレーム番号 | 30, 60, 90 |

#### 外部キー制約
- `video_ID` → `video_table.video_ID`
- `task_ID` → `task_table.task_ID`
- `ON DELETE RESTRICT`: 関連するビデオやタスクを削除する際、タグがある場合は削除を拒否

#### データ例
```sql
INSERT INTO tag_table (video_ID, task_ID, start, end) VALUES
(1, 1, 0, 30),    -- ビデオ1のタスク1: 0-30フレーム
(1, 1, 60, 90),   -- ビデオ1のタスク1: 60-90フレーム
(2, 2, 0, 45);    -- ビデオ2のタスク2: 0-45フレーム
```

### 5. core_lib_table（コアライブラリテーブル）

#### 目的
コアライブラリのバージョン履歴を管理します。自己参照により、バージョン間の関係を追跡できます。

#### スキーマ
```sql
CREATE TABLE core_lib_table (
    core_lib_ID INTEGER PRIMARY KEY AUTOINCREMENT,           -- コアライブラリの一意識別子
    core_lib_version TEXT,                                   -- バージョン文字列
    core_lib_update_information TEXT,                        -- 更新内容の説明
    core_lib_base_version_ID INTEGER,                        -- ベースバージョンID（自己参照）
    core_lib_commit_hash TEXT UNIQUE,                        -- Gitコミットハッシュ
    FOREIGN KEY (core_lib_base_version_ID) REFERENCES core_lib_table(core_lib_ID) ON DELETE SET NULL
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `core_lib_ID` | INTEGER | PK, AUTOINCREMENT | コアライブラリの一意識別子 | 1, 2, 3... |
| `core_lib_version` | TEXT | - | バージョン文字列 | "1.0.0", "1.1.0" |
| `core_lib_update_information` | TEXT | - | 更新内容の説明 | "バグ修正", "新機能追加" |
| `core_lib_base_version_ID` | INTEGER | FK, 自己参照 | ベースバージョンID | 1（前のバージョンを参照） |
| `core_lib_commit_hash` | TEXT | UNIQUE | Gitコミットハッシュ | "a1b2c3d4e5f6..." |

#### 外部キー制約
- `core_lib_base_version_ID` → `core_lib_table.core_lib_ID`（自己参照）
- `ON DELETE SET NULL`: ベースバージョンが削除された場合、NULLに設定

#### インデックス
```sql
CREATE INDEX idx_core_lib_version ON core_lib_table(core_lib_version);
```

#### データ例
```sql
INSERT INTO core_lib_table (core_lib_version, core_lib_update_information, core_lib_base_version_ID, core_lib_commit_hash) VALUES
('1.0.0', '初期バージョン', NULL, 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2'),
('1.1.0', 'バグ修正', 1, 'b2c3d4e5f6b2c3d4e5f6b2c3d4e5f6b2c3d4e5f6b2c3'),
('1.2.0', '新機能追加', 2, 'c3d4e5f6c3d4e5f6c3d4e5f6c3d4e5f6c3d4e5f6c3d4');
```

### 6. core_lib_output_table（コアライブラリ出力テーブル）

#### 目的
コアライブラリの評価実行結果を管理します。

#### スキーマ
```sql
CREATE TABLE core_lib_output_table (
    core_lib_output_ID INTEGER PRIMARY KEY AUTOINCREMENT,    -- 出力の一意識別子
    core_lib_ID INTEGER,                                     -- コアライブラリID（外部キー）
    video_ID INTEGER,                                        -- ビデオID（外部キー）
    core_lib_output_dir TEXT,                                -- 出力ディレクトリパス
    FOREIGN KEY (core_lib_ID) REFERENCES core_lib_table(core_lib_ID) ON DELETE RESTRICT,
    FOREIGN KEY (video_ID) REFERENCES video_table(video_ID) ON DELETE RESTRICT
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `core_lib_output_ID` | INTEGER | PK, AUTOINCREMENT | 出力の一意識別子 | 1, 2, 3... |
| `core_lib_ID` | INTEGER | FK | コアライブラリID | 1（core_lib_table.core_lib_IDを参照） |
| `video_ID` | INTEGER | FK | ビデオID | 1（video_table.video_IDを参照） |
| `core_lib_output_dir` | TEXT | - | 出力ディレクトリパス | "02_core_lib_output/v1.0.0_subject_a" |

#### 外部キー制約
- `core_lib_ID` → `core_lib_table.core_lib_ID`
- `video_ID` → `video_table.video_ID`
- `ON DELETE RESTRICT`: 関連するコアライブラリやビデオを削除する際、出力がある場合は削除を拒否

#### データ例
```sql
INSERT INTO core_lib_output_table (core_lib_ID, video_ID, core_lib_output_dir) VALUES
(1, 1, '02_core_lib_output/v1.0.0_subject_a_task1'),
(1, 2, '02_core_lib_output/v1.0.0_subject_a_task2'),
(2, 1, '02_core_lib_output/v1.1.0_subject_a_task1');
```

### 7. algorithm_table（アルゴリズムテーブル）

#### 目的
メインアルゴリズムのバージョン履歴を管理します。コアライブラリと同様に自己参照により、バージョン間の関係を追跡できます。

#### スキーマ
```sql
CREATE TABLE algorithm_table (
    algorithm_ID INTEGER PRIMARY KEY AUTOINCREMENT,           -- アルゴリズムの一意識別子
    algorithm_version TEXT,                                   -- バージョン文字列
    algorithm_update_information TEXT,                        -- 更新内容の説明
    algorithm_base_version_ID INTEGER,                        -- ベースバージョンID（自己参照）
    algorithm_commit_hash TEXT UNIQUE,                        -- Gitコミットハッシュ
    FOREIGN KEY (algorithm_base_version_ID) REFERENCES algorithm_table(algorithm_ID) ON DELETE SET NULL
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `algorithm_ID` | INTEGER | PK, AUTOINCREMENT | アルゴリズムの一意識別子 | 1, 2, 3... |
| `algorithm_version` | TEXT | - | バージョン文字列 | "2.0.0", "2.1.0" |
| `algorithm_update_information` | TEXT | - | 更新内容の説明 | "精度向上", "処理速度改善" |
| `algorithm_base_version_ID` | INTEGER | FK, 自己参照 | ベースバージョンID | 1（前のバージョンを参照） |
| `algorithm_commit_hash` | TEXT | UNIQUE | Gitコミットハッシュ | "f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2" |

#### 外部キー制約
- `algorithm_base_version_ID` → `algorithm_table.algorithm_ID`（自己参照）
- `ON DELETE SET NULL`: ベースバージョンが削除された場合、NULLに設定

#### インデックス
```sql
CREATE INDEX idx_algorithm_version ON algorithm_table(algorithm_version);
```

#### データ例
```sql
INSERT INTO algorithm_table (algorithm_version, algorithm_update_information, algorithm_base_version_ID, algorithm_commit_hash) VALUES
('2.0.0', '初期バージョン', NULL, 'f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2'),
('2.1.0', '精度向上', 1, 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3'),
('2.2.0', '処理速度改善', 2, 'b2c3d4e5f6b2c3d4e5f6b2c3d4e5f6b2c3d4e5f6b2c3');
```

### 8. algorithm_output_table（アルゴリズム出力テーブル）

#### 目的
メインアルゴリズムの評価実行結果を管理します。

#### スキーマ
```sql
CREATE TABLE algorithm_output_table (
    algorithm_output_ID INTEGER PRIMARY KEY AUTOINCREMENT,    -- 出力の一意識別子
    algorithm_ID INTEGER,                                     -- アルゴリズムID（外部キー）
    core_lib_output_ID INTEGER,                               -- コアライブラリ出力ID（外部キー）
    algorithm_output_dir TEXT,                                -- 出力ディレクトリパス
    FOREIGN KEY (algorithm_ID) REFERENCES algorithm_table(algorithm_ID) ON DELETE RESTRICT,
    FOREIGN KEY (core_lib_output_ID) REFERENCES core_lib_output_table(core_lib_output_ID) ON DELETE RESTRICT
);
```

#### フィールド詳細
| フィールド名 | データ型 | 制約 | 説明 | 例 |
|-------------|----------|------|------|-----|
| `algorithm_output_ID` | INTEGER | PK, AUTOINCREMENT | 出力の一意識別子 | 1, 2, 3... |
| `algorithm_ID` | INTEGER | FK | アルゴリズムID | 1（algorithm_table.algorithm_IDを参照） |
| `core_lib_output_ID` | INTEGER | FK | コアライブラリ出力ID | 1（core_lib_output_table.core_lib_output_IDを参照） |
| `algorithm_output_dir` | TEXT | - | 出力ディレクトリパス | "03_algorithm_output/v2.0.0_core_v1.0.0" |

#### 外部キー制約
- `algorithm_ID` → `algorithm_table.algorithm_ID`
- `core_lib_output_ID` → `core_lib_output_table.core_lib_output_ID`
- `ON DELETE RESTRICT`: 関連するアルゴリズムやコアライブラリ出力を削除する際、出力がある場合は削除を拒否

#### データ例
```sql
INSERT INTO algorithm_output_table (algorithm_ID, core_lib_output_ID, algorithm_output_dir) VALUES
(1, 1, '03_algorithm_output/v2.0.0_core_v1.0.0_subject_a_task1'),
(1, 2, '03_algorithm_output/v2.0.0_core_v1.0.0_subject_a_task2'),
(2, 1, '03_algorithm_output/v2.1.0_core_v1.0.0_subject_a_task1');
```

## テーブル間の関係

### 1. 基本関係（1:N）
```
subject_table (1) ←→ (N) video_table
video_table (1) ←→ (N) tag_table
task_table (1) ←→ (N) tag_table
```

### 2. 出力関係（1:N）
```
video_table (1) ←→ (N) core_lib_output_table
core_lib_table (1) ←→ (N) core_lib_output_table
core_lib_output_table (1) ←→ (N) algorithm_output_table
algorithm_table (1) ←→ (N) algorithm_output_table
```

### 3. 自己参照関係（1:N）
```
core_lib_table (1) ←→ (N) core_lib_table (core_lib_base_version_ID)
algorithm_table (1) ←→ (N) algorithm_table (algorithm_base_version_ID)
```

### 4. 多対多関係（N:M）
```
video_table ←→ task_table (tag_tableを介して)
```

## データ整合性ルール

### 1. 外部キー制約
- すべての外部キーは適切なテーブルを参照
- `ON DELETE RESTRICT`: 参照されているデータの削除を防止
- `ON DELETE SET NULL`: 自己参照の場合のみNULL許可

### 2. 一意性制約
- `core_lib_commit_hash`: コミットハッシュの重複を防止
- `algorithm_commit_hash`: コミットハッシュの重複を防止

### 3. データ検証ルール
- `start < end`: フレーム区間の妥当性（アプリケーション層で検証）
- 日付形式: `YYYY-MM-DD`（ISO 8601準拠）
- コミットハッシュ: 40文字の16進数文字列

## インデックス戦略

### 1. 既存インデックス
```sql
-- バージョン検索用
CREATE INDEX idx_core_lib_version ON core_lib_table(core_lib_version);
CREATE INDEX idx_algorithm_version ON algorithm_table(algorithm_version);

-- 自動生成インデックス
-- sqlite_autoindex_core_lib_table_1 (core_lib_commit_hash UNIQUE)
-- sqlite_autoindex_algorithm_table_1 (algorithm_commit_hash UNIQUE)
```

### 2. 推奨追加インデックス
```sql
-- 検索パフォーマンス向上用
CREATE INDEX idx_video_subject ON video_table(subject_ID);
CREATE INDEX idx_video_date ON video_table(video_date);
CREATE INDEX idx_tag_video ON tag_table(video_ID);
CREATE INDEX idx_tag_task ON tag_table(task_ID);
CREATE INDEX idx_core_lib_output_video ON core_lib_output_table(video_ID);
CREATE INDEX idx_algorithm_output_core ON algorithm_output_table(core_lib_output_ID);
```

## データ投入フロー

### 1. 初期設定フェーズ
```
1. task_table ← タスク定義を登録
2. subject_table ← 被験者情報を登録
```

### 2. データ収集フェーズ
```
3. video_table ← ビデオメタデータを登録
4. tag_table ← タスク区間をタグ付け
```

### 3. 評価実行フェーズ
```
5. core_lib_table ← コアライブラリバージョンを登録
6. core_lib_output_table ← コアライブラリ評価結果を登録
7. algorithm_table ← アルゴリズムバージョンを登録
8. algorithm_output_table ← アルゴリズム評価結果を登録
```

## パフォーマンス考慮事項

### 1. クエリ最適化
- JOINの順序を最適化
- 適切なインデックスの使用
- 大量データ時のページネーション

### 2. データサイズ管理
- 古いデータのアーカイブ
- 定期的なVACUUM実行
- 不要なインデックスの削除

### 3. 接続管理
- 適切なタイムアウト設定
- 接続プールの検討（高頻度アクセス時）
- トランザクションサイズの最適化

## バックアップ・復旧

### 1. バックアップ戦略
```bash
# データベースファイルのバックアップ
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db

# スキーマのバックアップ
sqlite3 database.db .schema > schema_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 復旧手順
```bash
# データベースファイルの復旧
cp database_backup_YYYYMMDD_HHMMSS.db database.db

# スキーマの再適用（必要時）
sqlite3 database.db < schema_backup_YYYYMMDD_HHMMSS.sql
```

## 監視・メンテナンス

### 1. 定期チェック項目
- テーブル件数の確認
- 外部キー制約の整合性チェック
- インデックスの使用状況
- データベースファイルサイズ

### 2. メンテナンスコマンド
```sql
-- 統計情報の確認
ANALYZE;

-- データベースの最適化
VACUUM;

-- インデックスの再構築
REINDEX;
```

---

このデータベース構造により、ビデオ処理評価システムのデータを体系的に管理し、バージョン履歴の追跡と評価結果の管理を効率的に行うことができます。
