"""エラトステネスのふるい。

2から順番に素数を選び、その倍数を合成数として消していく。
一定範囲の素数をまとめて列挙するときに効率がよい。
"""

from collections.abc import Iterator

from .common import PrimeAlgorithm, PrimeState


def create_steps(state: PrimeState) -> Iterator[None]:
    is_prime = [True] * (state.limit + 1)
    is_prime[0] = False
    is_prime[1] = False

    candidate = 2

    while candidate * candidate <= state.limit:
        state.current = candidate
        state.divisor = candidate

        if is_prime[candidate]:
            state.results[candidate] = True
            state.message = f"{candidate} の倍数をふるい落とす"
            yield

            for multiple in range(candidate * candidate, state.limit + 1, candidate):
                state.current = multiple
                state.operations += 1
                is_prime[multiple] = False
                state.results[multiple] = False
                state.message = f"{multiple} は {candidate} の倍数"
                yield

        candidate += 1

    # ふるい落とされなかった数を素数として確定する。
    for number in range(2, state.limit + 1):
        state.current = number
        state.operations += 1
        state.results[number] = is_prime[number]
        state.message = f"{number} の判定を確定"
        yield


ALGORITHM = PrimeAlgorithm(
    key="sieve",
    name="エラトステネスのふるい",
    summary="素数の倍数を順番に消して、範囲内の素数を残します。",
    time_complexity="O(n log log n)",
    create_steps=create_steps,
)
