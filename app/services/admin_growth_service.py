"""
app/services/admin_growth_service.py
管理者専用集客工房サービス (Phase 17)

11種の集客支援ツールを統括するオーケストレーターサービス。
初期は admin/headquarters 専用。将来的に member_paid/member_master へ段階的解放。

ツール一覧:
  campaign_forge      — キャンペーン工房 (SNS告知文生成)
  note_promotion      — note販促ビルダー
  auto_research       — リサーチ下書き自動生成
  image_campaign      — 画像キャンペーンビルダー
  multi_channel_pack  — マルチチャンネル記事パック
  launch_pack         — ローンチパックビルダー
  promo_calendar      — 販促カレンダー生成
  hook_library        — フック文ライブラリ
  variation_generator — バリエーション生成
  promo_score         — 販促スコアリング
  scribe_campaign     — ギルド書記キャンペーンモード
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.base import BaseService, ServiceResult


# ─────────────────────────────────────────────────────────────────────────────
# GrowthToolDef
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GrowthToolDef:
    """集客工房ツール定義。管理 UI で使うメタデータを保持する。"""
    tool_id: str
    label: str
    icon: str
    description: str
    category: str           # promotion / content / image / calendar / analysis
    future_unlock: str      # 将来解放予定ロール: member_paid | member_master | admin_only
    inputs: tuple[str, ...] # UI フォームが必要とするフィールド名
    sort_order: int = 0

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "label": self.label,
            "icon": self.icon,
            "description": self.description,
            "category": self.category,
            "future_unlock": self.future_unlock,
            "inputs": list(self.inputs),
            "sort_order": self.sort_order,
        }


# ─────────────────────────────────────────────────────────────────────────────
# GROWTH_TOOLS — 11 ツール定義
# ─────────────────────────────────────────────────────────────────────────────

GROWTH_TOOLS: dict[str, GrowthToolDef] = {
    "campaign_forge": GrowthToolDef(
        tool_id="campaign_forge",
        label="キャンペーン工房",
        icon="⚔",
        description="SNS告知文・キャンペーン文のプロンプト生成",
        category="promotion",
        future_unlock="member_paid",
        inputs=("title", "target", "value", "price"),
        sort_order=1,
    ),
    "note_promotion": GrowthToolDef(
        tool_id="note_promotion",
        label="note販促ビルダー",
        icon="📝",
        description="note記事の集客プランプロンプト生成",
        category="promotion",
        future_unlock="member_paid",
        inputs=("product_name", "platform", "price", "target", "strengths"),
        sort_order=2,
    ),
    "auto_research": GrowthToolDef(
        tool_id="auto_research",
        label="リサーチ下書き生成",
        icon="🔍",
        description="note記事の下書き骨組みを自動生成",
        category="content",
        future_unlock="member_paid",
        inputs=("theme", "target", "tone"),
        sort_order=3,
    ),
    "image_campaign": GrowthToolDef(
        tool_id="image_campaign",
        label="画像キャンペーンビルダー",
        icon="🖼",
        description="SNS告知用・サムネイル向け画像プロンプト生成",
        category="image",
        future_unlock="member_paid",
        inputs=("theme", "image_type", "style"),
        sort_order=4,
    ),
    "multi_channel_pack": GrowthToolDef(
        tool_id="multi_channel_pack",
        label="マルチチャンネル記事パック",
        icon="📡",
        description="1記事を5チャンネル向けにアレンジするプロンプト生成",
        category="content",
        future_unlock="member_paid",
        inputs=("article_title", "key_points", "target_audience"),
        sort_order=5,
    ),
    "launch_pack": GrowthToolDef(
        tool_id="launch_pack",
        label="ローンチパックビルダー",
        icon="🚀",
        description="商品ローンチに必要な7素材のプロンプトを一括生成",
        category="promotion",
        future_unlock="member_paid",
        inputs=("product_name", "price", "launch_date", "target", "unique_value"),
        sort_order=6,
    ),
    "promo_calendar": GrowthToolDef(
        tool_id="promo_calendar",
        label="販促カレンダー生成",
        icon="📅",
        description="30日間の販促スケジュールプロンプトを自動生成",
        category="calendar",
        future_unlock="member_paid",
        inputs=("product_name", "start_date", "platform"),
        sort_order=7,
    ),
    "hook_library": GrowthToolDef(
        tool_id="hook_library",
        label="フック文ライブラリ",
        icon="🎣",
        description="読者を引き込む冒頭フック文を10スタイルで生成",
        category="content",
        future_unlock="member_paid",
        inputs=("theme", "audience", "tone"),
        sort_order=8,
    ),
    "variation_generator": GrowthToolDef(
        tool_id="variation_generator",
        label="バリエーション生成",
        icon="🔁",
        description="既存コンテンツを3トーン (感情/論理/物語) でリライト",
        category="content",
        future_unlock="member_paid",
        inputs=("original_content", "variation_style"),
        sort_order=9,
    ),
    "promo_score": GrowthToolDef(
        tool_id="promo_score",
        label="販促スコアリング",
        icon="📊",
        description="販促プランを5軸で採点・改善提案を生成",
        category="analysis",
        future_unlock="member_master",
        inputs=("promotion_plan", "target_platform"),
        sort_order=10,
    ),
    "scribe_campaign": GrowthToolDef(
        tool_id="scribe_campaign",
        label="ギルド書記キャンペーンモード",
        icon="✒",
        description="ギルド広場向けキャンペーン投稿文を生成",
        category="promotion",
        future_unlock="member_paid",
        inputs=("campaign_theme", "platform", "point1", "point2"),
        sort_order=11,
    ),
}

# カテゴリの表示名マップ
CATEGORY_LABELS: dict[str, str] = {
    "promotion": "販促・告知",
    "content": "コンテンツ生成",
    "image": "画像プロンプト",
    "calendar": "スケジュール",
    "analysis": "分析・スコアリング",
}


# ─────────────────────────────────────────────────────────────────────────────
# 新ツール用テンプレート (FREE tier)
# ─────────────────────────────────────────────────────────────────────────────

_MULTI_CHANNEL_TEMPLATE = """\
あなたはコンテンツマーケティング戦略家であり、マルチプラットフォーム展開のプロです。
以下の記事を5つのチャンネルに最適化してリパーパスしてください。

【記事タイトル】{article_title}
【主要ポイント】{key_points}
【ターゲット読者】{target_audience}

以下の5チャンネルそれぞれに最適化した展開版を作成してください：

1. **X (Twitter)** — 280文字以内のスレッド形式 (3〜5投稿)
   - 最初の投稿でインパクトのあるフックを入れる
   - ハッシュタグ3〜5個を最後に追加

2. **Instagram** — カルーセル投稿 (5〜7枚)
   - 各スライドのタイトルと本文を作成
   - ビジュアルイメージの指示も含める

3. **note記事** — 無料公開記事として再構成 (2,000字)
   - 元記事の有料部分は「詳しくは本編で」として誘導

4. **メルマガ / LINE** — 短文通知 (200文字以内)
   - 緊急性・限定感を持たせた文章

5. **YouTube / ショート動画** — 台本の骨格
   - オープニング (15秒) → 本編 (1分) → CTA (15秒) の構成

各チャンネルで最大限の効果を出せるよう、それぞれのプラットフォームの文化・特性に合わせてください。
"""

_LAUNCH_PACK_TEMPLATE = """\
あなたはデジタルコンテンツ販売で累計1億円以上を達成したローンチ戦略家です。
以下の商品のローンチパック素材を一括生成してください。

【商品名】{product_name}
【価格】{price}円
【ローンチ日】{launch_date}
【ターゲット】{target}
【独自の価値・差別化点】{unique_value}

以下の7素材を全て作成してください：

1. **ランディングページ キャッチコピー**
   - メインキャッチ1本 + サブキャッチ2本
   - 「〇〇で悩む△△さんへ」形式

2. **先行告知文 (X・SNS用)**
   - 3日前・1日前・当日の3段階告知文

3. **販売開始メール / DM**
   - 件名 + 本文 (300字)、緊急性と希少性を入れる

4. **FAQ (よくある質問5問)**
   - 購入不安を先回りして解消

5. **お客様の声テンプレート**
   - 購入後にお願いするレビュー依頼文

6. **アフィリエイター向け案内文**
   - 紹介者が使いやすい紹介文テンプレート

7. **ローンチ後フォローメール**
   - 購入者への初回フォロー (24時間以内)

各素材にはそのまま使えるテンプレート文章と、カスタマイズポイントの注釈を付けてください。
"""

_PROMO_CALENDAR_TEMPLATE = """\
あなたはSNSマーケティングと販促計画の専門家です。
以下の商品の30日間販促カレンダーを作成してください。

【商品名】{product_name}
【販促開始日】{start_date}
【主要プラットフォーム】{platform}

30日間のデイリー販促スケジュールを以下のフェーズ構成で作成してください：

【フェーズ1: 認知拡大 (Day 1〜7)】
- 商品の存在を知ってもらう段階
- 各日の投稿テーマ + 代表的な投稿文1本

【フェーズ2: 興味喚起 (Day 8〜14)】
- 商品の価値・効果を伝える段階
- 実績・事例・ビフォーアフターを活用

【フェーズ3: 欲求促進 (Day 15〜21)】
- 購入したい気持ちを高める段階
- 特典・限定感・社会的証明を活用

【フェーズ4: 販売促進 (Day 22〜28)】
- 積極的にCTAを入れる段階、緊急性・希少性を演出

【フェーズ5: クロージング (Day 29〜30)】
- 「最後のチャンス」で背中を押す

毎週水曜・土曜は「エンゲージメント強化デー」として質問投稿を組み込むこと。
"""

_HOOK_LIBRARY_TEMPLATE = """\
あなたはフォロワー20万人超えのカリスマコピーライターです。
読者を一瞬で引き込む冒頭フック文を10スタイルで生成してください。

【テーマ】{theme}
【ターゲット読者】{audience}
【文章トーン】{tone}

以下の10スタイルで、各スタイル1〜2文のフック文を作成してください：

1. **衝撃の事実型** — 「実は〇〇だった」
2. **共感型** — 読者の悩みをそのまま言語化
3. **数字型** — 具体的な数字でリアリティを出す
4. **問いかけ型** — 読者に質問を投げかける
5. **逆説型** — 常識を覆す一言
6. **ストーリー型** — 「〇〇の日、私は...」
7. **緊急性型** — 「今すぐ読まないと損する」
8. **権威型** — 実績・経験を前面に出す
9. **好奇心型** — 「〇〇の秘密を明かします」
10. **ビフォーアフター型** — 「かつての私は〇〇だった。今は...」

各フック文には「なぜ効果的か」の一言解説も付けてください。
"""

_VARIATION_TEMPLATE = """\
あなたはコンテンツ最適化の専門家です。
以下のコンテンツを3つの異なるトーンでバリエーション展開してください。

【元のコンテンツ】
{original_content}

【バリエーションスタイル指示】{variation_style}

以下の3パターンでリライトしてください：

**バリエーション1: エモーショナル版**
- 感情に訴える表現を多用
- 共感・不安・希望を巧みに組み合わせる
- 読者の心を動かすことを最優先

**バリエーション2: ロジカル版**
- データ・事実・論理で説得
- 数字・比較・根拠を豊富に使用
- 理性的な読者に刺さる内容

**バリエーション3: ストーリー版**
- 物語形式でメッセージを伝える
- 主人公の変化・成長を描く
- 読者が自分事として感じやすい構成

各バリエーションの末尾に「使用シーン (どんな媒体・読者向きか)」の推薦を1行追加してください。
"""

_PROMO_SCORE_TEMPLATE = """\
あなたはデジタルマーケティングの専門アナリストです。
以下の販促プランを5軸で採点し、具体的な改善提案を提示してください。

【販促プラン概要】
{promotion_plan}

【対象プラットフォーム】{target_platform}

## 採点基準 (各20点満点、合計100点)

### 1. ターゲット明確度 (20点)
- ターゲット読者の具体性、ペルソナの深さ、メッセージとのマッチング
→ スコア: X / 20点、評価と改善点

### 2. 差別化・独自性 (20点)
- 競合との違い、USP (独自の強み) の訴求、オリジナリティ
→ スコア: X / 20点、評価と改善点

### 3. CTA・誘導設計 (20点)
- 行動喚起の強さ、購買導線の設計、緊急性・希少性の演出
→ スコア: X / 20点、評価と改善点

### 4. コンテンツ品質 (20点)
- 情報の充実度、読みやすさ・構成、信頼性の演出
→ スコア: X / 20点、評価と改善点

### 5. 継続性・拡散性 (20点)
- シェアされやすい設計、フォロー・登録への誘導、リピート施策
→ スコア: X / 20点、評価と改善点

## 総合スコア: X / 100点

## 優先改善アクション TOP3
1. (最重要)
2. (重要)
3. (推奨)

## 改善後の期待効果
上記の改善を実施した場合の転換率・売上への影響を見積もってください。
"""


# ─────────────────────────────────────────────────────────────────────────────
# AdminGrowthService
# ─────────────────────────────────────────────────────────────────────────────

class AdminGrowthService(BaseService):
    """
    管理者専用集客工房の統合オーケストレーターサービス。
    11種のツールを一元管理し、FREE tier テンプレートベース実装を提供。
    管理者認証はルーター層で担保するため FLAG_KEY は空 (常時有効)。
    """
    FLAG_KEY = ""

    def list_tools(self) -> ServiceResult:
        """全ツール定義の一覧を返す。"""
        tools = sorted(GROWTH_TOOLS.values(), key=lambda t: t.sort_order)
        categories = {
            cat: CATEGORY_LABELS.get(cat, cat)
            for cat in dict.fromkeys(t.category for t in tools)
        }
        return ServiceResult.free(
            content={
                "tools": [t.to_dict() for t in tools],
                "total": len(tools),
                "categories": categories,
            }
        )

    def run_tool(self, tool_id: str, params: dict[str, Any]) -> ServiceResult:
        """tool_id に対応するツールを実行して結果を返す。"""
        if tool_id not in GROWTH_TOOLS:
            return ServiceResult.free(
                content={"error": f"不明なツールID: {tool_id}"},
                hint="対応していないツールIDです",
            )
        dispatch = {
            "campaign_forge":      self._campaign_forge,
            "note_promotion":      self._note_promotion,
            "auto_research":       self._auto_research,
            "image_campaign":      self._image_campaign,
            "multi_channel_pack":  self._multi_channel_pack,
            "launch_pack":         self._launch_pack,
            "promo_calendar":      self._promo_calendar,
            "hook_library":        self._hook_library,
            "variation_generator": self._variation_generator,
            "promo_score":         self._promo_score,
            "scribe_campaign":     self._scribe_campaign,
        }
        handler = dispatch.get(tool_id)
        if handler is None:
            return ServiceResult.free(content={"error": "ハンドラーが未実装です"})
        return handler(**params)

    # ── 既存サービス委譲 ────────────────────────────────────────────

    def _campaign_forge(
        self,
        title: str = "",
        target: str = "",
        value: str = "",
        price: str = "0",
        **_: object,
    ) -> ServiceResult:
        from app.services.campaign_forge_service import campaign_forge_service
        return campaign_forge_service.build_prompt(
            "note_launch", title=title, target=target, value=value, price=price
        )

    def _note_promotion(
        self,
        product_name: str = "",
        platform: str = "note",
        price: str = "0",
        target: str = "",
        strengths: str = "",
        **_: object,
    ) -> ServiceResult:
        from app.services.promotion_planner_service import promotion_planner_service
        price_int = int(price) if str(price).isdigit() else 0
        return promotion_planner_service.build_plan(
            product_name=product_name,
            platform=platform,
            price=price_int,
            target=target,
            strengths=strengths,
        )

    def _auto_research(
        self,
        theme: str = "",
        target: str = "",
        tone: str = "です・ます調",
        **_: object,
    ) -> ServiceResult:
        from app.services.article_draft_service import article_draft_service
        return article_draft_service.generate_draft(theme=theme, target=target, tone=tone)

    def _image_campaign(
        self,
        theme: str = "",
        image_type: str = "social",
        style: str = "モダン・クリーン・プロフェッショナル",
        **_: object,
    ) -> ServiceResult:
        from app.services.image_prompt_service import ImagePromptService
        svc = ImagePromptService(theme=theme, image_type=image_type, style=style)
        return svc.build_as_result()

    def _scribe_campaign(
        self,
        campaign_theme: str = "",
        platform: str = "note",
        point1: str = "",
        point2: str = "",
        **_: object,
    ) -> ServiceResult:
        from app.services.guild_scribe_service import guild_scribe_service
        points = [
            point1 or "強力なフックで読者を引き込む",
            point2 or "具体的な数字と事例でリアリティを演出",
            "明確なCTAで購読・購入行動を促す",
        ]
        return guild_scribe_service.generate_post(
            title=f"【キャンペーン】{campaign_theme}",
            theme=campaign_theme,
            category=platform if platform in ("note", "cw", "fortune", "sns") else "default",
            points=points,
        )

    # ── 6つの新ツール (FREE tier テンプレートベース) ────────────────

    def _multi_channel_pack(
        self,
        article_title: str = "",
        key_points: str = "",
        target_audience: str = "",
        **_: object,
    ) -> ServiceResult:
        prompt = _MULTI_CHANNEL_TEMPLATE.format(
            article_title=article_title or "記事タイトル未入力",
            key_points=key_points or "キーポイント未入力",
            target_audience=target_audience or "副業・収入アップに関心があるすべての人",
        )
        return ServiceResult.free(
            content={"prompt": prompt, "tool_id": "multi_channel_pack"},
            hint="5チャンネル (X / Instagram / note / メルマガ / YouTube) 向けに展開するプロンプトです",
        )

    def _launch_pack(
        self,
        product_name: str = "",
        price: str = "0",
        launch_date: str = "",
        target: str = "",
        unique_value: str = "",
        **_: object,
    ) -> ServiceResult:
        prompt = _LAUNCH_PACK_TEMPLATE.format(
            product_name=product_name or "商品名未入力",
            price=price,
            launch_date=launch_date or "未定",
            target=target or "副業・収入アップを目指す方",
            unique_value=unique_value or "独自の視点と実体験に基づく内容",
        )
        return ServiceResult.free(
            content={"prompt": prompt, "tool_id": "launch_pack"},
            hint="ローンチに必要な7素材 (LP・告知文・メール・FAQ・レビュー依頼・アフィ案内・フォロー) のプロンプトです",
        )

    def _promo_calendar(
        self,
        product_name: str = "",
        start_date: str = "",
        platform: str = "X・Instagram",
        **_: object,
    ) -> ServiceResult:
        prompt = _PROMO_CALENDAR_TEMPLATE.format(
            product_name=product_name or "商品名未入力",
            start_date=start_date or "未定",
            platform=platform,
        )
        return ServiceResult.free(
            content={"prompt": prompt, "tool_id": "promo_calendar"},
            hint="5フェーズ30日間の販促スケジュールプロンプトです",
        )

    def _hook_library(
        self,
        theme: str = "",
        audience: str = "",
        tone: str = "です・ます調",
        **_: object,
    ) -> ServiceResult:
        prompt = _HOOK_LIBRARY_TEMPLATE.format(
            theme=theme or "副業・収入アップ",
            audience=audience or "20〜40代の会社員",
            tone=tone,
        )
        return ServiceResult.free(
            content={"prompt": prompt, "tool_id": "hook_library"},
            hint="10スタイルのフック文 + 解説を生成するプロンプトです",
        )

    def _variation_generator(
        self,
        original_content: str = "",
        variation_style: str = "標準",
        **_: object,
    ) -> ServiceResult:
        prompt = _VARIATION_TEMPLATE.format(
            original_content=original_content or "コンテンツを入力してください",
            variation_style=variation_style,
        )
        return ServiceResult.free(
            content={"prompt": prompt, "tool_id": "variation_generator"},
            hint="エモーショナル / ロジカル / ストーリーの3バリエーションを生成するプロンプトです",
        )

    def _promo_score(
        self,
        promotion_plan: str = "",
        target_platform: str = "note",
        **_: object,
    ) -> ServiceResult:
        prompt = _PROMO_SCORE_TEMPLATE.format(
            promotion_plan=promotion_plan or "販促プランを入力してください",
            target_platform=target_platform,
        )
        return ServiceResult.free(
            content={"prompt": prompt, "tool_id": "promo_score"},
            hint="5軸採点 (ターゲット・差別化・CTA・品質・拡散性) + 改善提案を生成するプロンプトです",
        )


# グローバルシングルトン
admin_growth_service = AdminGrowthService()
