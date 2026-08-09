"""数列アルゴリズムの代表的な値を確認する。"""

from algorithms.sequences.collatz import ALGORITHM as COLLATZ
from algorithms.sequences.common import SequenceRunner
from algorithms.sequences.recaman import ALGORITHM as RECAMAN


def test_recaman_prefix() -> None:
    runner = SequenceRunner(RECAMAN)

    for _ in range(15):
        runner.step()

    assert runner.state.values[:16] == [
        0, 1, 3, 6, 2, 7, 13, 20,
        12, 21, 11, 22, 10, 23, 9, 24,
    ]


def test_collatz_reaches_one() -> None:
    runner = SequenceRunner(COLLATZ)

    for _ in range(10_000):
        if runner.done:
            break
        runner.step()

    assert runner.done
    assert runner.state.values[-1] == 1
