"""計数ソート。

値同士を比較せず、それぞれの値が何回登場したかを数える。
扱う値の範囲が小さいときに非常に高速だが、広い範囲には大きなメモリが必要。
"""

from collections.abc import Iterator

from .common import AlgorithmInfo, SortAlgorithm, SortState


def create_steps(state: SortState) -> Iterator[None]:
    values = state.values

    if not values:
        return

    maximum = max(values)
    counts = [0] * (maximum + 1)

    # それぞれの値が何回登場するかを数える。
    for index, value in enumerate(values):
        counts[value] += 1
        state.active_indices = (index,)
        state.writes += 1
        state.message = f"値 {value} の個数を数える"
        yield

    write_index = 0

    # 小さい値から登場回数分だけ元のリストへ書き戻す。
    for value, count in enumerate(counts):
        for _ in range(count):
            values[write_index] = value
            state.active_indices = (write_index,)
            state.sorted_indices.add(write_index)
            state.writes += 1
            state.message = f"値 {value} を位置 {write_index} へ書き戻す"
            write_index += 1
            yield


ALGORITHM = SortAlgorithm(
    info=AlgorithmInfo(
        key="counting",
        name="計数ソート",
        summary="値の登場回数を数え、小さい順に書き戻します。",
        time_complexity="O(n + k)（kは値の範囲）",
        space_complexity="O(k)",
    ),
    create_steps=create_steps,
)
