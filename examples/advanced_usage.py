#!/usr/bin/env python3
"""
DataWareHouse API 高度な使用例

このスクリプトは、バージョン履歴、検索機能、分析機能などの
高度なAPIの使用方法を示します。

事前準備:
    pip install datawarehouse

実行例:
    python advanced_usage.py
"""

import datawarehouse as dwh


def setup_sample_data():
    """サンプルデータをセットアップ"""
    print("サンプルデータをセットアップ中...")
    
    # 被験者登録
    subject_a_id = dwh.create_subject("Subject A")
    subject_b_id = dwh.create_subject("Subject B")
    
    # タスク登録
    task1_id = dwh.create_task(1, "正検知評価", "ビデオ内の正検知を評価")
    task2_id = dwh.create_task(1, "誤検知評価", "ビデオ内の誤検知を評価")
    
    # ビデオ登録
    video_a1_id = dwh.create_video("01_mov_data/subject_a_task1.mp4", subject_a_id, "2025-08-19", 120)
    video_a2_id = dwh.create_video("01_mov_data/subject_a_task2.mp4", subject_a_id, "2025-08-19", 150)
    video_b1_id = dwh.create_video("01_mov_data/subject_b_task1.mp4", subject_b_id, "2025-08-20", 110)
    
    # タグ登録
    dwh.create_tag(video_a1_id, task1_id, 0, 30)
    dwh.create_tag(video_a1_id, task1_id, 60, 90)
    dwh.create_tag(video_a2_id, task2_id, 10, 40)
    dwh.create_tag(video_b1_id, task1_id, 5, 35)
    
    # コアライブラリのバージョン履歴
    core_v1_id = dwh.create_core_lib_version(
        "1.0.0", "初期バージョン", "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    )
    core_v11_id = dwh.create_core_lib_version(
        "1.1.0", "バグ修正", "b2c3d4e5f6b2c3d4e5f6b2c3d4e5f6b2c3d4e5f6b2c3", core_v1_id
    )
    core_v12_id = dwh.create_core_lib_version(
        "1.2.0", "新機能追加", "c3d4e5f6c3d4e5f6c3d4e5f6c3d4e5f6c3d4e5f6c3d4", core_v11_id
    )
    
    # アルゴリズムのバージョン履歴
    algo_v2_id = dwh.create_algorithm_version(
        "2.0.0", "初期バージョン", "f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    )
    algo_v21_id = dwh.create_algorithm_version(
        "2.1.0", "精度向上", "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4", algo_v2_id
    )
    
    # 出力データ
    output1_id = dwh.create_core_lib_output(core_v12_id, video_a1_id, "02_core_lib_output/v1.2.0_subject_a_task1")
    output2_id = dwh.create_core_lib_output(core_v12_id, video_a2_id, "02_core_lib_output/v1.2.0_subject_a_task2")
    
    dwh.create_algorithm_output(algo_v21_id, output1_id, "03_algorithm_output/v2.1.0_core_v1.2.0_subject_a_task1")
    dwh.create_algorithm_output(algo_v21_id, output2_id, "03_algorithm_output/v2.1.0_core_v1.2.0_subject_a_task2")
    
    print("サンプルデータのセットアップが完了しました\n")
    
    return {
        "subjects": [subject_a_id, subject_b_id],
        "tasks": [task1_id, task2_id],
        "videos": [video_a1_id, video_a2_id, video_b1_id],
        "core_libs": [core_v1_id, core_v11_id, core_v12_id],
        "algorithms": [algo_v2_id, algo_v21_id]
    }


def demo_version_history(data):
    """バージョン履歴のデモ"""
    print("=== バージョン履歴の確認 ===")
    
    # コアライブラリのバージョン履歴
    print("コアライブラリのバージョン履歴:")
    core_history = dwh.get_core_lib_version_history(data["core_libs"][-1])  # 最新バージョン
    for version in core_history:
        print(f"  v{version['core_lib_version']}: {version['core_lib_update_information']}")
    
    # アルゴリズムのバージョン履歴
    print("\nアルゴリズムのバージョン履歴:")
    algo_history = dwh.get_algorithm_version_history(data["algorithms"][-1])  # 最新バージョン
    for version in algo_history:
        print(f"  v{version['algorithm_version']}: {version['algorithm_update_information']}")
    
    print()


def demo_search_functionality():
    """検索機能のデモ"""
    print("=== 検索機能のデモ ===")
    
    # タスク実行状況の検索
    print("1. タスク実行状況の検索")
    
    # 特定のタスクセットで検索
    executions = dwh.search_task_executions(task_set=1)
    print(f"タスクセット1の実行状況: {len(executions)}件")
    for ex in executions:
        print(f"  {ex['subject_name']} - {ex['task_name']} ({ex['start']}-{ex['end']}フレーム)")
    
    # 日付範囲で検索
    executions_date = dwh.search_task_executions(date_from="2025-08-19", date_to="2025-08-19")
    print(f"\n2025-08-19の実行状況: {len(executions_date)}件")
    
    # バージョン情報で検索
    print("\n2. バージョン情報で検索")
    core_lib = dwh.find_core_lib_by_version("1.2.0")
    if core_lib:
        print(f"コアライブラリ v1.2.0: {core_lib}")
    
    algorithm = dwh.find_algorithm_by_version("2.1.0")
    if algorithm:
        print(f"アルゴリズム v2.1.0: {algorithm}")
    
    print()


def demo_analytics():
    """分析機能のデモ"""
    print("=== 分析機能のデモ ===")
    
    # テーブル統計
    print("1. テーブル統計")
    stats = dwh.get_table_statistics()
    for table, count in stats.items():
        print(f"  {table}: {count}件")
    
    # パフォーマンスメトリクス
    print("\n2. パフォーマンスメトリクス")
    metrics = dwh.get_performance_metrics()
    print(f"  総ビデオ数: {metrics['total_videos']}")
    print(f"  総タグ数: {metrics['total_tags']}")
    print(f"  ビデオあたり平均タグ数: {metrics['avg_tags_per_video']:.2f}")
    print(f"  コアライブラリバージョン数: {metrics['core_lib_versions']}")
    print(f"  アルゴリズムバージョン数: {metrics['algorithm_versions']}")
    
    # 処理パイプライン概要
    print("\n3. 処理パイプライン概要")
    pipeline = dwh.get_processing_pipeline_summary()
    for item in pipeline:
        print(f"  {item['video_dir']} -> Core v{item['core_lib_version']} -> Algo v{item['algorithm_version']}")
    
    # データ整合性チェック
    print("\n4. データ整合性チェック")
    integrity = dwh.check_data_integrity()
    print(f"  外部キー制約違反: {len(integrity['foreign_key_check'])}件")
    print(f"  フレーム区間違反: {len(integrity['frame_validation'])}件")
    print(f"  孤立レコード:")
    for orphan_type, count in integrity['orphaned_records'].items():
        print(f"    {orphan_type}: {count}件")
    
    print()


def demo_connection_management():
    """接続管理のデモ"""
    print("=== 接続管理のデモ ===")
    
    # コンテキストマネージャーを使用した高度な操作
    print("コンテキストマネージャーを使用したバッチ処理:")
    
    with dwh.get_connection() as conn:
        cursor = conn.cursor()
        
        # 複数のビデオのタグ数を一括取得
        cursor.execute("""
            SELECT v.video_dir, COUNT(t.tag_ID) as tag_count
            FROM video_table v
            LEFT JOIN tag_table t ON v.video_ID = t.video_ID
            GROUP BY v.video_ID, v.video_dir
            ORDER BY tag_count DESC
        """)
        
        results = cursor.fetchall()
        print("ビデオ別タグ数:")
        for row in results:
            print(f"  {row[0]}: {row[1]}タグ")
    
    print()


def demo_schema_validation():
    """スキーマ検証のデモ"""
    print("=== スキーマ検証のデモ ===")

    # スキーマ検証レポート取得
    print("1. スキーマ検証レポート")
    report = dwh.get_schema_validation_report("database.db")
    print("レポートの最初の200文字:")
    print(report[:200] + "...")

    # 詳細な検証結果取得
    print("\n2. 詳細な検証結果")
    validation_result = dwh.validate_database_schema("database.db")
    print(f"有効なスキーマ: {validation_result['is_valid']}")
    print(f"重大問題数: {len(validation_result['issues'])}")
    print(f"警告数: {len(validation_result['warnings'])}")
    print(f"検出テーブル数: {len(validation_result['tables_found'])}")

    # 互換性チェック
    print("\n3. 互換性チェック")
    is_compatible = dwh.check_database_compatibility("database.db")
    print(f"互換性: {'✅ 有' if is_compatible else '❌ 無'}")

    print()


def main():
    """高度な使用例のデモ"""
    print("=== DataWareHouse API 高度な使用例 ===\n")
    
    try:
        # サンプルデータのセットアップ
        data = setup_sample_data()
        
        # バージョン履歴のデモ
        demo_version_history(data)
        
        # 検索機能のデモ
        demo_search_functionality()
        
        # 分析機能のデモ
        demo_analytics()
        
        # 接続管理のデモ
        demo_connection_management()

        # スキーマ検証のデモ
        demo_schema_validation()

        print("=== 高度な使用例が正常に完了しました ===")
        
    except dwh.DWHError as e:
        print(f"DataWareHouseエラー: {e}")
        print(f"エラーコード: {e.error_code}")
        if hasattr(e, 'table_name') and e.table_name:
            print(f"テーブル: {e.table_name}")
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
