"""Algorithm Visual LabのPygameアプリ。

このファイルは画面表示と操作だけを担当する。
アルゴリズム本体は algorithms/ 以下に分離している。
"""

from __future__ import annotations

import math
import random
import statistics
import time

import pygame

from algorithms.primes import ALL_ALGORITHMS as PRIME_ALGORITHMS
from algorithms.primes.common import PrimeRunner
from algorithms.sequences import ALL_ALGORITHMS as SEQUENCE_ALGORITHMS
from algorithms.sequences.common import SequenceRunner
from algorithms.sorting import ALL_ALGORITHMS as SORT_ALGORITHMS
from algorithms.sorting.common import SortRunner


幅 = 1440
高さ = 900
毎秒フレーム数 = 60

背景色 = (6, 10, 20)
パネル色 = (24, 33, 54)
選択色 = (38, 63, 91)
枠色 = (93, 115, 155)
文字色 = (238, 244, 255)
補助文字色 = (200, 211, 231)
水色 = (69, 220, 255)
紫色 = (180, 105, 255)
緑色 = (88, 230, 158)
黄色 = (255, 215, 90)
赤色 = (255, 105, 125)


def 日本語フォント(size: int, bold: bool = False) -> pygame.font.Font:
    """Windowsで利用できる日本語フォントを優先して取得する。"""

    path = pygame.font.match_font("Yu Gothic UI,Meiryo,MS Gothic", bold=bold)
    return pygame.font.Font(path, size)


def 文字を描く(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    position: tuple[int, int],
    center: bool = False,
) -> None:
    image = font.render(text, True, color)
    rect = image.get_rect()
    rect.center = position if center else rect.center

    if not center:
        rect.topleft = position

    screen.blit(image, rect)


class ボタン:
    """マウスで押せる共通ボタン。"""

    def __init__(self, rect: pygame.Rect, label: str) -> None:
        self.rect = rect
        self.label = label

    def 押された(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def 描く(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = 選択色 if hovered else パネル色
        pygame.draw.rect(screen, color, self.rect, border_radius=9)
        pygame.draw.rect(screen, 枠色, self.rect, 1, border_radius=9)
        文字を描く(screen, font, self.label, 文字色, self.rect.center, True)


class 数値スライダー:
    """指定範囲の整数をマウスで変更する共通スライダー。"""

    def __init__(
        self,
        rect: pygame.Rect,
        minimum: int,
        maximum: int,
        value: int,
        label: str,
        unit: str,
        color: tuple[int, int, int],
    ) -> None:
        self.rect = rect
        self.minimum = minimum
        self.maximum = maximum
        self.value = value
        self.label = label
        self.unit = unit
        self.color = color
        self.dragging = False

    @property
    def handle_x(self) -> int:
        ratio = (self.value - self.minimum) / (self.maximum - self.minimum)
        return round(self.rect.left + self.rect.width * ratio)

    def イベント処理(self, event: pygame.event.Event) -> bool:
        """値の確定時にTrueを返す。"""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(24, 28).collidepoint(event.pos):
                self.dragging = True
                self._座標から値を設定(event.pos[0])
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._座標から値を設定(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.dragging
            self.dragging = False
            return was_dragging

        return False

    def _座標から値を設定(self, x: int) -> None:
        x = max(self.rect.left, min(x, self.rect.right))
        ratio = (x - self.rect.left) / self.rect.width
        self.value = round(self.minimum + ratio * (self.maximum - self.minimum))

    def 描く(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, 枠色, self.rect, border_radius=4)
        active = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.handle_x - self.rect.left,
            self.rect.height,
        )
        pygame.draw.rect(screen, self.color, active, border_radius=4)
        pygame.draw.circle(screen, 文字色, (self.handle_x, self.rect.centery), 9)
        文字を描く(
            screen,
            font,
            f"{self.label}: {self.value} {self.unit}",
            文字色,
            (self.rect.left, self.rect.top - 26),
        )


class 可視化アプリ:
    """画面、入力、選択中のアルゴリズムをまとめて管理する。"""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((幅, 高さ))
        pygame.display.set_caption("アルゴリズム可視化ラボ")
        self.clock = pygame.time.Clock()

        self.title_font = 日本語フォント(36, True)
        self.heading_font = 日本語フォント(24, True)
        self.normal_font = 日本語フォント(19, True)
        self.small_font = 日本語フォント(16, True)

        self.running = True
        self.mode = "menu"
        self.view_mode = "single"
        self.started = False
        self.paused = False
        self.elapsed = 0.0
        self.accumulator = 0.0
        self.completion_times: dict[str, float] = {}
        self.processing_times: dict[str, float] = {}
        self.benchmark_operations: dict[str, int] = {}
        self.benchmark_cache: dict[tuple[str, str, int], tuple[float, int]] = {}

        self.data_slider = 数値スライダー(
            pygame.Rect(700, 862, 270, 8),
            minimum=10,
            maximum=300,
            value=50,
            label="データ量",
            unit="件",
            color=紫色,
        )
        self.speed_slider = 数値スライダー(
            pygame.Rect(1040, 862, 340, 8),
            minimum=1,
            maximum=500,
            value=50,
            label="表示速度",
            unit="ステップ/秒",
            color=水色,
        )

        self.sort_index = 0
        self.prime_index = 0
        self.sequence_index = 0
        self.sort_values: list[int] = []

        self.sort_runner: SortRunner
        self.prime_runner: PrimeRunner
        self.sequence_runner: SequenceRunner
        self.sort_compare_runners: list[SortRunner] = []
        self.prime_compare_runners: list[PrimeRunner] = []
        self.sequence_compare_runners: list[SequenceRunner] = []
        self._reset_sort()
        self._reset_prime()
        self._reset_sequence()

        self.home_button = ボタン(pygame.Rect(22, 842, 110, 42), "ホーム")
        self.start_button = ボタン(pygame.Rect(146, 842, 115, 42), "スタート")
        self.pause_button = ボタン(pygame.Rect(275, 842, 125, 42), "一時停止")
        self.step_button = ボタン(pygame.Rect(414, 842, 115, 42), "1ステップ")
        self.reset_button = ボタン(pygame.Rect(543, 842, 115, 42), "リセット")

    def 実行(self) -> None:
        while self.running:
            delta_time = self.clock.tick(毎秒フレーム数) / 1000
            self._イベント処理()
            self._更新(delta_time)
            self._描画()

        pygame.quit()

    def _イベント処理(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._キー操作(event.key)

            if self.mode == "menu":
                self._メニュー操作(event)
            else:
                self._共通操作(event)
                self._一覧操作(event)
                if self.data_slider.イベント処理(event):
                    self._現在をリセット()
                self.speed_slider.イベント処理(event)

    def _キー操作(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.mode = "menu"
        elif key == pygame.K_SPACE and self.mode != "menu":
            if not self.started:
                self._スタート()
            else:
                self.paused = not self.paused
        elif key == pygame.K_RIGHT and self.mode != "menu":
            self._手動で1ステップ進める()
        elif key == pygame.K_r and self.mode != "menu":
            self._現在をリセット()
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self._モードを開く({pygame.K_1: "sort", pygame.K_2: "prime", pygame.K_3: "sequence"}[key])

    def _メニュー操作(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        for mode, rect in self._メニューカード().items():
            if rect.collidepoint(event.pos):
                self._モードを開く(mode)

    def _共通操作(self, event: pygame.event.Event) -> None:
        if self.home_button.押された(event):
            self.mode = "menu"
        elif self.start_button.押された(event):
            self._スタート()
        elif self.pause_button.押された(event):
            if self.started:
                self.paused = not self.paused
        elif self.step_button.押された(event):
            self._手動で1ステップ進める()
        elif self.reset_button.押された(event):
            self._現在をリセット()

    def _一覧操作(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        for view_mode, rect in self._表示切替ボタン().items():
            if rect.collidepoint(event.pos):
                self.view_mode = view_mode
                self._現在をリセット()
                return

        names = self._現在の名前一覧()

        for index in range(len(names)):
            rect = pygame.Rect(24, 246 + index * 52, 276, 42)
            if rect.collidepoint(event.pos):
                self.view_mode = "single"
                if self.mode == "sort":
                    self.sort_index = index
                    self._reset_sort(keep_values=True)
                elif self.mode == "prime":
                    self.prime_index = index
                    self._reset_prime()
                else:
                    self.sequence_index = index
                    self._reset_sequence()
                self._時間をリセット()

    def _モードを開く(self, mode: str) -> None:
        self.mode = mode
        self._現在をリセット()

    def _時間をリセット(self) -> None:
        self.elapsed = 0.0
        self.accumulator = 0.0
        self.started = False
        self.paused = False
        self.completion_times = {}
        self.processing_times = {}
        self.benchmark_operations = {}

    def _スタート(self) -> None:
        """固定条件のベンチマーク後、アニメーションを開始する。"""

        if self._完了している():
            return

        self._ベンチマークを準備する()
        self.started = True
        self.paused = False

    def _手動で1ステップ進める(self) -> None:
        """自動実行せず、利用者の操作で1ステップだけ進める。"""

        if self._完了している():
            return

        if not self.started:
            self._ベンチマークを準備する()
        self.started = True
        self.paused = True
        self._1ステップ進める()

    def _現在をリセット(self) -> None:
        self._時間をリセット()
        if self.mode == "sort":
            self._reset_sort()
        elif self.mode == "prime":
            self._reset_prime()
        elif self.mode == "sequence":
            self._reset_sequence()

    def _reset_sort(self, keep_values: bool = False) -> None:
        if (
            not keep_values
            or not self.sort_values
            or len(self.sort_values) != self.data_slider.value
        ):
            self.sort_values = list(range(1, self.data_slider.value + 1))
            # 同じデータ量なら、リセット後も必ず同じ並びを再現する。
            random.Random(self.data_slider.value).shuffle(self.sort_values)
        self.sort_runner = SortRunner(SORT_ALGORITHMS[self.sort_index], self.sort_values)
        self.sort_compare_runners = [
            SortRunner(algorithm, self.sort_values)
            for algorithm in SORT_ALGORITHMS
        ]

    def _reset_prime(self) -> None:
        self.prime_runner = PrimeRunner(
            PRIME_ALGORITHMS[self.prime_index],
            limit=self.data_slider.value,
        )
        self.prime_compare_runners = [
            PrimeRunner(algorithm, limit=self.data_slider.value)
            for algorithm in PRIME_ALGORITHMS
        ]

    def _reset_sequence(self) -> None:
        self.sequence_runner = SequenceRunner(SEQUENCE_ALGORITHMS[self.sequence_index])
        self.sequence_compare_runners = [
            SequenceRunner(algorithm)
            for algorithm in SEQUENCE_ALGORITHMS
        ]

    def _更新(self, delta_time: float) -> None:
        if self.mode == "menu" or not self.started or self.paused or self._完了している():
            return

        self.elapsed += delta_time
        self.accumulator += delta_time * self.speed_slider.value
        steps = min(int(self.accumulator), 1000)
        self.accumulator -= steps

        for _ in range(steps):
            self._1ステップ進める()

    def _1ステップ進める(self) -> None:
        if self.view_mode == "compare":
            for runner in self._比較ランナー一覧():
                self._ランナーを進める(runner)
            return

        if self.mode == "sort":
            self._ランナーを進める(self.sort_runner)
        elif self.mode == "prime":
            self._ランナーを進める(self.prime_runner)
        elif self.mode == "sequence":
            self._ランナーを進める(self.sequence_runner)

    def _ランナーを進める(
        self,
        runner: SortRunner | PrimeRunner | SequenceRunner,
    ) -> None:
        """計測済みの結果を変えず、可視化だけを1ステップ進める。"""

        if self._ランナー完了(runner):
            return

        key = self._ランナーキー(runner)
        runner.step()

        if self._ランナー完了(runner):
            self.completion_times.setdefault(key, self.processing_times.get(key, 0.0))

    def _ベンチマークを準備する(self) -> None:
        """描画なしで測定し、表示速度に依存しない結果を固定する。"""

        runners = (
            self._比較ランナー一覧()
            if self.view_mode == "compare"
            else [self._現在のランナー()]
        )

        for runner in runners:
            if runner is None:
                continue

            key = self._ランナーキー(runner)
            cache_key = (self.mode, key, self.data_slider.value)

            if cache_key not in self.benchmark_cache:
                # 最初の1回はPythonやCPUのウォームアップとして結果から除外する。
                self._ベンチマークを1回実行(runner)
                samples = [
                    self._ベンチマークを1回実行(runner)
                    for _ in range(5)
                ]
                durations = [duration for duration, _ in samples]
                operations = samples[0][1]
                self.benchmark_cache[cache_key] = (
                    statistics.median(durations),
                    operations,
                )

            duration, operations = self.benchmark_cache[cache_key]
            self.processing_times[key] = duration
            self.benchmark_operations[key] = operations

    def _ベンチマークを1回実行(
        self,
        source: SortRunner | PrimeRunner | SequenceRunner,
    ) -> tuple[float, int]:
        """新しいランナーを描画せず最後まで実行する。"""

        runner = self._新しいベンチマークランナー(source)
        started_at = time.perf_counter()

        while not self._ランナー完了(runner):
            runner.step()

        duration = time.perf_counter() - started_at
        return duration, self._ランナー操作回数(runner)

    def _新しいベンチマークランナー(
        self,
        source: SortRunner | PrimeRunner | SequenceRunner,
    ) -> SortRunner | PrimeRunner | SequenceRunner:
        """画面表示用と同じ条件の、計測専用ランナーを作る。"""

        if isinstance(source, SortRunner):
            return SortRunner(source.algorithm, self.sort_values)
        if isinstance(source, PrimeRunner):
            return PrimeRunner(source.algorithm, limit=self.data_slider.value)
        return SequenceRunner(source.algorithm)

    def _現在のランナー(self) -> SortRunner | PrimeRunner | SequenceRunner | None:
        return {
            "sort": self.sort_runner,
            "prime": self.prime_runner,
            "sequence": self.sequence_runner,
        }.get(self.mode)

    def _完了している(self) -> bool:
        if self.view_mode == "compare":
            return all(self._ランナー完了(runner) for runner in self._比較ランナー一覧())

        if self.mode == "sort":
            return self._ランナー完了(self.sort_runner)
        if self.mode == "prime":
            return self._ランナー完了(self.prime_runner)
        if self.mode == "sequence":
            return self._ランナー完了(self.sequence_runner)
        return False

    def _現在の操作回数(self) -> int:
        if self.view_mode == "compare":
            return sum(self._表示用操作回数(runner) for runner in self._比較ランナー一覧())

        if self.mode == "sort":
            return self._表示用操作回数(self.sort_runner)
        if self.mode == "prime":
            return self._表示用操作回数(self.prime_runner)
        if self.mode == "sequence":
            return self._表示用操作回数(self.sequence_runner)
        return 0

    def _比較ランナー一覧(self) -> list[SortRunner | PrimeRunner | SequenceRunner]:
        """現在のカテゴリで比較中の全ランナーを返す。"""

        if self.mode == "sort":
            return self.sort_compare_runners
        if self.mode == "prime":
            return self.prime_compare_runners
        if self.mode == "sequence":
            return self.sequence_compare_runners
        return []

    def _ランナー操作回数(self, runner: SortRunner | PrimeRunner | SequenceRunner) -> int:
        if isinstance(runner, SortRunner):
            return runner.operations
        return runner.state.operations

    def _表示用操作回数(self, runner: SortRunner | PrimeRunner | SequenceRunner) -> int:
        """ベンチマーク済みなら、表示速度に依存しない処理回数を返す。"""

        key = self._ランナーキー(runner)
        return self.benchmark_operations.get(key, 0)

    def _ランナーキー(self, runner: SortRunner | PrimeRunner | SequenceRunner) -> str:
        if isinstance(runner, SortRunner):
            return runner.algorithm.info.key
        return runner.algorithm.key

    def _ランナー完了(self, runner: SortRunner | PrimeRunner | SequenceRunner) -> bool:
        """数列では指定ステップ数への到達も完了として扱う。"""

        if isinstance(runner, SequenceRunner):
            return runner.done or runner.state.operations >= self.data_slider.value
        return runner.done

    def _現在の完了時間(self) -> float | None:
        """個別表示、または全体比較の完了時間を返す。"""

        if self.view_mode == "compare":
            runners = self._比較ランナー一覧()
            if not runners or not all(self._ランナー完了(runner) for runner in runners):
                return None
            times = [
                self.completion_times[self._ランナーキー(runner)]
                for runner in runners
                if self._ランナーキー(runner) in self.completion_times
            ]
            return max(times) if times else None

        runner = {
            "sort": self.sort_runner,
            "prime": self.prime_runner,
            "sequence": self.sequence_runner,
        }.get(self.mode)

        if runner is None or not self._ランナー完了(runner):
            return None
        return self.completion_times.get(self._ランナーキー(runner))

    def _現在の計算時間(self) -> float:
        """描画待ちを除いた、アルゴリズム処理だけの累計時間を返す。"""

        if self.view_mode == "compare":
            return sum(
                self.processing_times.get(self._ランナーキー(runner), 0.0)
                for runner in self._比較ランナー一覧()
            )

        runner = {
            "sort": self.sort_runner,
            "prime": self.prime_runner,
            "sequence": self.sequence_runner,
        }.get(self.mode)
        return self.processing_times.get(self._ランナーキー(runner), 0.0) if runner else 0.0

    @staticmethod
    def _時間を表示(seconds: float | None) -> str:
        """短い計算時間はミリ秒、長い時間は秒で読みやすく表示する。"""

        if seconds is None:
            return "--"
        if seconds < 1:
            return f"{seconds * 1000:.3f} ms"
        return f"{seconds:.3f} 秒"

    def _現在の名前一覧(self) -> list[str]:
        if self.mode == "sort":
            return [algorithm.info.name for algorithm in SORT_ALGORITHMS]
        if self.mode == "prime":
            return [algorithm.name for algorithm in PRIME_ALGORITHMS]
        return [algorithm.name for algorithm in SEQUENCE_ALGORITHMS]

    def _描画(self) -> None:
        self.screen.fill(背景色)
        self._ヘッダーを描く()

        if self.mode == "menu":
            self._メニューを描く()
        else:
            self._一覧を描く()
            self._計測値を描く()

            if self.view_mode == "compare":
                self._比較を描く()
            else:
                if self.mode == "sort":
                    self._ソートを描く()
                elif self.mode == "prime":
                    self._素数を描く()
                else:
                    self._数列を描く()

            self._操作欄を描く()

        pygame.display.flip()

    def _ヘッダーを描く(self) -> None:
        titles = {
            "menu": "好きな可視化を選んでください",
            "sort": "ソートアルゴリズム",
            "prime": "素数探索アルゴリズム",
            "sequence": "数列アルゴリズム",
        }
        文字を描く(self.screen, self.title_font, "アルゴリズム可視化ラボ", 文字色, (24, 14))
        文字を描く(self.screen, self.normal_font, titles[self.mode], 補助文字色, (26, 55))
        pygame.draw.line(self.screen, 枠色, (0, 88), (幅, 88))

    def _メニューカード(self) -> dict[str, pygame.Rect]:
        return {
            "sort": pygame.Rect(55, 190, 400, 390),
            "prime": pygame.Rect(520, 190, 400, 390),
            "sequence": pygame.Rect(985, 190, 400, 390),
        }

    def _メニューを描く(self) -> None:
        data = {
            "sort": ("1", "ソート", "9種類", 水色, "値が並び替わる過程を見る"),
            "prime": ("2", "素数探索", "2種類", 緑色, "素数を探す方法を比べる"),
            "sequence": ("3", "数列アート", "2種類", 紫色, "数の規則を形として見る"),
        }

        for mode, rect in self._メニューカード().items():
            number, title, count, color, summary = data[mode]
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, 選択色 if hovered else パネル色, rect, border_radius=18)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=18)
            pygame.draw.circle(self.screen, color, (rect.centerx, rect.top + 72), 34, 3)
            文字を描く(self.screen, self.heading_font, number, color, (rect.centerx, rect.top + 72), True)
            文字を描く(self.screen, self.heading_font, title, 文字色, (rect.centerx, rect.top + 145), True)
            文字を描く(self.screen, self.normal_font, count, color, (rect.centerx, rect.top + 184), True)
            文字を描く(self.screen, self.small_font, summary, 補助文字色, (rect.centerx, rect.top + 230), True)
            文字を描く(self.screen, self.normal_font, "クリックして開始", 文字色, (rect.centerx, rect.bottom - 48), True)

    def _一覧を描く(self) -> None:
        names = self._現在の名前一覧()
        selected = {"sort": self.sort_index, "prime": self.prime_index, "sequence": self.sequence_index}[self.mode]
        文字を描く(self.screen, self.heading_font, "表示方法", 文字色, (24, 105))

        for view_mode, rect in self._表示切替ボタン().items():
            is_selected = self.view_mode == view_mode
            color = 選択色 if is_selected else パネル色
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, 水色 if is_selected else 枠色, rect, 2, border_radius=8)
            label = "個別表示" if view_mode == "single" else "全体比較"
            文字を描く(self.screen, self.small_font, label, 文字色, rect.center, True)

        文字を描く(self.screen, self.heading_font, "アルゴリズム一覧", 文字色, (24, 207))

        for index, name in enumerate(names):
            rect = pygame.Rect(24, 246 + index * 52, 276, 42)
            is_selected = self.view_mode == "single" and index == selected
            color = 選択色 if is_selected else パネル色
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, 水色 if is_selected else 枠色, rect, 2, border_radius=8)
            文字を描く(self.screen, self.small_font, name, 文字色, (rect.left + 13, rect.top + 10))

    def _表示切替ボタン(self) -> dict[str, pygame.Rect]:
        return {
            "single": pygame.Rect(24, 145, 132, 43),
            "compare": pygame.Rect(168, 145, 132, 43),
        }

    def _計測値を描く(self) -> None:
        operations = self._現在の操作回数()
        processing_time = self._現在の計算時間()
        per_second = operations / processing_time if processing_time else 0
        completion_time = self._現在の完了時間()
        labels = [
            f"計算時間  {self._時間を表示(processing_time)}",
            f"処理回数  {operations:,}",
            f"毎秒処理  {per_second:,.1f}",
            f"完了時間  {self._時間を表示(completion_time)}",
        ]

        for index, label in enumerate(labels):
            rect = pygame.Rect(330 + index * 270, 105, 258, 52)
            pygame.draw.rect(self.screen, パネル色, rect, border_radius=9)
            pygame.draw.rect(self.screen, 枠色, rect, 1, border_radius=9)
            文字を描く(
                self.screen,
                self.small_font,
                label,
                (水色, 紫色, 緑色, 黄色)[index],
                (rect.left + 14, rect.top + 14),
            )

    def _ソートを描く(self) -> None:
        runner = self.sort_runner
        info = runner.algorithm.info
        chart = pygame.Rect(330, 180, 1070, 520)
        pygame.draw.rect(self.screen, パネル色, chart, border_radius=14)

        values = runner.state.values
        bar_width = chart.width / len(values)
        maximum = max(values)

        for index, value in enumerate(values):
            bar_height = round((value / maximum) * (chart.height - 42))
            rect = pygame.Rect(
                chart.left + round(index * bar_width),
                chart.bottom - bar_height,
                max(2, round(bar_width) - 2),
                bar_height,
            )
            color = 緑色 if index in runner.state.sorted_indices else 水色
            if index in runner.state.active_indices:
                color = 黄色
            pygame.draw.rect(self.screen, color, rect, border_radius=2)

        文字を描く(self.screen, self.heading_font, info.name, 文字色, (330, 716))
        文字を描く(self.screen, self.small_font, info.summary, 補助文字色, (330, 751))
        文字を描く(self.screen, self.small_font, f"時間計算量: {info.time_complexity}    追加領域: {info.space_complexity}", 紫色, (330, 778))
        文字を描く(self.screen, self.small_font, runner.state.message, 黄色, (330, 805))

    def _素数を描く(self) -> None:
        runner = self.prime_runner
        state = runner.state
        columns = 20
        cell_width = 52
        cell_height = 37
        start_x = 350
        start_y = 180

        for offset, number in enumerate(range(2, state.limit + 1)):
            column = offset % columns
            row = offset // columns
            rect = pygame.Rect(start_x + column * cell_width, start_y + row * cell_height, 47, 32)
            result = state.results.get(number)
            color = 緑色 if result is True else パネル色
            if number == state.current and not runner.done:
                color = 黄色
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            text_color = 背景色 if result is True else 文字色
            文字を描く(self.screen, self.small_font, str(number), text_color, rect.center, True)

        algorithm = runner.algorithm
        文字を描く(self.screen, self.heading_font, algorithm.name, 文字色, (330, 748))
        文字を描く(self.screen, self.small_font, algorithm.summary, 補助文字色, (330, 785))
        文字を描く(self.screen, self.small_font, state.message, 黄色, (850, 785))

    def _数列を描く(self) -> None:
        runner = self.sequence_runner
        chart = pygame.Rect(330, 180, 1070, 540)
        pygame.draw.rect(self.screen, パネル色, chart, border_radius=14)

        if runner.algorithm.key == "recaman":
            self._レカマンを描く(chart, runner.state.values)
        else:
            self._折れ線を描く(chart, runner.state.values)

        文字を描く(self.screen, self.heading_font, runner.algorithm.name, 文字色, (330, 738))
        文字を描く(self.screen, self.small_font, runner.algorithm.rule, 補助文字色, (330, 776))
        文字を描く(self.screen, self.small_font, runner.state.message, 黄色, (330, 804))

    def _レカマンを描く(self, chart: pygame.Rect, values: list[int]) -> None:
        if len(values) < 2:
            return

        maximum = max(max(values), 1)
        baseline = chart.centery
        pygame.draw.line(self.screen, 枠色, (chart.left + 15, baseline), (chart.right - 15, baseline))

        # 同じ表示範囲から「現在の値」と「次の値」の組を作る。
        # 別々の負数スライスを直接zipすると、要素数が少ないときに
        # 先頭同士がずれるため、先にvisibleへ切り出してから1つずらす。
        visible = values[-301:]

        for index, (start, end) in enumerate(
            zip(visible, visible[1:]),
            start=max(1, len(values) - 300),
        ):
            center = (start + end) / 2
            radius = abs(end - start) / 2
            direction = -1 if index % 2 else 1
            points = []

            for point_index in range(25):
                angle = math.pi * point_index / 24
                value_x = center + radius * math.cos(angle)
                x = chart.left + 18 + value_x / maximum * (chart.width - 36)
                y = baseline + direction * math.sin(angle) * radius / maximum * chart.height * 1.7
                points.append((round(x), round(y)))

            color = pygame.Color(0)
            color.hsva = ((index * 9) % 360, 70, 95, 100)
            pygame.draw.lines(self.screen, color, False, points, 2)

    def _折れ線を描く(self, chart: pygame.Rect, values: list[int]) -> None:
        if len(values) < 2:
            return

        visible = values[-250:]
        maximum = max(visible)
        minimum = min(visible)
        value_range = max(1, maximum - minimum)
        points = []

        for index, value in enumerate(visible):
            x = chart.left + 20 + index / max(1, len(visible) - 1) * (chart.width - 40)
            y = chart.bottom - 20 - (value - minimum) / value_range * (chart.height - 40)
            points.append((round(x), round(y)))

        pygame.draw.aalines(self.screen, 紫色, False, points)

    def _比較を描く(self) -> None:
        """選択中のカテゴリに含まれる全アルゴリズムを並べて描く。"""

        if self.mode == "sort":
            self._ソート比較を描く()
        elif self.mode == "prime":
            self._素数比較を描く()
        else:
            self._数列比較を描く()

    def _比較情報を描く(
        self,
        rect: pygame.Rect,
        name: str,
        operations: int,
        done: bool,
        processing_time: float,
        completion_time: float | None,
    ) -> None:
        """比較カードへ名前と速度情報を描く。"""

        if done:
            status = "完了"
            status_color = 緑色
        elif not self.started:
            status = "開始待ち"
            status_color = 補助文字色
        elif self.paused:
            status = "一時停止"
            status_color = 黄色
        else:
            status = "実行中"
            status_color = 黄色

        per_second = operations / processing_time if processing_time else 0
        completion_label = self._時間を表示(completion_time)

        文字を描く(
            self.screen,
            self.normal_font,
            name,
            文字色,
            (rect.left + 12, rect.top + 9),
        )
        文字を描く(
            self.screen,
            self.small_font,
            f"{status}　処理回数 {operations:,}",
            status_color,
            (rect.left + 12, rect.top + 38),
        )
        文字を描く(
            self.screen,
            self.small_font,
            f"毎秒 {per_second:,.0f}　完了時間 {completion_label}",
            補助文字色,
            (rect.left + 12, rect.top + 62),
        )

    def _ソート比較を描く(self) -> None:
        """9種類のソートを3列×3行で同時表示する。"""

        area = pygame.Rect(330, 180, 1070, 630)
        gap = 12
        card_width = (area.width - gap * 2) // 3
        card_height = (area.height - gap * 2) // 3

        for index, runner in enumerate(self.sort_compare_runners):
            column = index % 3
            row = index // 3
            card = pygame.Rect(
                area.left + column * (card_width + gap),
                area.top + row * (card_height + gap),
                card_width,
                card_height,
            )
            pygame.draw.rect(self.screen, パネル色, card, border_radius=11)
            pygame.draw.rect(
                self.screen,
                緑色 if self._ランナー完了(runner) else 枠色,
                card,
                2,
                border_radius=11,
            )
            self._比較情報を描く(
                card,
                runner.algorithm.info.name,
                self._表示用操作回数(runner),
                self._ランナー完了(runner),
                self.processing_times.get(self._ランナーキー(runner), 0.0),
                self.completion_times.get(self._ランナーキー(runner)),
            )

            chart = pygame.Rect(card.left + 10, card.top + 92, card.width - 20, card.height - 102)
            values = runner.state.values
            maximum = max(values)
            bar_width = chart.width / len(values)

            for value_index, value in enumerate(values):
                bar_height = round(value / maximum * chart.height)
                bar = pygame.Rect(
                    chart.left + round(value_index * bar_width),
                    chart.bottom - bar_height,
                    max(1, round(bar_width) - 1),
                    bar_height,
                )
                color = 緑色 if value_index in runner.state.sorted_indices else 水色
                if value_index in runner.state.active_indices:
                    color = 黄色
                pygame.draw.rect(self.screen, color, bar)

    def _素数比較を描く(self) -> None:
        """2種類の素数探索を同じ1〜300の範囲で比較する。"""

        gap = 24
        card_width = 523

        for index, runner in enumerate(self.prime_compare_runners):
            card = pygame.Rect(330 + index * (card_width + gap), 180, card_width, 630)
            pygame.draw.rect(self.screen, パネル色, card, border_radius=12)
            pygame.draw.rect(
                self.screen,
                緑色 if self._ランナー完了(runner) else 枠色,
                card,
                2,
                border_radius=12,
            )
            self._比較情報を描く(
                card,
                runner.algorithm.name,
                self._表示用操作回数(runner),
                self._ランナー完了(runner),
                self.processing_times.get(self._ランナーキー(runner), 0.0),
                self.completion_times.get(self._ランナーキー(runner)),
            )

            columns = 20
            cell = 23
            start_x = card.left + 31
            start_y = card.top + 105

            for offset, number in enumerate(range(2, runner.state.limit + 1)):
                column = offset % columns
                row = offset // columns
                square = pygame.Rect(start_x + column * cell, start_y + row * 32, 19, 26)
                result = runner.state.results.get(number)
                color = 緑色 if result is True else (13, 19, 34)
                if number == runner.state.current and not self._ランナー完了(runner):
                    color = 黄色
                pygame.draw.rect(self.screen, color, square, border_radius=3)

            文字を描く(
                self.screen,
                self.small_font,
                runner.state.message,
                補助文字色,
                (card.left + 16, card.bottom - 35),
            )

    def _数列比較を描く(self) -> None:
        """レカマン数列とコラッツ数列を横並びで比較する。"""

        gap = 24
        card_width = 523

        for index, runner in enumerate(self.sequence_compare_runners):
            card = pygame.Rect(330 + index * (card_width + gap), 180, card_width, 630)
            pygame.draw.rect(self.screen, パネル色, card, border_radius=12)
            pygame.draw.rect(
                self.screen,
                緑色 if self._ランナー完了(runner) else 枠色,
                card,
                2,
                border_radius=12,
            )
            self._比較情報を描く(
                card,
                runner.algorithm.name,
                self._表示用操作回数(runner),
                self._ランナー完了(runner),
                self.processing_times.get(self._ランナーキー(runner), 0.0),
                self.completion_times.get(self._ランナーキー(runner)),
            )

            chart = pygame.Rect(card.left + 14, card.top + 102, card.width - 28, 450)
            pygame.draw.rect(self.screen, (13, 19, 34), chart, border_radius=8)

            if runner.algorithm.key == "recaman":
                self._レカマンを描く(chart, runner.state.values)
            else:
                self._折れ線を描く(chart, runner.state.values)

            文字を描く(
                self.screen,
                self.small_font,
                runner.state.message,
                補助文字色,
                (card.left + 16, card.bottom - 44),
            )

    def _操作欄を描く(self) -> None:
        pygame.draw.line(self.screen, 枠色, (0, 825), (幅, 825))
        self.start_button.label = "開始済み" if self.started else "スタート"
        self.pause_button.label = "再開" if self.paused else "一時停止"
        for button in (
            self.home_button,
            self.start_button,
            self.pause_button,
            self.step_button,
            self.reset_button,
        ):
            button.描く(self.screen, self.small_font)
        self.data_slider.描く(self.screen, self.small_font)
        self.speed_slider.描く(self.screen, self.small_font)


def main() -> None:
    app = 可視化アプリ()
    app.実行()


if __name__ == "__main__":
    main()
