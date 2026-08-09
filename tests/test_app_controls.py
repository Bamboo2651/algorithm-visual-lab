"""アプリの開始待ちと完了時間の記録を確認する。"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from app import 可視化アプリ


def test_algorithm_does_not_run_before_start() -> None:
    app = 可視化アプリ()

    try:
        app.mode = "sort"
        app.view_mode = "compare"
        app._現在をリセット()

        before = [runner.state.values.copy() for runner in app.sort_compare_runners]
        app._更新(1.0)
        after = [runner.state.values for runner in app.sort_compare_runners]

        assert before == after
        assert app.elapsed == 0
        assert app._現在の操作回数() == 0
    finally:
        pygame.quit()

def test_completion_time_is_recorded_after_start() -> None:
    app = 可視化アプリ()

    try:
        app.mode = "sort"
        app.view_mode = "single"
        app.sort_index = 8  # 計数ソート
        app._現在をリセット()
        app._スタート()
        app.elapsed = 1_000.0

        for _ in range(200):
            app._更新(0.05)
            if app.sort_runner.done:
                break

        assert app.sort_runner.done
        assert app._現在の操作回数() > 0
        assert app._現在の完了時間() is not None
        assert app._現在の完了時間() < 1.0
    finally:
        pygame.quit()


def test_data_size_is_applied_to_each_category() -> None:
    app = 可視化アプリ()

    try:
        app.data_slider.value = 25

        app.mode = "sort"
        app._現在をリセット()
        assert len(app.sort_runner.state.values) == 25

        app.mode = "prime"
        app._現在をリセット()
        assert app.prime_runner.state.limit == 25

        app.mode = "sequence"
        app._現在をリセット()
        app._スタート()

        for _ in range(100):
            app._1ステップ進める()
            if app._完了している():
                break

        assert app._完了している()
        assert app.sequence_runner.state.operations == 25
    finally:
        pygame.quit()


def test_display_speed_does_not_change_benchmark_result() -> None:
    app = 可視化アプリ()

    try:
        app.mode = "sort"
        app.view_mode = "single"
        app.sort_index = 0  # バブルソート
        app.data_slider.value = 10
        app.speed_slider.value = 1
        app._現在をリセット()
        first_values = app.sort_values.copy()
        app._スタート()
        first_time = app.processing_times["bubble"]
        first_operations = app.benchmark_operations["bubble"]

        for _ in range(1_000):
            app._更新(1.0)
            if app._完了している():
                break

        assert app._現在の完了時間() == first_time

        app.speed_slider.value = 500
        app._現在をリセット()
        assert app.sort_values == first_values
        app._スタート()

        for _ in range(10):
            app._更新(1.0)
            if app._完了している():
                break

        assert app._現在の完了時間() == first_time
        assert app.benchmark_operations["bubble"] == first_operations
    finally:
        pygame.quit()
