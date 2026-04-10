"""
app/gamification/constants.py — ゲーミフィケーション定数

ここを変更するだけでXP値・レベル式・称号・バッジ定義を調整できる。
本番運用でバランスを調整する場合もここだけ変更すればよい。

レベル式:
  レベル k → k+1 に必要な XP = 50 + (k-1)^2 × 15
  累積 XP (レベル n の閾値) = sum_{k=1}^{n-1} [50 + (k-1)^2 × 15]
  例: Lv2=50, Lv3=115, Lv4=225, Lv5=410, Lv10≒3510

TODO: Phase N+ これらを DB の設定テーブルに移し管理画面から調整可能にする
"""

# ── XP イベント名 ──────────────────────────────────────────────────
class XPEvent:
    LOGIN             = "login"             # 日次ログイン
    POST_PUBLIC       = "post_public"       # 公開投稿
    POST_PRIVATE      = "post_private"      # 非公開投稿
    COPY_RECEIVED     = "copy_received"     # 自分の投稿がコピーされた (後方互換)
    GENERATE          = "generate"          # プロンプト生成 (受け皿: Phase N+ 実装)
    POST_LIKED        = "post_liked"        # 投稿にいいねされた (受け皿: Phase N+)
    POST_SAVED        = "post_saved"        # 投稿を保存された (受け皿: Phase N+)
    POST_USED         = "post_used"         # 投稿が使用された (受け皿: Phase N+)
    COMMENT_RECEIVED  = "comment_received"  # コメントをもらった (受け皿: Phase N+)


# ── XP 付与量 (event_type → xp) ──────────────────────────────────
XP_VALUES: dict[str, int] = {
    XPEvent.LOGIN:            10,
    XPEvent.POST_PUBLIC:      50,
    XPEvent.POST_PRIVATE:     10,
    XPEvent.COPY_RECEIVED:     5,
    XPEvent.GENERATE:          5,
    XPEvent.POST_LIKED:       10,
    XPEvent.POST_SAVED:       10,
    XPEvent.POST_USED:        15,
    XPEvent.COMMENT_RECEIVED:  5,
}

# ── 日次1回上限のイベント ─────────────────────────────────────────
# 同じ日に何度発火しても1回分しか付与しない
DAILY_CAP_EVENTS: frozenset[str] = frozenset({XPEvent.LOGIN})

# ── イベント種別 → 関連エンティティ種別マッピング ──────────────────
# XpEvent.related_entity_type の自動設定に使用
ENTITY_TYPE_BY_EVENT: dict[str, str | None] = {
    XPEvent.LOGIN:            None,
    XPEvent.GENERATE:         "generate",
    XPEvent.POST_PUBLIC:      "post",
    XPEvent.POST_PRIVATE:     "post",
    XPEvent.COPY_RECEIVED:    "post",
    XPEvent.POST_LIKED:       "post",
    XPEvent.POST_SAVED:       "post",
    XPEvent.POST_USED:        "post",
    XPEvent.COMMENT_RECEIVED: "post",
}

# ── レベル上限 ────────────────────────────────────────────────────
MAX_LEVEL = 99  # 実用上の上限

# ── 称号テーブル (min_level, title) 昇順 ─────────────────────────
# 間のレベルは直前の称号を引き継ぐ
# 例: Lv1〜4 は「見習い」、Lv5〜9 は「研究員」
LEVEL_TITLES: list[tuple[int, str]] = [
    (1,  "見習い"),
    (5,  "研究員"),
    (10, "職人"),
    (20, "マスター"),
    (30, "レジェンド"),
]

# ── レベル別特典 (threshold_level → benefits) ────────────────────
# そのレベル以上に適用される特典。ユーザーのレベルに対応する最大閾値を使用。
# daily_gen_limit / post_limit: -1 = 無制限
LEVEL_BENEFITS: dict[int, dict] = {
    1:  {"daily_gen_limit": 5,    "post_limit": 10,   "invite_codes": 0},
    5:  {"daily_gen_limit": 20,   "post_limit": 50,   "invite_codes": 1},
    10: {"daily_gen_limit": 50,   "post_limit": 200,  "invite_codes": 3},
    20: {"daily_gen_limit": 100,  "post_limit": 1000, "invite_codes": 10},
    30: {"daily_gen_limit": -1,   "post_limit": -1,   "invite_codes": 30},
}

# ── バッジ定義 ────────────────────────────────────────────────────
BADGE_DEFINITIONS: dict[str, dict] = {
    "first_post": {
        "name":        "初投稿",
        "icon":        "📝",
        "description": "初めて広場にプロンプトを公開投稿した",
    },
    "gen_100": {
        "name":        "100回生成",
        "icon":        "⚡",
        "description": "プロンプトを100回生成した",
    },
    "first_liked": {
        "name":        "初いいね獲得",
        "icon":        "❤️",
        "description": "初めて投稿にいいねをもらった",
    },
    "first_saved": {
        "name":        "初保存獲得",
        "icon":        "🔖",
        "description": "初めて投稿を保存してもらった",
    },
    "first_used": {
        "name":        "初使用達成",
        "icon":        "🚀",
        "description": "初めて投稿を使用されたと判定された",
    },
    # TODO: Phase N+ 実装予定バッジ
    # "streak_7":   7日間連続ログイン (streak tracking が必要)
    # "shared_10":  投稿が合計10回コピーされた (use_count 集計が必要)
    # "invite_3":   3人を招待した
}
