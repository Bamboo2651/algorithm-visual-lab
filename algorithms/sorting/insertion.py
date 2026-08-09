"""挿入ソート。

左側を整列済みの領域として扱い、新しい値を正しい位置へ差し込む。
トランプを手札へ順番に入れる動きに似ている。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values

    for index in range(1, len(values)):
        value_to_insert = values[index]
        position = index

        while position > 0:
            state.active_indices = (position - 1, position)
            state.comparisons += 1
            state.message = f"{value_to_insert} を左側の値と比較"
            yield

            if values[position - 1] <= value_to_insert:
                break

            values[position] = values[position - 1]
            state.writes += 1
            position -= 1
            state.message = "大きい値を1つ右へ移動"
            yield

        values[position] = value_to_insert
        state.writes += 1
        state.sorted_indices = set(range(index + 1))
        state.message = f"{value_to_insert} を位置 {position} へ挿入"
        yield


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="insertion",
        name="挿入ソート",
        summary="整列済み部分の正しい場所へ値を差し込みます。",
        time_complexity="平均 O(n²) / 最良 O(n)",
        space_complexity="O(1)",
    ),
    create_steps=create_steps,
)
