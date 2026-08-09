"""カクテルソート。

バブルソートを左右両方向に行う方法。
右へ大きい値を運んだ後、左へ小さい値を運ぶため、偏った並びに強くなる。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values
    left = 0
    right = len(values) - 1

    while left < right:
        swapped = False

        for index in range(left, right):
            state.active_indices = (index, index + 1)
            state.comparisons += 1
            state.message = "右方向へ比較"
            yield

            if values[index] > values[index + 1]:
                values[index], values[index + 1] = values[index + 1], values[index]
                state.writes += 2
                swapped = True
                yield

        state.sorted_indices.add(right)
        right -= 1

        if not swapped:
            break

        swapped = False

        for index in range(right, left, -1):
            state.active_indices = (index - 1, index)
            state.comparisons += 1
            state.message = "左方向へ比較"
            yield

            if values[index - 1] > values[index]:
                values[index - 1], values[index] = values[index], values[index - 1]
                state.writes += 2
                swapped = True
                yield

        state.sorted_indices.add(left)
        left += 1

        if not swapped:
            break


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="cocktail",
        name="カクテルソート",
        summary="左右へ交互に走査するバブルソートです。",
        time_complexity="平均 O(n²) / 最良 O(n)",
        space_complexity="O(1)",
    ),
    create_steps=create_steps,
)
