from __future__ import annotations

import math
import random

import pygame


# ============================================================
# 基本設定
# ============================================================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 760
FPS = 60

BACKGROUND = (8, 12, 24)
PANEL_COLOR = (18, 25, 43)
PANEL_HOVER = (27, 38, 63)
BORDER_COLOR = (54, 70, 105)
TEXT_COLOR = (235, 242, 255)
SUBTEXT_COLOR = (145, 160, 190)

CYAN = (69, 220, 255)
BLUE = (90, 130, 255)
PURPLE = (180, 100, 255)
GREEN = (90, 230, 160)
YELLOW = (255, 215, 90)
RED = (255, 100, 120)

HEADER_HEIGHT = 90
FOOTER_HEIGHT = 90


# ============================================================
# 共通関数
# ============================================================

def draw_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    position: tuple[int, int],
    center: bool = False,
) -> None:
    """画面へ文字を描画する。"""

    image = font.render(text, True, color)
    rect = image.get_rect()

    if center:
        rect.center = position
    else:
        rect.topleft = position

    screen.blit(image, rect)


def format_number(value: int | float) -> str:
    """数字を3桁区切りで表示する。"""

    if isinstance(value, float):
        return f"{value:,.1f}"

    return f"{value:,}"


# ============================================================
# ボタン
# ============================================================

class Button:
    """クリックできる長方形のボタン。"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label

    def clicked(self, event: pygame.event.Event) -> bool:
        """このボタンがクリックされたか調べる。"""

        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        """ボタンを描画する。"""

        mouse_position = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_position)

        color = PANEL_HOVER if is_hovered else PANEL_COLOR

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            BORDER_COLOR,
            self.rect,
            width=2,
            border_radius=10,
        )

        draw_text(
            screen,
            font,
            self.label,
            TEXT_COLOR,
            self.rect.center,
            center=True,
        )


# ============================================================
# スライダー
# ============================================================

class Slider:
    """マウスで値を変更できるスライダー。"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        minimum: int,
        maximum: int,
        value: int,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, 8)

        self.minimum = minimum
        self.maximum = maximum
        self.value = value

        self.dragging = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """マウス操作を受け取って値を変更する。"""

        handle_rect = pygame.Rect(
            self.handle_x - 10,
            self.rect.centery - 10,
            20,
            20,
        )

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.inflate(20, 24).collidepoint(event.pos):
                    self.dragging = True
                    self.set_value_from_x(event.pos[0])

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.set_value_from_x(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

    def set_value_from_x(self, mouse_x: int) -> None:
        """マウスのX座標をスライダーの値へ変換する。"""

        limited_x = max(
            self.rect.left,
            min(mouse_x, self.rect.right),
        )

        ratio = (
            (limited_x - self.rect.left)
            / self.rect.width
        )

        value_range = self.maximum - self.minimum

        self.value = round(
            self.minimum + value_range * ratio
        )

    @property
    def handle_x(self) -> int:
        """現在値に対応するつまみのX座標を返す。"""

        ratio = (
            (self.value - self.minimum)
            / (self.maximum - self.minimum)
        )

        return round(
            self.rect.left + self.rect.width * ratio
        )

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        """スライダーを描画する。"""

        pygame.draw.rect(
            screen,
            BORDER_COLOR,
            self.rect,
            border_radius=4,
        )

        active_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.handle_x - self.rect.left,
            self.rect.height,
        )

        pygame.draw.rect(
            screen,
            CYAN,
            active_rect,
            border_radius=4,
        )

        pygame.draw.circle(
            screen,
            TEXT_COLOR,
            (self.handle_x, self.rect.centery),
            10,
        )

        draw_text(
            screen,
            font,
            f"Speed: {self.value} steps/sec",
            TEXT_COLOR,
            (self.rect.left, self.rect.top - 27),
        )


# ============================================================
# ソートアルゴリズム
# ============================================================

class SortRunner:
    """1種類のソートアルゴリズムの状態を管理する。"""

    def __init__(
        self,
        name: str,
        values: list[int],
        algorithm,
        color: tuple[int, int, int],
    ) -> None:
        self.name = name
        self.values = values.copy()
        self.color = color

        self.active_indices: tuple[int, int] | None = None
        self.comparisons = 0
        self.swaps = 0
        self.done = False

        self.generator = algorithm(self)

    @property
    def operations(self) -> int:
        """比較回数と交換回数の合計を返す。"""

        return self.comparisons + self.swaps

    def step(self) -> None:
        """アルゴリズムを1段階だけ進める。"""

        if self.done:
            return

        try:
            next(self.generator)

        except StopIteration:
            self.done = True
            self.active_indices = None


def bubble_sort(runner: SortRunner):
    """バブルソートを1比較ずつ進めるジェネレーター。"""

    values = runner.values
    length = len(values)

    for end in range(length - 1, 0, -1):
        swapped = False

        for index in range(end):
            runner.active_indices = (index, index + 1)
            runner.comparisons += 1

            if values[index] > values[index + 1]:
                values[index], values[index + 1] = (
                    values[index + 1],
                    values[index],
                )

                runner.swaps += 1
                swapped = True

            yield

        if not swapped:
            break


def insertion_sort(runner: SortRunner):
    """挿入ソートを1比較ずつ進めるジェネレーター。"""

    values = runner.values

    for index in range(1, len(values)):
        current_value = values[index]
        position = index

        while position > 0:
            runner.active_indices = (
                position - 1,
                position,
            )

            runner.comparisons += 1
            yield

            if values[position - 1] <= current_value:
                break

            values[position] = values[position - 1]
            runner.swaps += 1
            position -= 1

            yield

        values[position] = current_value


def selection_sort(runner: SortRunner):
    """選択ソートを1比較ずつ進めるジェネレーター。"""

    values = runner.values
    length = len(values)

    for start in range(length - 1):
        smallest = start

        for index in range(start + 1, length):
            runner.active_indices = (smallest, index)
            runner.comparisons += 1

            yield

            if values[index] < values[smallest]:
                smallest = index

        if smallest != start:
            values[start], values[smallest] = (
                values[smallest],
                values[start],
            )

            runner.active_indices = (start, smallest)
            runner.swaps += 1

            yield


class SortMode:
    """ソート競争全体を管理する。"""

    def __init__(self) -> None:
        self.runners: list[SortRunner] = []
        self.reset()

    def reset(self) -> None:
        """3つのソートを同じ数列で最初から作り直す。"""

        values = list(range(1, 41))
        random.shuffle(values)

        self.runners = [
            SortRunner(
                "Bubble Sort",
                values,
                bubble_sort,
                CYAN,
            ),
            SortRunner(
                "Insertion Sort",
                values,
                insertion_sort,
                PURPLE,
            ),
            SortRunner(
                "Selection Sort",
                values,
                selection_sort,
                GREEN,
            ),
        ]

    @property
    def operations(self) -> int:
        return sum(
            runner.operations
            for runner in self.runners
        )

    @property
    def done(self) -> bool:
        return all(
            runner.done
            for runner in self.runners
        )

    def step(self) -> None:
        for runner in self.runners:
            runner.step()


# ============================================================
# 素数探索
# ============================================================

class PrimeMode:
    """割り算を少しずつ行って素数を探す。"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.candidate = 2
        self.divisor = 2

        self.results: dict[int, bool] = {}
        self.primes: list[int] = []

        self.operations = 0

    def step(self) -> None:
        """割り算による判定を1回進める。"""

        # 2は最初の素数
        if self.candidate == 2:
            self.finish_candidate(True)
            return

        self.operations += 1

        # 約数は平方根まで調べればよい
        if self.divisor * self.divisor > self.candidate:
            self.finish_candidate(True)
            return

        # 割り切れたら素数ではない
        if self.candidate % self.divisor == 0:
            self.finish_candidate(False)
            return

        self.divisor += 1

    def finish_candidate(self, is_prime: bool) -> None:
        """現在の数字の判定結果を保存する。"""

        self.results[self.candidate] = is_prime

        if is_prime:
            self.primes.append(self.candidate)

        self.candidate += 1
        self.divisor = 2


# ============================================================
# Recamán数列
# ============================================================

class RecamanMode:
    """Recamán数列と描画用の弧を管理する。"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.current = 0
        self.index = 1

        self.values = [0]
        self.seen = {0}

        self.arcs: list[tuple[int, int, int]] = []
        self.operations = 0

    def step(self) -> None:
        """Recamán数列を1項進める。"""

        previous = self.current
        backward = self.current - self.index

        if backward > 0 and backward not in self.seen:
            self.current = backward
        else:
            self.current += self.index

        self.values.append(self.current)
        self.seen.add(self.current)

        self.arcs.append(
            (previous, self.current, self.index)
        )

        self.index += 1
        self.operations += 1


# ============================================================
# アプリ本体
# ============================================================

class AlgorithmVisualLab:
    """アプリ全体を管理するクラス。"""

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        pygame.display.set_caption(
            "Algorithm Visual Lab"
        )

        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            34,
            bold=True,
        )

        self.heading_font = pygame.font.SysFont(
            "Segoe UI",
            24,
            bold=True,
        )

        self.normal_font = pygame.font.SysFont(
            "Segoe UI",
            18,
        )

        self.small_font = pygame.font.SysFont(
            "Segoe UI",
            15,
        )

        self.mode = "menu"
        self.running = True
        self.paused = False

        self.elapsed_time = 0.0
        self.step_accumulator = 0.0

        self.sort_mode = SortMode()
        self.prime_mode = PrimeMode()
        self.recaman_mode = RecamanMode()

        footer_y = WINDOW_HEIGHT - 67

        self.home_button = Button(
            25,
            footer_y,
            110,
            44,
            "Home",
        )

        self.pause_button = Button(
            150,
            footer_y,
            120,
            44,
            "Pause",
        )

        self.step_button = Button(
            285,
            footer_y,
            110,
            44,
            "Step",
        )

        self.reset_button = Button(
            410,
            footer_y,
            110,
            44,
            "Reset",
        )

        self.speed_slider = Slider(
            640,
            WINDOW_HEIGHT - 43,
            500,
            1,
            300,
            40,
        )

        self.menu_cards = {
            "sort": pygame.Rect(
                55,
                190,
                335,
                330,
            ),
            "prime": pygame.Rect(
                432,
                190,
                335,
                330,
            ),
            "recaman": pygame.Rect(
                809,
                190,
                335,
                330,
            ),
        }

    def run(self) -> None:
        """ゲームループを開始する。"""

        while self.running:
            delta_time = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()

    def handle_events(self) -> None:
        """キーボードとマウスの操作を処理する。"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self.handle_keyboard(event)

            if self.mode == "menu":
                self.handle_menu_click(event)

            else:
                self.handle_control_click(event)
                self.speed_slider.handle_event(event)

    def handle_keyboard(
        self,
        event: pygame.event.Event,
    ) -> None:
        """キーボードショートカットを処理する。"""

        if event.key == pygame.K_ESCAPE:
            self.open_menu()

        elif event.key == pygame.K_SPACE:
            if self.mode != "menu":
                self.paused = not self.paused

        elif event.key == pygame.K_RIGHT:
            if self.mode != "menu":
                self.perform_one_step()

        elif event.key == pygame.K_r:
            if self.mode != "menu":
                self.reset_current_mode()

        elif event.key == pygame.K_1:
            self.open_mode("sort")

        elif event.key == pygame.K_2:
            self.open_mode("prime")

        elif event.key == pygame.K_3:
            self.open_mode("recaman")

    def handle_menu_click(
        self,
        event: pygame.event.Event,
    ) -> None:
        """メニューカードのクリックを処理する。"""

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        for mode_name, rect in self.menu_cards.items():
            if rect.collidepoint(event.pos):
                self.open_mode(mode_name)

    def handle_control_click(
        self,
        event: pygame.event.Event,
    ) -> None:
        """画面下部のボタン操作を処理する。"""

        if self.home_button.clicked(event):
            self.open_menu()

        elif self.pause_button.clicked(event):
            self.paused = not self.paused

        elif self.step_button.clicked(event):
            self.perform_one_step()

        elif self.reset_button.clicked(event):
            self.reset_current_mode()

    def open_menu(self) -> None:
        self.mode = "menu"
        self.paused = False

    def open_mode(self, mode_name: str) -> None:
        self.mode = mode_name
        self.paused = False

        self.elapsed_time = 0.0
        self.step_accumulator = 0.0

        self.reset_current_mode()

    def reset_current_mode(self) -> None:
        """現在表示中のモードを初期状態へ戻す。"""

        self.elapsed_time = 0.0
        self.step_accumulator = 0.0
        self.paused = False

        if self.mode == "sort":
            self.sort_mode.reset()

        elif self.mode == "prime":
            self.prime_mode.reset()

        elif self.mode == "recaman":
            self.recaman_mode.reset()

    def update(self, delta_time: float) -> None:
        """時間経過に応じて計算を進める。"""

        if self.mode == "menu":
            return

        if self.paused:
            return

        self.elapsed_time += delta_time

        self.step_accumulator += (
            delta_time * self.speed_slider.value
        )

        steps = int(self.step_accumulator)

        if steps == 0:
            return

        self.step_accumulator -= steps

        # 1フレームで進みすぎないよう制限する
        steps = min(steps, 1000)

        for _ in range(steps):
            self.perform_one_step()

    def perform_one_step(self) -> None:
        """現在のモードを1段階だけ進める。"""

        if self.mode == "sort":
            self.sort_mode.step()

        elif self.mode == "prime":
            self.prime_mode.step()

        elif self.mode == "recaman":
            self.recaman_mode.step()

    @property
    def current_operations(self) -> int:
        if self.mode == "sort":
            return self.sort_mode.operations

        if self.mode == "prime":
            return self.prime_mode.operations

        if self.mode == "recaman":
            return self.recaman_mode.operations

        return 0

    def draw(self) -> None:
        """現在の状態を画面へ描画する。"""

        self.screen.fill(BACKGROUND)

        self.draw_header()

        if self.mode == "menu":
            self.draw_menu()

        elif self.mode == "sort":
            self.draw_sort_mode()

        elif self.mode == "prime":
            self.draw_prime_mode()

        elif self.mode == "recaman":
            self.draw_recaman_mode()

        if self.mode != "menu":
            self.draw_controls()

        pygame.display.flip()

    def draw_header(self) -> None:
        """画面上部のタイトルを描画する。"""

        pygame.draw.line(
            self.screen,
            BORDER_COLOR,
            (0, HEADER_HEIGHT),
            (WINDOW_WIDTH, HEADER_HEIGHT),
            width=1,
        )

        draw_text(
            self.screen,
            self.title_font,
            "Algorithm Visual Lab",
            TEXT_COLOR,
            (28, 17),
        )

        subtitle = {
            "menu": "Choose a visualization",
            "sort": "Sorting Algorithm Race",
            "prime": "Prime Number Explorer",
            "recaman": "Recaman Sequence Art",
        }[self.mode]

        draw_text(
            self.screen,
            self.normal_font,
            subtitle,
            SUBTEXT_COLOR,
            (30, 57),
        )

    def draw_menu(self) -> None:
        """3つのモード選択カードを描画する。"""

        cards = [
            (
                "sort",
                "1",
                "SORT RACE",
                "Compare three sorting algorithms.",
                CYAN,
            ),
            (
                "prime",
                "2",
                "PRIME EXPLORER",
                "Watch numbers become prime or composite.",
                GREEN,
            ),
            (
                "recaman",
                "3",
                "RECAMAN ART",
                "Draw a number sequence with colorful arcs.",
                PURPLE,
            ),
        ]

        for mode_name, number, title, description, color in cards:
            rect = self.menu_cards[mode_name]
            hovered = rect.collidepoint(
                pygame.mouse.get_pos()
            )

            panel_color = (
                PANEL_HOVER
                if hovered
                else PANEL_COLOR
            )

            pygame.draw.rect(
                self.screen,
                panel_color,
                rect,
                border_radius=18,
            )

            pygame.draw.rect(
                self.screen,
                color,
                rect,
                width=2,
                border_radius=18,
            )

            pygame.draw.circle(
                self.screen,
                color,
                (rect.centerx, rect.top + 75),
                35,
                width=3,
            )

            draw_text(
                self.screen,
                self.heading_font,
                number,
                color,
                (rect.centerx, rect.top + 75),
                center=True,
            )

            draw_text(
                self.screen,
                self.heading_font,
                title,
                TEXT_COLOR,
                (rect.centerx, rect.top + 145),
                center=True,
            )

            draw_text(
                self.screen,
                self.small_font,
                description,
                SUBTEXT_COLOR,
                (rect.centerx, rect.top + 190),
                center=True,
            )

            draw_text(
                self.screen,
                self.normal_font,
                "Click to start",
                color,
                (rect.centerx, rect.bottom - 55),
                center=True,
            )

        draw_text(
            self.screen,
            self.small_font,
            "Keyboard: 1 Sort / 2 Prime / 3 Recaman",
            SUBTEXT_COLOR,
            (WINDOW_WIDTH // 2, 575),
            center=True,
        )

    def draw_metrics(self) -> None:
        """経過時間などの共通情報を描画する。"""

        operations = self.current_operations

        if self.elapsed_time > 0:
            operations_per_second = (
                operations / self.elapsed_time
            )
        else:
            operations_per_second = 0

        metrics = [
            (
                "TIME",
                f"{self.elapsed_time:.1f} sec",
                CYAN,
            ),
            (
                "OPERATIONS",
                format_number(operations),
                PURPLE,
            ),
            (
                "OPS / SEC",
                format_number(operations_per_second),
                GREEN,
            ),
        ]

        card_width = 205
        gap = 16
        total_width = card_width * 3 + gap * 2
        start_x = (WINDOW_WIDTH - total_width) // 2

        for index, (label, value, color) in enumerate(metrics):
            rect = pygame.Rect(
                start_x + index * (card_width + gap),
                105,
                card_width,
                58,
            )

            pygame.draw.rect(
                self.screen,
                PANEL_COLOR,
                rect,
                border_radius=10,
            )

            pygame.draw.rect(
                self.screen,
                BORDER_COLOR,
                rect,
                width=1,
                border_radius=10,
            )

            draw_text(
                self.screen,
                self.small_font,
                label,
                SUBTEXT_COLOR,
                (rect.left + 13, rect.top + 8),
            )

            draw_text(
                self.screen,
                self.normal_font,
                value,
                color,
                (rect.left + 13, rect.top + 30),
            )

    def draw_sort_mode(self) -> None:
        """3種類のソートを棒グラフで描画する。"""

        self.draw_metrics()

        panel_y = 180
        panel_height = 465
        panel_width = 365
        gap = 20
        start_x = 32

        for runner_index, runner in enumerate(
            self.sort_mode.runners
        ):
            panel = pygame.Rect(
                start_x + runner_index * (panel_width + gap),
                panel_y,
                panel_width,
                panel_height,
            )

            pygame.draw.rect(
                self.screen,
                PANEL_COLOR,
                panel,
                border_radius=14,
            )

            pygame.draw.rect(
                self.screen,
                BORDER_COLOR,
                panel,
                width=1,
                border_radius=14,
            )

            status = "DONE" if runner.done else "RUNNING"
            status_color = GREEN if runner.done else runner.color

            draw_text(
                self.screen,
                self.heading_font,
                runner.name,
                TEXT_COLOR,
                (panel.left + 16, panel.top + 14),
            )

            draw_text(
                self.screen,
                self.small_font,
                status,
                status_color,
                (panel.right - 80, panel.top + 20),
            )

            draw_text(
                self.screen,
                self.small_font,
                (
                    f"Comparisons: {runner.comparisons:,}   "
                    f"Moves: {runner.swaps:,}"
                ),
                SUBTEXT_COLOR,
                (panel.left + 16, panel.top + 49),
            )

            chart = pygame.Rect(
                panel.left + 14,
                panel.top + 85,
                panel.width - 28,
                panel.height - 105,
            )

            self.draw_sort_bars(
                runner,
                chart,
            )

    def draw_sort_bars(
        self,
        runner: SortRunner,
        chart: pygame.Rect,
    ) -> None:
        """1つの数列を棒グラフとして描画する。"""

        values = runner.values
        maximum = max(values)

        bar_width = chart.width / len(values)

        for index, value in enumerate(values):
            height_ratio = value / maximum
            bar_height = int(
                chart.height * height_ratio
            )

            x = chart.left + int(index * bar_width)
            y = chart.bottom - bar_height

            width = max(2, int(bar_width) - 2)

            color = runner.color

            if (
                runner.active_indices is not None
                and index in runner.active_indices
            ):
                color = YELLOW

            pygame.draw.rect(
                self.screen,
                color,
                (x, y, width, bar_height),
                border_radius=2,
            )

    def draw_prime_mode(self) -> None:
        """素数を数字のグリッドとして描画する。"""

        self.draw_metrics()

        draw_text(
            self.screen,
            self.heading_font,
            f"Checking: {self.prime_mode.candidate:,}",
            TEXT_COLOR,
            (55, 185),
        )

        draw_text(
            self.screen,
            self.normal_font,
            f"Current divisor: {self.prime_mode.divisor:,}",
            SUBTEXT_COLOR,
            (55, 220),
        )

        draw_text(
            self.screen,
            self.normal_font,
            f"Primes found: {len(self.prime_mode.primes):,}",
            GREEN,
            (920, 195),
        )

        columns = 20
        rows = 10
        cell_width = 52
        cell_height = 37

        grid_width = columns * cell_width
        grid_x = (WINDOW_WIDTH - grid_width) // 2
        grid_y = 265

        visible_count = columns * rows

        start_number = max(
            2,
            self.prime_mode.candidate
            - visible_count
            + 25,
        )

        for offset in range(visible_count):
            number = start_number + offset

            column = offset % columns
            row = offset // columns

            rect = pygame.Rect(
                grid_x + column * cell_width,
                grid_y + row * cell_height,
                cell_width - 4,
                cell_height - 4,
            )

            if number == self.prime_mode.candidate:
                color = YELLOW
                border_width = 2

            elif self.prime_mode.results.get(number) is True:
                color = GREEN
                border_width = 0

            elif self.prime_mode.results.get(number) is False:
                color = PANEL_COLOR
                border_width = 0

            else:
                color = (13, 18, 32)
                border_width = 0

            pygame.draw.rect(
                self.screen,
                color,
                rect,
                width=border_width,
                border_radius=5,
            )

            text_color = (
                BACKGROUND
                if color == GREEN
                else TEXT_COLOR
            )

            draw_text(
                self.screen,
                self.small_font,
                str(number),
                text_color,
                rect.center,
                center=True,
            )

        draw_text(
            self.screen,
            self.small_font,
            "Green = prime    Dark = composite    Yellow = checking",
            SUBTEXT_COLOR,
            (WINDOW_WIDTH // 2, 655),
            center=True,
        )

    def draw_recaman_mode(self) -> None:
        """Recamán数列を半円の連続として描画する。"""

        self.draw_metrics()

        current_value = self.recaman_mode.current
        current_index = self.recaman_mode.index - 1

        draw_text(
            self.screen,
            self.heading_font,
            f"n = {current_index:,}",
            TEXT_COLOR,
            (45, 183),
        )

        draw_text(
            self.screen,
            self.heading_font,
            f"a(n) = {current_value:,}",
            PURPLE,
            (190, 183),
        )

        chart = pygame.Rect(
            35,
            230,
            WINDOW_WIDTH - 70,
            400,
        )

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            chart,
            border_radius=14,
        )

        pygame.draw.line(
            self.screen,
            BORDER_COLOR,
            (chart.left + 15, chart.centery),
            (chart.right - 15, chart.centery),
            width=1,
        )

        self.draw_recaman_arcs(chart)

    def draw_recaman_arcs(
        self,
        chart: pygame.Rect,
    ) -> None:
        """保存された値の間に半円を描画する。"""

        arcs = self.recaman_mode.arcs

        if not arcs:
            return

        visible_arcs = arcs[-400:]

        maximum_value = max(
            max(start, end)
            for start, end, _ in visible_arcs
        )

        maximum_value = max(maximum_value, 1)

        padding = 20
        drawable_width = chart.width - padding * 2

        for start, end, index in visible_arcs:
            center_value = (start + end) / 2
            radius = abs(end - start) / 2

            direction = -1 if index % 2 else 1

            points: list[tuple[int, int]] = []

            for point_index in range(25):
                ratio = point_index / 24
                angle = math.pi * ratio

                value_x = (
                    center_value
                    + radius * math.cos(angle)
                )

                normalized_x = value_x / maximum_value

                x = (
                    chart.left
                    + padding
                    + normalized_x * drawable_width
                )

                radius_ratio = radius / maximum_value

                arc_height = (
                    radius_ratio
                    * chart.height
                    * 1.7
                )

                y = (
                    chart.centery
                    + direction
                    * math.sin(angle)
                    * arc_height
                )

                points.append((round(x), round(y)))

            color = pygame.Color(0)

            color.hsva = (
                (index * 9) % 360,
                70,
                95,
                100,
            )

            pygame.draw.lines(
                self.screen,
                color,
                False,
                points,
                width=2,
            )

    def draw_controls(self) -> None:
        """画面下部の共通操作欄を描画する。"""

        footer_top = WINDOW_HEIGHT - FOOTER_HEIGHT

        pygame.draw.line(
            self.screen,
            BORDER_COLOR,
            (0, footer_top),
            (WINDOW_WIDTH, footer_top),
            width=1,
        )

        self.pause_button.label = (
            "Resume"
            if self.paused
            else "Pause"
        )

        self.home_button.draw(
            self.screen,
            self.normal_font,
        )

        self.pause_button.draw(
            self.screen,
            self.normal_font,
        )

        self.step_button.draw(
            self.screen,
            self.normal_font,
        )

        self.reset_button.draw(
            self.screen,
            self.normal_font,
        )

        self.speed_slider.draw(
            self.screen,
            self.small_font,
        )


def main() -> None:
    app = AlgorithmVisualLab()
    app.run()


if __name__ == "__main__":
    main()