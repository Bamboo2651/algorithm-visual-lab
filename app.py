"""Algorithm Visual LabのPygameアプリ。

このファイルは画面表示と操作だけを担当する。
アルゴリズム本体は algorithms/ 以下に分離している。
"""

from __future__ import annotations

import math
import random

import pygame

from algorithms.primes import ALL_ALGORITHMS as PRIME_ALGORITHMS
from algorithms.primes.common import PrimeRunner
from algorithms.sequences import ALL_ALGORITHMS as SEQUENCE_ALGORITHMS
from algorithms.sequences.common import SequenceRunner
from algorithms.sorting import ALL_ALGORITHMS as SORT_ALGORITHMS
from algorithms.sorting.common import SortRunner


幅 = 1280
高さ = 800
毎秒フレーム数 = 60

背景色 = (8, 12, 24)
パネル色 = (18, 25, 43)
選択色 = (29, 48, 73)
枠色 = (55, 72, 108)
文字色 = (238, 244, 255)
補助文字色 = (150, 166, 196)
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


class 速度スライダー:
    """1秒間に進めるステップ数を変更する。"""

    def __init__(self) -> None:
        self.rect = pygame.Rect(770, 758, 450, 7)
        self.minimum = 1
        self.maximum = 500
        self.value = 50
        self.dragging = False

    @property
    def handle_x(self) -> int:
        ratio = (self.value - self.minimum) / (self.maximum - self.minimum)
        return round(self.rect.left + self.rect.width * ratio)

    def イベント処理(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(24, 28).collidepoint(event.pos):
                self.dragging = True
                self._座標から値を設定(event.pos[0])
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._座標から値を設定(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

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
        pygame.draw.rect(screen, 水色, active, border_radius=4)
        pygame.draw.circle(screen, 文字色, (self.handle_x, self.rect.centery), 9)
        文字を描く(
            screen,
            font,
            f"速度: 毎秒 {self.value} ステップ",
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

        self.title_font = 日本語フォント(32, True)
        self.heading_font = 日本語フォント(22, True)
        self.normal_font = 日本語フォント(17)
        self.small_font = 日本語フォント(14)

        self.running = True
        self.mode = "menu"
        self.paused = False
        self.elapsed = 0.0
        self.accumulator = 0.0

        self.sort_index = 0
        self.prime_index = 0
        self.sequence_index = 0
        self.sort_values: list[int] = []

        self.sort_runner: SortRunner
        self.prime_runner: PrimeRunner
        self.sequence_runner: SequenceRunner
        self._reset_sort()
        self._reset_prime()
        self._reset_sequence()

        self.home_button = ボタン(pygame.Rect(22, 738, 100, 42), "ホーム")
        self.pause_button = ボタン(pygame.Rect(136, 738, 120, 42), "一時停止")
        self.step_button = ボタン(pygame.Rect(270, 738, 110, 42), "1ステップ")
        self.reset_button = ボタン(pygame.Rect(394, 738, 110, 42), "リセット")
        self.speed_slider = 速度スライダー()

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
                self.speed_slider.イベント処理(event)

    def _キー操作(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.mode = "menu"
        elif key == pygame.K_SPACE and self.mode != "menu":
            self.paused = not self.paused
        elif key == pygame.K_RIGHT and self.mode != "menu":
            self._1ステップ進める()
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
        elif self.pause_button.押された(event):
            self.paused = not self.paused
        elif self.step_button.押された(event):
            self._1ステップ進める()
        elif self.reset_button.押された(event):
            self._現在をリセット()

    def _一覧操作(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        names = self._現在の名前一覧()

        for index in range(len(names)):
            rect = pygame.Rect(24, 154 + index * 48, 252, 39)
            if rect.collidepoint(event.pos):
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
        self.paused = False

    def _現在をリセット(self) -> None:
        self._時間をリセット()
        if self.mode == "sort":
            self._reset_sort()
        elif self.mode == "prime":
            self._reset_prime()
        elif self.mode == "sequence":
            self._reset_sequence()

    def _reset_sort(self, keep_values: bool = False) -> None:
        if not keep_values or not self.sort_values:
            self.sort_values = list(range(1, 51))
            random.shuffle(self.sort_values)
        self.sort_runner = SortRunner(SORT_ALGORITHMS[self.sort_index], self.sort_values)

    def _reset_prime(self) -> None:
        self.prime_runner = PrimeRunner(PRIME_ALGORITHMS[self.prime_index], limit=300)

    def _reset_sequence(self) -> None:
        self.sequence_runner = SequenceRunner(SEQUENCE_ALGORITHMS[self.sequence_index])

    def _更新(self, delta_time: float) -> None:
        if self.mode == "menu" or self.paused or self._完了している():
            return

        self.elapsed += delta_time
        self.accumulator += delta_time * self.speed_slider.value
        steps = min(int(self.accumulator), 1000)
        self.accumulator -= steps

        for _ in range(steps):
            self._1ステップ進める()

    def _1ステップ進める(self) -> None:
        if self.mode == "sort":
            self.sort_runner.step()
        elif self.mode == "prime":
            self.prime_runner.step()
        elif self.mode == "sequence":
            self.sequence_runner.step()

    def _完了している(self) -> bool:
        if self.mode == "sort":
            return self.sort_runner.done
        if self.mode == "prime":
            return self.prime_runner.done
        if self.mode == "sequence":
            return self.sequence_runner.done
        return False

    def _現在の操作回数(self) -> int:
        if self.mode == "sort":
            return self.sort_runner.operations
        if self.mode == "prime":
            return self.prime_runner.state.operations
        if self.mode == "sequence":
            return self.sequence_runner.state.operations
        return 0

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
            "sort": pygame.Rect(55, 180, 360, 350),
            "prime": pygame.Rect(460, 180, 360, 350),
            "sequence": pygame.Rect(865, 180, 360, 350),
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
        文字を描く(self.screen, self.heading_font, "アルゴリズム一覧", 文字色, (24, 108))

        for index, name in enumerate(names):
            rect = pygame.Rect(24, 154 + index * 48, 252, 39)
            color = 選択色 if index == selected else パネル色
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, 水色 if index == selected else 枠色, rect, 1, border_radius=8)
            文字を描く(self.screen, self.small_font, name, 文字色, (rect.left + 12, rect.top + 10))

    def _計測値を描く(self) -> None:
        operations = self._現在の操作回数()
        per_second = operations / self.elapsed if self.elapsed else 0
        labels = [
            f"経過時間  {self.elapsed:.1f} 秒",
            f"処理回数  {operations:,}",
            f"毎秒処理  {per_second:,.1f}",
        ]

        for index, label in enumerate(labels):
            rect = pygame.Rect(310 + index * 300, 105, 275, 48)
            pygame.draw.rect(self.screen, パネル色, rect, border_radius=9)
            文字を描く(self.screen, self.normal_font, label, (水色, 紫色, 緑色)[index], (rect.left + 14, rect.top + 13))

    def _ソートを描く(self) -> None:
        runner = self.sort_runner
        info = runner.algorithm.info
        chart = pygame.Rect(310, 180, 930, 425)
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

        文字を描く(self.screen, self.heading_font, info.name, 文字色, (310, 620))
        文字を描く(self.screen, self.small_font, info.summary, 補助文字色, (310, 652))
        文字を描く(self.screen, self.small_font, f"時間計算量: {info.time_complexity}    追加領域: {info.space_complexity}", 紫色, (310, 678))
        文字を描く(self.screen, self.small_font, runner.state.message, 黄色, (310, 704))

    def _素数を描く(self) -> None:
        runner = self.prime_runner
        state = runner.state
        columns = 20
        cell_width = 45
        cell_height = 32
        start_x = 320
        start_y = 185

        for offset, number in enumerate(range(2, state.limit + 1)):
            column = offset % columns
            row = offset // columns
            rect = pygame.Rect(start_x + column * cell_width, start_y + row * cell_height, 41, 28)
            result = state.results.get(number)
            color = 緑色 if result is True else パネル色
            if number == state.current and not runner.done:
                color = 黄色
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            text_color = 背景色 if result is True else 文字色
            文字を描く(self.screen, self.small_font, str(number), text_color, rect.center, True)

        algorithm = runner.algorithm
        文字を描く(self.screen, self.heading_font, algorithm.name, 文字色, (310, 675))
        文字を描く(self.screen, self.small_font, algorithm.summary, 補助文字色, (310, 706))
        文字を描く(self.screen, self.small_font, state.message, 黄色, (770, 706))

    def _数列を描く(self) -> None:
        runner = self.sequence_runner
        chart = pygame.Rect(310, 180, 930, 470)
        pygame.draw.rect(self.screen, パネル色, chart, border_radius=14)

        if runner.algorithm.key == "recaman":
            self._レカマンを描く(chart, runner.state.values)
        else:
            self._折れ線を描く(chart, runner.state.values)

        文字を描く(self.screen, self.heading_font, runner.algorithm.name, 文字色, (310, 665))
        文字を描く(self.screen, self.small_font, runner.algorithm.rule, 補助文字色, (310, 698))
        文字を描く(self.screen, self.small_font, runner.state.message, 黄色, (310, 720))

    def _レカマンを描く(self, chart: pygame.Rect, values: list[int]) -> None:
        if len(values) < 2:
            return

        maximum = max(max(values), 1)
        baseline = chart.centery
        pygame.draw.line(self.screen, 枠色, (chart.left + 15, baseline), (chart.right - 15, baseline))

        for index, (start, end) in enumerate(zip(values[-301:-1], values[-300:]), start=max(1, len(values) - 300)):
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

    def _操作欄を描く(self) -> None:
        pygame.draw.line(self.screen, 枠色, (0, 725), (幅, 725))
        self.pause_button.label = "再開" if self.paused else "一時停止"
        for button in (self.home_button, self.pause_button, self.step_button, self.reset_button):
            button.描く(self.screen, self.small_font)
        self.speed_slider.描く(self.screen, self.small_font)


def main() -> None:
    app = 可視化アプリ()
    app.実行()


if __name__ == "__main__":
    main()
