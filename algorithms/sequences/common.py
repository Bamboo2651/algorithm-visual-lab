"""数列アルゴリズムで共有するデータ構造。"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field


@dataclass
class SequenceState:
    values: list[int] = field(default_factory=list)
    operations: int = 0
    message: str = "開始前"
    done: bool = False


SequenceStepGenerator = Callable[[SequenceState], Iterator[None]]


@dataclass(frozen=True)
class SequenceAlgorithm:
    key: str
    name: str
    summary: str
    rule: str
    create_steps: SequenceStepGenerator


class SequenceRunner:
    def __init__(self, algorithm: SequenceAlgorithm) -> None:
        self.algorithm = algorithm
        self.state = SequenceState()
        self._steps = algorithm.create_steps(self.state)

    @property
    def done(self) -> bool:
        return self.state.done

    def step(self) -> None:
        if self.state.done:
            return

        try:
            next(self._steps)
        except StopIteration:
            self.state.done = True
            self.state.message = "生成完了"
