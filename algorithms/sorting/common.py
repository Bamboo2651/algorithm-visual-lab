"""すべてのソートアルゴリズムで共有する状態と実行機能。"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AlgorithmInfo:
    """GUIと学習画面に表示するアルゴリズムの説明。"""

    key: str
    name: str
    summary: str
    time_complexity: str
    space_complexity: str


@dataclass
class SortState:
    """ソート中に変化する値を1か所にまとめる。

    アルゴリズム側はこのオブジェクトを更新し、GUI側はこの状態を
    読み取って棒グラフを描く。計算と描画を分離するための入れ物である。
    """

    values: list[int]
    active_indices: tuple[int, ...] = ()
    sorted_indices: set[int] = field(default_factory=set)
    comparisons: int = 0
    writes: int = 0
    message: str = "開始前"


StepGenerator = Callable[[SortState], Iterator[None]]


@dataclass(frozen=True)
class SortAlgorithm:
    """説明と処理本体を組にしたソートアルゴリズム。"""

    info: AlgorithmInfo
    create_steps: StepGenerator


class SortRunner:
    """ジェネレーターを使ってソートを1ステップずつ進める。"""

    def __init__(self, algorithm: SortAlgorithm, values: list[int]) -> None:
        self.algorithm = algorithm
        self.state = SortState(values.copy())
        self._steps = algorithm.create_steps(self.state)
        self.done = False

    @property
    def operations(self) -> int:
        return self.state.comparisons + self.state.writes

    def step(self) -> None:
        if self.done:
            return

        try:
            next(self._steps)
        except StopIteration:
            self.done = True
            self.state.active_indices = ()
            self.state.sorted_indices = set(range(len(self.state.values)))
            self.state.message = "完了"
