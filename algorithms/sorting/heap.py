"""ヒープソート。

親が子より大きい「最大ヒープ」を作り、根にある最大値を右端へ移す。
残りの範囲でヒープを作り直す操作を繰り返す。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values
    length = len(values)

    # 葉を持つ最後の親から順に最大ヒープを作る。
    for root in range(length // 2 - 1, -1, -1):
        yield from _sift_down(state, root, length)

    # 最大値を右端へ移し、対象範囲を1つ狭める。
    for end in range(length - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        state.writes += 2
        state.active_indices = (0, end)
        state.sorted_indices.add(end)
        state.message = "最大値を右端へ移動"
        yield

        yield from _sift_down(state, 0, end)


def _sift_down(state: SortState, root: int, size: int) -> Iterator[None]:
    """rootの値を下へ移し、最大ヒープの条件を回復する。"""

    values = state.values

    while True:
        left_child = root * 2 + 1

        if left_child >= size:
            return

        largest = root

        for child in (left_child, left_child + 1):
            if child >= size:
                continue

            state.active_indices = (largest, child)
            state.comparisons += 1
            state.message = "親と子の大きさを比較"
            yield

            if values[child] > values[largest]:
                largest = child

        if largest == root:
            return

        values[root], values[largest] = values[largest], values[root]
        state.writes += 2
        state.active_indices = (root, largest)
        state.message = "大きい子を親の位置へ移動"
        yield

        root = largest


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="heap",
        name="ヒープソート",
        summary="最大値を根へ集め、右端から順番に確定させます。",
        time_complexity="O(n log n)",
        space_complexity="O(1)",
    ),
    create_steps=create_steps,
)
