"""クイックソート。

基準値（ピボット）より小さい値を左、大きい値を右へ分け、
分けた範囲に対して同じ処理を再帰的に行う。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    yield from _quick_sort(state, 0, len(state.values) - 1)


def _quick_sort(state: SortState, left: int, right: int) -> Iterator[None]:
    """leftからrightまでを再帰的に整列する。"""

    if left >= right:
        if left == right:
            state.sorted_indices.add(left)
        return

    pivot_index = yield from _partition(state, left, right)
    state.sorted_indices.add(pivot_index)

    yield from _quick_sort(state, left, pivot_index - 1)
    yield from _quick_sort(state, pivot_index + 1, right)


def _partition(state: SortState, left: int, right: int) -> Iterator[None]:
    """右端をピボットにし、値を左右へ振り分ける。"""

    values = state.values
    pivot = values[right]
    boundary = left

    for index in range(left, right):
        state.active_indices = (index, right)
        state.comparisons += 1
        state.message = f"{values[index]} とピボット {pivot} を比較"
        yield

        if values[index] <= pivot:
            values[boundary], values[index] = values[index], values[boundary]
            state.writes += 2
            state.active_indices = (boundary, index)
            state.message = "小さい値を左側へ移動"
            boundary += 1
            yield

    values[boundary], values[right] = values[right], values[boundary]
    state.writes += 2
    state.active_indices = (boundary, right)
    state.message = "ピボットの位置を確定"
    yield

    return boundary


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="quick",
        name="クイックソート",
        summary="ピボットを基準に左右へ分割し、再帰的に整列します。",
        time_complexity="平均 O(n log n) / 最悪 O(n²)",
        space_complexity="平均 O(log n)",
    ),
    create_steps=create_steps,
)
