"""シェルソート。

離れた位置の値を先に整列し、間隔を半分ずつ狭める。
最後は間隔1の挿入ソートになるが、事前に値が移動しているため速くなりやすい。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values
    gap = len(values) // 2

    while gap > 0:
        state.message = f"間隔を {gap} に設定"
        yield

        for index in range(gap, len(values)):
            value_to_insert = values[index]
            position = index

            while position >= gap:
                state.active_indices = (position - gap, position)
                state.comparisons += 1
                state.message = f"{gap} 個離れた値を比較"
                yield

                if values[position - gap] <= value_to_insert:
                    break

                values[position] = values[position - gap]
                state.writes += 1
                position -= gap
                yield

            values[position] = value_to_insert
            state.writes += 1
            yield

        gap //= 2


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="shell",
        name="シェルソート",
        summary="広い間隔から挿入ソートし、徐々に間隔を狭めます。",
        time_complexity="間隔列に依存（代表例 O(n²)）",
        space_complexity="O(1)",
    ),
    create_steps=create_steps,
)
