"""選択ソート。

未整列部分から最小値を探し、その先頭へ置く操作を繰り返す。
比較回数は多いが、交換回数が少なく動きを追いやすい。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values

    for start in range(len(values) - 1):
        smallest = start

        for index in range(start + 1, len(values)):
            state.active_indices = (smallest, index)
            state.comparisons += 1
            state.message = f"最小候補 {values[smallest]} と {values[index]} を比較"
            yield

            if values[index] < values[smallest]:
                smallest = index
                state.message = f"新しい最小値は {values[smallest]}"
                yield

        if smallest != start:
            values[start], values[smallest] = values[smallest], values[start]
            state.writes += 2
            state.message = "見つけた最小値を未整列部分の先頭へ移動"
            yield

        state.sorted_indices.add(start)


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="selection",
        name="選択ソート",
        summary="最小値を選び、左から順番に確定させます。",
        time_complexity="O(n²)",
        space_complexity="O(1)",
    ),
    create_steps=create_steps,
)
