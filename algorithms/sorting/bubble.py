"""バブルソート。

隣り合う2つを比べ、大きい値を右へ少しずつ移動させる。
1周するたびに、未整列部分で最大の値が右端へ確定する。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values

    for end in range(len(values) - 1, 0, -1):
        swapped = False

        for index in range(end):
            state.active_indices = (index, index + 1)
            state.comparisons += 1
            state.message = f"{values[index]} と {values[index + 1]} を比較"
            yield

            if values[index] > values[index + 1]:
                values[index], values[index + 1] = values[index + 1], values[index]
                state.writes += 2
                state.message = "左の値が大きいため交換"
                swapped = True
                yield

        state.sorted_indices.add(end)

        if not swapped:
            break


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="bubble",
        name="バブルソート",
        summary="隣同士を交換し、大きい値を右端へ浮かせます。",
        time_complexity="平均 O(n²) / 最良 O(n)",
        space_complexity="O(1)",
    ),
    create_steps=create_steps,
)
