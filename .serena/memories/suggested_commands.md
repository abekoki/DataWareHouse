# 推奨コマンド

## パッケージ管理
```powershell
# 仮想環境作成
uv venv .venv

# 依存関係の同期
uv sync

# Pythonスクリプト実行
uv run python <script_name>
```

## データベース管理
```powershell
# データベース初期化・更新
uv run python scripts/create_database.py

# データベース構造確認
uv run python scripts/query_db_structure.py
```

## 開発・テスト
```powershell
# パッケージ使用例
uv run python examples/basic_usage.py
uv run python examples/advanced_usage.py
```

## Git操作
```powershell
# 状態確認
git status

# 変更のコミット
git add .
git commit -m "コミットメッセージ"

# リモートへのプッシュ
git push origin main
```

## ファイル管理（Windows）
```powershell
# ディレクトリ内容確認
dir
ls  # PowerShellのエイリアス

# ファイル検索
Get-ChildItem -Recurse -Name "*.py"

# テキスト検索
Select-String -Path "*.py" -Pattern "pattern"
```

## バックアップ
```powershell
# データベースバックアップ
copy database.db database_backup.db
```