# DataWareHouse - ビデオ処理評価システム

## 概要
ビデオデータに基づくタスクのタグ付け、コアライブラリとメインアルゴリズムのバージョン管理、およびそれらの出力結果を管理するためのデータベースシステムです。

## 機能
- **タスク管理**: ビデオ内のタスク区間をタグ付け
- **バージョン管理**: コアライブラリとアルゴリズムのバージョン履歴追跡
- **出力管理**: 評価結果の格納と管理
- **データ整合性**: 外部キー制約による参照整合性の保証

## システム構成

### ディレクトリ構造
```
DataWareHouse/
├── 00_design/                    # 設計・仕様書
│   ├── database_spec_with_timing.md  # データベース仕様書
│   └── schema.sql               # SQLiteスキーマ
├── 01_mov_data/                 # ビデオデータ格納
├── 02_core_lib_output/          # コアライブラリ評価結果
├── 03_algorithm_output/         # アルゴリズム評価結果
├── scripts/                      # ユーティリティスクリプト
│   ├── create_database.py       # データベース初期化
│   └── query_db_structure.py    # データベース構造確認
├── datawarehouse/                # プロジェクトパッケージ
├── database.db                   # SQLiteデータベース
├── pyproject.toml               # uv設定
└── .gitignore                   # Git除外設定
```

### データベーススキーマ
- **8テーブル**: タスク、被験者、ビデオ、タグ、コアライブラリ、アルゴリズム、出力管理
- **外部キー制約**: データ整合性の保証
- **自己参照**: バージョン履歴の追跡

## セットアップ

### 前提条件
- Windows 10/11
- Python 3.10以上
- uv（Pythonパッケージ管理ツール）

### 1. uvのインストール
```powershell
# PowerShellで実行
iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
```

### 2. 仮想環境の作成
```powershell
# 仮想環境作成（.venv固定）
uv venv .venv

# 依存関係の同期
uv sync
```

### 3. データベースの初期化
```powershell
# データベース作成・更新
uv run python scripts/create_database.py
```

## 使用方法

### データベース構造の確認
```powershell
# テーブル構造、外部キー制約、インデックス情報を表示
uv run python scripts/query_db_structure.py
```

### データ投入フロー
1. **準備段階**: `task_table`, `subject_table` にタスク・被験者情報を登録
2. **データ収集後**: `video_table`, `tag_table` にビデオ・タグ情報を登録
3. **コアライブラリ更新**: `core_lib_table` に新バージョンを登録
4. **コアライブラリ評価**: `core_lib_output_table` に評価結果を登録
5. **アルゴリズム更新**: `algorithm_table` に新バージョンを登録
6. **アルゴリズム評価**: `algorithm_output_table` に評価結果を登録

## 開発・運用

### 外部キー制約
- SQLiteでは接続ごとに `PRAGMA foreign_keys = ON;` が必要
- アプリケーション起動時に必ず実行してください

### バックアップ
```powershell
# データベースのバックアップ
copy database.db database_backup.db
```

### ログ管理
- 作業内容は `log.md` に記録
- 日付付きで活動内容を管理

## 技術仕様

### データベース
- **エンジン**: SQLite3
- **特徴**: 軽量、組み込み型、サーバーレス
- **制約**: 外部キー制約、UNIQUE制約、インデックス

### バージョン管理
- **形式**: セマンティックバージョニング（例: 1.0.0）
- **識別子**: Gitコミットハッシュ（SHA-1, 40文字）
- **履歴**: 自己参照によるバージョン履歴追跡

### ファイル管理
- **ビデオ**: MP4形式（.gitignoreで除外）
- **出力**: CSV、その他評価結果ファイル
- **設定**: YAML/TOML形式

## トラブルシューティング

### よくある問題
1. **外部キー制約が無効**: `PRAGMA foreign_keys = ON;` を実行
2. **uv syncエラー**: `datawarehouse/` パッケージが存在することを確認
3. **データベースアクセスエラー**: ファイルパーミッションを確認

### ログ確認
- エラー詳細は `log.md` を参照
- データベース構造は `scripts/query_db_structure.py` で確認

## ライセンス
プロジェクト固有のライセンス情報を記載してください。

## 貢献
1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

---

**注意**: 本システムは研究・開発用途を想定しています。本格運用前に十分なテストを行ってください。
