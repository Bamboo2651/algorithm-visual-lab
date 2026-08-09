"""素数探索アルゴリズムの結果を確認する。"""

import pytest

from algorithms.primes import ALL_ALGORITHMS
from algorithms.primes.common import PrimeRunner


EXPECTED_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


@pytest.mark.parametrize("algorithm", ALL_ALGORITHMS, ids=lambda item: item.key)
def test_prime_algorithm_finds_primes_up_to_30(algorithm) -> None:
    runner = PrimeRunner(algorithm, limit=30)

    for _ in range(10_000):
        if runner.done:
            break
        runner.step()

    assert runner.done
    assert runner.state.primes == EXPECTED_PRIMES

