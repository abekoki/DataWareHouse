"""
DataWareHouse API ライブラリ

このライブラリは、ビデオ処理評価システムのDataWareHouseにアクセスするための
包括的なAPIを提供します。
"""

# 接続管理
from .connection import DWHConnection, get_connection

# 例外クラス
from .exceptions import (
    DWHError,
    DWHConstraintError,
    DWHNotFoundError,
    DWHValidationError,
    DWHConnectionError,
    DWHUniqueConstraintError
)

# API関数
from .task_api import (
    create_task,
    get_task,
    list_tasks,
    update_task,
    delete_task
)

from .subject_api import (
    create_subject,
    get_subject,
    list_subjects,
    update_subject,
    delete_subject,
    find_subject_by_name
)

from .video_api import (
    create_video,
    get_video,
    list_videos,
    get_videos_by_subject,
    update_video,
    delete_video
)

from .tag_api import (
    create_tag,
    get_tag,
    get_video_tags,
    get_task_tags,
    list_tags,
    update_tag,
    delete_tag,
    get_tag_duration
)

from .core_lib_api import (
    create_core_lib_version,
    get_core_lib_version,
    list_core_lib_versions,
    get_core_lib_version_history,
    find_core_lib_by_version,
    find_core_lib_by_commit_hash,
    create_core_lib_output,
    get_core_lib_output,
    list_core_lib_outputs
)

from .algorithm_api import (
    create_algorithm_version,
    get_algorithm_version,
    list_algorithm_versions,
    get_algorithm_version_history,
    find_algorithm_by_version,
    find_algorithm_by_commit_hash,
    create_algorithm_output,
    get_algorithm_output,
    list_algorithm_outputs,
    get_latest_algorithm_version
)

from .analytics_api import (
    search_task_executions,
    get_version_history,
    get_table_statistics,
    check_data_integrity,
    get_processing_pipeline_summary,
    get_performance_metrics
)

from .evaluation_api import (
    create_evaluation_result,
    get_evaluation_result,
    list_evaluation_results,
    create_evaluation_data,
    list_evaluation_data,
    get_evaluation_overview,
)

from .analysis_api import (
    create_analysis_result,
    get_analysis_result,
    list_analysis_results,
    create_problem,
    get_problem,
    list_problems,
    create_analysis_data,
    list_analysis_data,
)

# 検証モジュール
from .validation import (
    validate_database_schema,
    get_schema_validation_report,
    check_database_compatibility,
    SchemaValidator
)

# CLIモジュール（オプション）
try:
    from . import cli
except ImportError:
    cli = None

__version__ = "0.1.0"
__all__ = [
    # 接続管理
    "DWHConnection",
    "get_connection",
    
    # 例外クラス
    "DWHError",
    "DWHConstraintError", 
    "DWHNotFoundError",
    "DWHValidationError",
    "DWHConnectionError",
    "DWHUniqueConstraintError",
    
    # タスク管理
    "create_task",
    "get_task",
    "list_tasks",
    "update_task",
    "delete_task",
    
    # 被験者管理
    "create_subject",
    "get_subject",
    "list_subjects",
    "update_subject",
    "delete_subject",
    "find_subject_by_name",
    
    # ビデオ管理
    "create_video",
    "get_video",
    "list_videos",
    "get_videos_by_subject",
    "update_video",
    "delete_video",
    
    # タグ管理
    "create_tag",
    "get_tag",
    "get_video_tags",
    "get_task_tags",
    "list_tags",
    "update_tag",
    "delete_tag",
    "get_tag_duration",
    
    # コアライブラリ管理
    "create_core_lib_version",
    "get_core_lib_version",
    "list_core_lib_versions",
    "get_core_lib_version_history",
    "find_core_lib_by_version",
    "find_core_lib_by_commit_hash",
    "create_core_lib_output",
    "get_core_lib_output",
    "list_core_lib_outputs",
    
    # アルゴリズム管理
    "create_algorithm_version",
    "get_algorithm_version",
    "list_algorithm_versions",
    "get_algorithm_version_history",
    "find_algorithm_by_version",
    "find_algorithm_by_commit_hash",
    "create_algorithm_output",
    "get_algorithm_output",
    "list_algorithm_outputs",
    "get_latest_algorithm_version",
    
    # 検索・分析
    "search_task_executions",
    "get_version_history",
    "get_table_statistics",
    "check_data_integrity",
    "get_processing_pipeline_summary",
    "get_performance_metrics",

    # 評価管理
    "create_evaluation_result",
    "get_evaluation_result",
    "list_evaluation_results",
    "create_evaluation_data",
    "list_evaluation_data",
    "get_evaluation_overview",

    # 課題分析管理
    "create_analysis_result",
    "get_analysis_result",
    "list_analysis_results",
    "create_problem",
    "get_problem",
    "list_problems",
    "create_analysis_data",
    "list_analysis_data",

    # スキーマ検証
    "validate_database_schema",
    "get_schema_validation_report",
    "check_database_compatibility",
    "SchemaValidator",
]


