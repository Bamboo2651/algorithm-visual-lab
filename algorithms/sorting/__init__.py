"""ソートアルゴリズムを1ファイルずつ管理する。"""

from .bubble import ALGORITHM as BUBBLE_SORT
from .cocktail import ALGORITHM as COCKTAIL_SORT
from .counting import ALGORITHM as COUNTING_SORT
from .heap import ALGORITHM as HEAP_SORT
from .insertion import ALGORITHM as INSERTION_SORT
from .merge import ALGORITHM as MERGE_SORT
from .quick import ALGORITHM as QUICK_SORT
from .selection import ALGORITHM as SELECTION_SORT
from .shell import ALGORITHM as SHELL_SORT


# GUIはこの順番でアルゴリズムを表示する。
ALL_ALGORITHMS = [
    BUBBLE_SORT,
    INSERTION_SORT,
    SELECTION_SORT,
    COCKTAIL_SORT,
    SHELL_SORT,
    MERGE_SORT,
    QUICK_SORT,
    HEAP_SORT,
    COUNTING_SORT,
]


__all__ = ["ALL_ALGORITHMS"]
