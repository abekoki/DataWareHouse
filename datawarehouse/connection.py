"""
DataWareHouse データベース接続管理
"""

import sqlite3
from pathlib import Path
from typing import Optional
from .exceptions import DWHConnectionError


class DWHConnection:
    """DataWareHouseへの接続を管理するクラス"""
    
    def __init__(self, db_path: str = "database.db"):
        """
        初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def __enter__(self) -> sqlite3.Connection:
        """コンテキストマネージャー開始"""
        try:
            # データベースファイルの存在確認
            if not Path(self.db_path).exists():
                raise DWHConnectionError(
                    f"Database file not found: {self.db_path}",
                    db_path=self.db_path
                )
            
            # 接続を作成
            self.connection = sqlite3.connect(self.db_path)
            
            # 外部キー制約を有効化
            self.connection.execute("PRAGMA foreign_keys = ON;")
            
            # Row factory設定（辞書形式でアクセス可能）
            self.connection.row_factory = sqlite3.Row
            
            return self.connection
            
        except sqlite3.Error as e:
            raise DWHConnectionError(
                f"Failed to connect to database: {e}",
                db_path=self.db_path
            ) from e
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        if self.connection:
            if exc_type is None:
                # 正常終了時はコミット
                self.connection.commit()
            else:
                # 例外発生時はロールバック
                self.connection.rollback()
            
            self.connection.close()
            self.connection = None


def get_connection(db_path: str = "database.db") -> DWHConnection:
    """
    データベース接続を取得
    
    Args:
        db_path: データベースファイルのパス
    
    Returns:
        DWHConnection: データベース接続オブジェクト
    """
    return DWHConnection(db_path)
