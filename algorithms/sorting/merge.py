"""マージソート。

数列を半分ずつに分割し、整列した小さな数列を結合する。
補助リストを使う代わりに、入力の並びに左右されにくい速さを持つ。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    yield from _merge_sort(state, 0, len(state.values))


def _merge_sort(state: SortState, start: int, end: int) -> Iterator[None]:
    """start以上end未満の範囲を整列する。"""

    if end - start <= 1:
        return

    middle = (start + end) // 2
    yield from _merge_sort(state, start, middle)
    yield from _merge_sort(state, middle, end)
    yield from _merge(state, start, middle, end)


def _merge(
    state: SortState,
    start: int,
    middle: int,
    end: int,
) -> Iterator[None]:
    """2つの整列済み範囲を1つに結合する。"""

    values = state.values
    left_values = values[start:middle]
    right_values = values[middle:end]
    left_index = 0
    right_index = 0
    write_index = start

    while left_index < len(left_values) and right_index < len(right_values):
        state.active_indices = (start + left_index, middle + right_index)
        state.comparisons += 1
        state.message = "左右の先頭を比較して小さい方を書き戻す"
        yield

        if left_values[left_index] <= right_values[right_index]:
            values[write_index] = left_values[left_index]
            left_index += 1
        else:
            values[write_index] = right_values[right_index]
            right_index += 1

        state.writes += 1
        write_index += 1
        yield

    remaining = left_values[left_index:] + right_values[right_index:]

    for value in remaining:
        values[write_index] = value
        state.active_indices = (write_index,)
        state.writes += 1
        state.message = "残っている値を書き戻す"
        write_index += 1
        yield


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="merge",
        name="マージソート",
        summary="半分に分割し、整列済みの範囲を結合します。",
        time_complexity="O(n log n)",
        space_complexity="O(n)",
    ),
    create_steps=create_steps,
)
