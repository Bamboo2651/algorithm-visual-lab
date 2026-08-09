"""すべてのソートアルゴリズムに共通する正しさを確認する。"""

import pytest

from algorithms.sorting import ALL_ALGORITHMS
from algorithms.sorting.common import SortRunner


@pytest.mark.parametrize("algorithm", ALL_ALGORITHMS, ids=lambda item: item.info.key)
@pytest.mark.parametrize(
    "values",
    [
        [5, 1, 4, 2, 3],
        [3, 3, 1, 2, 1],
        [1],
        [],
    ],
)
def test_sort_algorithm_orders_values(algorithm, values: list[int]) -> None:
    runner = SortRunner(algorithm, values)

    # 無限ループも検出できるよう、十分大きな上限を設ける。
    for _ in range(10_000):
        if runner.done:
            break
        runner.step()

    assert runner.done
    assert runner.state.values == sorted(values)

