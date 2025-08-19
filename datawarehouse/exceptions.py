"""
DataWareHouse カスタム例外クラス
"""


class DWHError(Exception):
    """DataWareHouse関連の基本例外クラス"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code


class DWHConstraintError(DWHError):
    """制約違反エラー"""
    def __init__(self, message: str, table_name: str = None, constraint_name: str = None):
        super().__init__(message, "E001")
        self.table_name = table_name
        self.constraint_name = constraint_name


class DWHNotFoundError(DWHError):
    """データが見つからないエラー"""
    def __init__(self, message: str, table_name: str = None, record_id: int = None):
        super().__init__(message, "E003")
        self.table_name = table_name
        self.record_id = record_id


class DWHValidationError(DWHError):
    """データ検証エラー"""
    def __init__(self, message: str, field_name: str = None, field_value=None):
        super().__init__(message, "E004")
        self.field_name = field_name
        self.field_value = field_value


class DWHConnectionError(DWHError):
    """データベース接続エラー"""
    def __init__(self, message: str, db_path: str = None):
        super().__init__(message, "E005")
        self.db_path = db_path


class DWHUniqueConstraintError(DWHError):
    """UNIQUE制約違反エラー"""
    def __init__(self, message: str, table_name: str = None, field_name: str = None):
        super().__init__(message, "E002")
        self.table_name = table_name
        self.field_name = field_name
