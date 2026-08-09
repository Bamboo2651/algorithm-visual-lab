"""素数探索アルゴリズム。"""

from .sieve import ALGORITHM as SIEVE
from .trial_division import ALGORITHM as TRIAL_DIVISION


ALL_ALGORITHMS = [
    TRIAL_DIVISION,
    SIEVE,
]


__all__ = ["ALL_ALGORITHMS"]
