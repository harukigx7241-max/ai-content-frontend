"""
app/gamification/xp_service.py — XP 計算・レベル算出 (DB を触らない純粋関数)

責務:
  - xp_for_level(n)  : レベル n に必要な累積 XP
  - calc_level(xp)   : XP からレベルを計算
  - get_level_info() : レベル情報タプルを返す
  - get_title()      : 称号を返す
  - get_benefits()   : レベル別特典を返す

レベル式:
  レベル k → k+1 の必要 XP = 50 + (k-1)^2 × 15
  累積 XP for level n     = sum_{k=1}^{n-1} [50 + (k-1)^2 × 15]
"""
from typing import Optional

from app.gamification.constants import LEVEL_BENEFITS, LEVEL_TITLES, MAX_LEVEL


def xp_for_level(n: int) -> int:
    """レベル n に到達するための累積 XP (レベル1 = 0)。"""
    if n <= 1:
        return 0
    return sum(50 + (k - 1) ** 2 * 15 for k in range(1, n))


def calc_level(xp: int) -> int:
    """XP からレベルを計算する。MAX_LEVEL を上限とする。"""
    level = 1
    while level < MAX_LEVEL and xp >= xp_for_level(level + 1):
        level += 1
    return level


def get_level_info(level: int) -> tuple[int, Optional[int], str, Optional[int]]:
    """
    Returns: (xp_at_current_level, xp_at_next_level_or_none, title, next_level_or_none)
    """
    current_min = xp_for_level(level)
    next_level  = level + 1 if level < MAX_LEVEL else None
    next_min    = xp_for_level(next_level) if next_level else None
    title       = get_title(level)
    return current_min, next_min, title, next_level


def get_title(level: int) -> str:
    """レベルに対応する称号を返す。LEVEL_TITLES の直前エントリを引き継ぐ。"""
    title = LEVEL_TITLES[0][1]  # フォールバック
    for min_lv, t in LEVEL_TITLES:
        if level >= min_lv:
            title = t
        else:
            break
    return title


def get_benefits(level: int) -> dict:
    """
    そのレベルで適用される特典を返す。
    LEVEL_BENEFITS の中でレベル以下の最大閾値エントリを使用。
    """
    result = LEVEL_BENEFITS[1]
    for threshold_level, benefits in sorted(LEVEL_BENEFITS.items()):
        if level >= threshold_level:
            result = benefits
        else:
            break
    return result
