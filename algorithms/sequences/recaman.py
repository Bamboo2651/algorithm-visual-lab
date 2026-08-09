"""Recamán（レカマン）数列。

現在値から項番号を引けて、その値が未登場なら引く。
引けない場合は項番号を足す。弧で結ぶと特徴的な模様になる。
"""

from collections.abc import Iterator

from .common import SequenceAlgorithm, SequenceState


def create_steps(state: SequenceState) -> Iterator[None]:
    current = 0
    seen = {0}
    state.values.append(current)

    index = 1

    while True:
        backward = current - index

        if backward > 0 and backward not in seen:
            current = backward
            state.message = f"{index} を引いて {current} へ移動"
        else:
            current += index
            state.message = f"引けないため {index} を足して {current} へ移動"

        seen.add(current)
        state.values.append(current)
        state.operations += 1
        index += 1
        yield


ALGORITHM = SequenceAlgorithm(
    key="recaman",
    name="レカマン数列",
    summary="引けるときは戻り、引けないときは前へ進む数列です。",
    rule="a(n)=a(n-1)-n が正かつ未登場なら引く。それ以外は足す。",
    create_steps=create_steps,
)
