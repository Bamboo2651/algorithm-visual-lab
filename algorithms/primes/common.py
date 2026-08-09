"""素数探索で共有するデータ構造。"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field


@dataclass
class PrimeState:
    """GUIが描画する素数探索の途中状態。"""

    limit: int
    current: int = 2
    divisor: int | None = None
    results: dict[int, bool] = field(default_factory=dict)
    operations: int = 0
    message: str = "開始前"

    @property
    def primes(self) -> list[int]:
        return [number for number, is_prime in self.results.items() if is_prime]


PrimeStepGenerator = Callable[[PrimeState], Iterator[None]]


@dataclass(frozen=True)
class PrimeAlgorithm:
    key: str
    name: str
    summary: str
    time_complexity: str
    create_steps: PrimeStepGenerator


class PrimeRunner:
    """素数探索を1ステップずつ実行する。"""

    def __init__(self, algorithm: PrimeAlgorithm, limit: int = 300) -> None:
        self.algorithm = algorithm
        self.state = PrimeState(limit=limit)
        self._steps = algorithm.create_steps(self.state)
        self.done = False

    def step(self) -> None:
        if self.done:
            return

        try:
            next(self._steps)
        except StopIteration:
            self.done = True
            self.state.divisor = None
            self.state.message = "探索完了"
