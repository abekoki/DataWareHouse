#!/usr/bin/env python3
"""
DataWareHouse API 基本使用例

このスクリプトは、DataWareHouse APIライブラリの基本的な使用方法を示します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import datawarehouse as dwh


def main():
    """基本的な使用例のデモ"""
    
    print("=== DataWareHouse API 基本使用例 ===\n")
    
    try:
        # 1. 被験者の登録
        print("1. 被験者を登録")
        subject_id = dwh.create_subject("Subject A")
        print(f"被験者ID: {subject_id}")
        
        # 2. タスクの登録
        print("\n2. タスクを登録")
        task_id = dwh.create_task(1, "正検知評価", "ビデオ内の正検知を評価するタスク")
        print(f"タスクID: {task_id}")
        
        # 3. ビデオの登録
        print("\n3. ビデオを登録")
        video_id = dwh.create_video(
            video_dir="01_mov_data/subject_a_task1.mp4",
            subject_id=subject_id,
            video_date="2025-08-19",
            video_length=120
        )
        print(f"ビデオID: {video_id}")
        
        # 4. タグの登録
        print("\n4. タグを登録")
        tag_id = dwh.create_tag(
            video_id=video_id,
            task_id=task_id,
            start=0,
            end=30
        )
        print(f"タグID: {tag_id}")
        
        # 5. コアライブラリバージョンの登録
        print("\n5. コアライブラリバージョンを登録")
        core_lib_id = dwh.create_core_lib_version(
            version="1.0.0",
            update_info="初期バージョン",
            commit_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        )
        print(f"コアライブラリID: {core_lib_id}")
        
        # 6. コアライブラリ出力の登録
        print("\n6. コアライブラリ出力を登録")
        core_output_id = dwh.create_core_lib_output(
            core_lib_id=core_lib_id,
            video_id=video_id,
            output_dir="02_core_lib_output/v1.0.0_subject_a_task1"
        )
        print(f"コアライブラリ出力ID: {core_output_id}")
        
        # 7. アルゴリズムバージョンの登録
        print("\n7. アルゴリズムバージョンを登録")
        algorithm_id = dwh.create_algorithm_version(
            version="2.0.0",
            update_info="初期バージョン",
            commit_hash="f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        )
        print(f"アルゴリズムID: {algorithm_id}")
        
        # 8. アルゴリズム出力の登録
        print("\n8. アルゴリズム出力を登録")
        algo_output_id = dwh.create_algorithm_output(
            algorithm_id=algorithm_id,
            core_lib_output_id=core_output_id,
            output_dir="03_algorithm_output/v2.0.0_core_v1.0.0_subject_a_task1"
        )
        print(f"アルゴリズム出力ID: {algo_output_id}")
        
        # 9. データの取得・確認
        print("\n=== データの取得・確認 ===")
        
        # 被験者情報
        subject = dwh.get_subject(subject_id)
        print(f"被験者: {subject}")
        
        # ビデオのタグ一覧
        video_tags = dwh.get_video_tags(video_id)
        print(f"ビデオのタグ: {video_tags}")
        
        # 統計情報
        stats = dwh.get_table_statistics()
        print(f"テーブル統計: {stats}")
        
        # データ整合性チェック
        integrity = dwh.check_data_integrity()
        print(f"整合性チェック結果: {integrity}")
        
        print("\n=== 基本使用例が正常に完了しました ===")
        
    except dwh.DWHError as e:
        print(f"DataWareHouseエラー: {e}")
        print(f"エラーコード: {e.error_code}")
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
