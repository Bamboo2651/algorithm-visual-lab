"""試し割り法による素数探索。

2から上限までの各整数について、2から平方根まで順番に割る。
割り切れる数がなければ素数と判断する、最も理解しやすい方法。
"""

from collections.abc import Iterator

from .common import PrimeAlgorithm, PrimeState


def create_steps(state: PrimeState) -> Iterator[None]:
    for candidate in range(2, state.limit + 1):
        state.current = candidate
        is_prime = True

        for divisor in range(2, math_limit(candidate) + 1):
            state.divisor = divisor
            state.operations += 1
            state.message = f"{candidate} を {divisor} で割って確認"
            yield

            if candidate % divisor == 0:
                is_prime = False
                state.message = f"{divisor} で割り切れるため合成数"
                break

        state.results[candidate] = is_prime
        state.message = f"{candidate} は{'素数' if is_prime else '合成数'}"
        yield


def math_limit(number: int) -> int:
    """浮動小数点を使わず、平方根以下の最大整数を返す。"""

    divisor = 1
    while (divisor + 1) * (divisor + 1) <= number:
        divisor += 1
    return divisor


ALGORITHM = PrimeAlgorithm(
    key="trial_division",
    name="試し割り法",
    summary="各数を平方根まで順番に割り、約数があるか調べます。",
    time_complexity="およそ O(n√n)",
    create_steps=create_steps,
)
