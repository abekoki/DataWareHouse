# コードスタイルと規約

## ドキュメント
- **docstring**: 全関数に日本語のdocstringが記載
- **型ヒント**: typing モジュールを使用してすべての関数パラメータと戻り値に型注釈
- **インポート**: 標準ライブラリ → サードパーティ → ローカルモジュールの順序

## 命名規則
- **関数名**: snake_case（例: create_task, get_video）
- **クラス名**: PascalCase（例: DWHConnection, DWHError）
- **変数名**: snake_case
- **定数**: UPPER_SNAKE_CASE

## ファイル構造
- **API モジュール**: `{entity}_api.py` 形式（例: task_api.py, video_api.py）
- **例外クラス**: exceptions.py に集約
- **接続管理**: connection.py に集約

## エラーハンドリング
- カスタム例外クラスを使用
- 適切なエラーメッセージと詳細情報を提供
- SQLite例外をラップして一貫したエラー処理

## データベースアクセス
- コンテキストマネージャーを使用した接続管理
- 外部キー制約を有効化（PRAGMA foreign_keys = ON）
- Row factoryを使用した辞書形式でのアクセス