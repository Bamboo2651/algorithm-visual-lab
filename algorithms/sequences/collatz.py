"""コラッツ数列。

偶数なら2で割り、奇数なら3倍して1を足す。
どの正の整数から始めても最終的に1へ到達すると予想されている。
"""

from collections.abc import Iterator

from .common import SequenceAlgorithm, SequenceState


START_VALUE = 6_171


def create_steps(state: SequenceState) -> Iterator[None]:
    current = START_VALUE
    state.values.append(current)
    state.message = f"開始値は {current}"
    yield

    while current != 1:
        previous = current

        if current % 2 == 0:
            current //= 2
            state.message = f"{previous} は偶数なので2で割る"
        else:
            current = current * 3 + 1
            state.message = f"{previous} は奇数なので3倍して1を足す"

        state.values.append(current)
        state.operations += 1
        yield

    state.done = True
    state.message = "1へ到達"


ALGORITHM = SequenceAlgorithm(
    key="collatz",
    name="コラッツ数列",
    summary="偶数と奇数で異なる計算を繰り返す数列です。",
    rule="偶数: n÷2、奇数: 3n+1。開始値は6,171。",
    create_steps=create_steps,
)
