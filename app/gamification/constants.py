"""
app/gamification/constants.py — ゲーミフィケーション定数

ここを変更するだけでXP値・レベル閾値・バッジ定義を調整できる。
本番運用でバランスを調整する場合もここだけ変更すればよい。

TODO: Phase N+ これらを DB の設定テーブルに移し管理画面から調整可能にする
"""

# ── XP イベント名 ──────────────────────────────────────────────────
class XPEvent:
    LOGIN          = "login"           # 日次ログイン
    POST_PUBLIC    = "post_public"     # 公開投稿
    POST_PRIVATE   = "post_private"    # 非公開投稿
    COPY_RECEIVED  = "copy_received"   # 自分の投稿がコピーされた
    # TODO: Phase N+
    # LIKE_RECEIVED  = "like_received"
    # COMMENT_POSTED = "comment_posted"
    # INVITE_ACCEPTED = "invite_accepted"


# ── XP 付与量 (event_type → xp) ──────────────────────────────────
XP_VALUES: dict[str, int] = {
    XPEvent.LOGIN:         10,
    XPEvent.POST_PUBLIC:   50,
    XPEvent.POST_PRIVATE:  10,
    XPEvent.COPY_RECEIVED:  5,
}

# ── 日次1回上限のイベント ─────────────────────────────────────────
# 同じ日に何度発火しても1回分しか付与しない
DAILY_CAP_EVENTS: frozenset[str] = frozenset({XPEvent.LOGIN})


# ── レベル閾値定義 ────────────────────────────────────────────────
# (level, min_xp, title) の昇順リスト
# レベルは XP に基づいてリアルタイム計算される (User.level はキャッシュ)
LEVEL_THRESHOLDS: list[tuple[int, int, str]] = [
    (1,    0,    "見習い副業家"),
    (2,    100,  "副業スターター"),
    (3,    300,  "副業チャレンジャー"),
    (4,    600,  "副業ランナー"),
    (5,   1000,  "副業プロ"),
    (6,   1500,  "副業エキスパート"),
    (7,   2200,  "副業マスター"),
    (8,   3000,  "副業達人"),
    (9,   4000,  "副業レジェンド"),
    (10,  5500,  "副業神"),
]

MAX_LEVEL = LEVEL_THRESHOLDS[-1][0]


# ── バッジ定義 ────────────────────────────────────────────────────
# key → {name, icon, description}
BADGE_DEFINITIONS: dict[str, dict] = {
    "first_post": {
        "name":        "初投稿",
        "icon":        "📝",
        "description": "初めて広場にプロンプトを公開投稿した",
    },
    "level_2": {
        "name":        "副業スターター",
        "icon":        "⭐",
        "description": "レベル2に到達した",
    },
    "level_5": {
        "name":        "副業プロ",
        "icon":        "🏆",
        "description": "レベル5に到達した",
    },
    "level_10": {
        "name":        "副業神",
        "icon":        "👑",
        "description": "レベル10に到達した",
    },
    # TODO: Phase N+ 実装予定バッジ
    # "shared_10":    投稿が合計10回コピーされた (use_count 集計が必要)
    # "regular":      7日間連続ログイン (streak tracking が必要)
    # "invite_3":     3人を招待した
    # "level_3":      レベル3到達
    # "level_7":      レベル7到達
}

# レベル到達バッジのマッピング (level → badge_key)
LEVEL_BADGE_MAP: dict[int, str] = {2: "level_2", 5: "level_5", 10: "level_10"}
