"""数列を生成するアルゴリズム。"""

from .collatz import ALGORITHM as COLLATZ
from .recaman import ALGORITHM as RECAMAN


ALL_ALGORITHMS = [
    RECAMAN,
    COLLATZ,
]


__all__ = ["ALL_ALGORITHMS"]
