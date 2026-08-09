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

        for _ in range(200):
            app._更新(0.05)
            if app.sort_runner.done:
                break

        assert app.sort_runner.done
        assert app._現在の操作回数() > 0
        assert app._現在の完了時間() is not None
    finally:
        pygame.quit()

