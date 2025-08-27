"""
E2Eテスト: 課題分析テーブルと関連APIの動作確認

前提:
- database.db が存在し、schema と既存テーブルが作成済み
- 追加テーブル: analysis_result_table, problem_table, analysis_data_table

テスト内容:
1) 最小限の前提データを作成（subject → video → core_lib → algorithm → eval → analysis）
2) 取得系APIで作成データが参照できることを確認
3) 例外が発生しないことを確認
"""

from datetime import datetime
import datawarehouse as dwh


def _gen_commit_hash(prefix_digit: str) -> str:
    """40桁の[a-f0-9]で構成されるダミーコミットハッシュを生成（時刻ベース）。"""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")  # 14桁（0-9）
    base = (ts + (prefix_digit * 40))[:40]
    # 念のため、a-f の文字も混ぜる（検証パターン対応）。
    return (base[:-1] + "a")[:40]


def main() -> None:
    # 1) 前提データの作成
    subject_id = dwh.create_subject("E2E_Subject_Test")
    video_id = dwh.create_video(
        video_dir="01_mov_data/video001/WIN_20250819_10_10_42_Pro.mp4",
        subject_id=subject_id,
        video_date="2025-08-19",
        video_length=120,
    )

    # コアライブラリとアルゴリズムのバージョン（コミットハッシュは一意）
    core_hash = _gen_commit_hash("1")
    algo_hash = _gen_commit_hash("2")

    core_lib_id = dwh.create_core_lib_version(
        version="1.0.0-e2e",
        update_info="E2E test core lib",
        commit_hash=core_hash,
        base_version_id=None,
    )

    core_output_id = dwh.create_core_lib_output(
        core_lib_id=core_lib_id,
        video_id=video_id,
        output_dir="02_core_lib_output/v1.0.0/e2e",
    )

    algorithm_id = dwh.create_algorithm_version(
        version="0.1.0-e2e",
        update_info="E2E test algorithm",
        commit_hash=algo_hash,
        base_version_id=None,
    )

    algo_output_id = dwh.create_algorithm_output(
        algorithm_id=algorithm_id,
        core_lib_output_id=core_output_id,
        output_dir="03_algorithm_output/v0.1.0/e2e",
    )

    # 評価結果と評価データ
    eval_result_id = dwh.create_evaluation_result(
        version="v0.0.1-e2e",
        algorithm_id=algorithm_id,
        true_positive=0.9,
        false_positive=0.1,
        evaluation_result_dir="04_evaluation_output/e2e",
        evaluation_timestamp="2025-08-27 12:00:00",
    )

    eval_data_id = dwh.create_evaluation_data(
        evaluation_result_id=eval_result_id,
        algorithm_output_id=algo_output_id,
        correct_task_num=9,
        total_task_num=10,
        evaluation_data_path="04_evaluation_output/e2e/1.csv",
    )

    # 2) 課題分析: 分析結果、課題、分析データ
    analysis_result_id = dwh.create_analysis_result(
        analysis_result_dir="05_analysis_output/e2e",
        evaluation_result_id=eval_result_id,
        analysis_timestamp="2025-08-27 12:05:00",
    )

    problem_id = dwh.create_problem(
        problem_name="遅延検知",
        problem_description="開始検知が平均で+5フレーム遅延",
        problem_status="open",
        analysis_result_id=analysis_result_id,
    )

    # isproblem = 0（課題なし）：problem_IDはNULL
    ad_id_1 = dwh.create_analysis_data(
        evaluation_data_id=eval_data_id,
        analysis_result_id=analysis_result_id,
        analysis_data_isproblem=0,
        analysis_data_dir="05_analysis_output/e2e/ed1",
        analysis_data_description="特記事項なし",
        problem_id=None,
    )

    # isproblem = 1（課題あり）：problem_IDが必須
    ad_id_2 = dwh.create_analysis_data(
        evaluation_data_id=eval_data_id,
        analysis_result_id=analysis_result_id,
        analysis_data_isproblem=1,
        analysis_data_dir="05_analysis_output/e2e/ed2",
        analysis_data_description="開始遅延検知",
        problem_id=problem_id,
    )

    # 3) 取得系で確認
    results = dwh.list_analysis_results(evaluation_result_id=eval_result_id)
    problems = dwh.list_problems(analysis_result_id=analysis_result_id)
    analysis_data = dwh.list_analysis_data(analysis_result_id=analysis_result_id)

    overview = dwh.get_evaluation_overview(eval_result_id)

    print("E2E Test Completed")
    print({
        "subject_id": subject_id,
        "video_id": video_id,
        "core_lib_id": core_lib_id,
        "algorithm_id": algorithm_id,
        "eval_result_id": eval_result_id,
        "analysis_result_id": analysis_result_id,
        "counts": {
            "analysis_results": len(results),
            "problems": len(problems),
            "analysis_data": len(analysis_data),
        },
        "overview": overview,
        "analysis_data_ids": [ad_id_1, ad_id_2],
    })


if __name__ == "__main__":
    main()


