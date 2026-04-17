"""
app/services/subscription_service.py
サブスクリプション / プラン管理サービス — Phase 16

Tiers:
  FREE  — プラン情報の読み取り・ユーザープラン確認 (常時動作)
  API   — Stripe Checkout 作成・Webhook 処理 (STRIPE_SECRET_KEY 設定後)
  DISABLED — ENABLE_BILLING=false 時 (読み取りは常時可能)

プラン定義:
  free    → member_free  ロール相当
  paid    → member_paid  ロール相当 (月額 980円 / 年額 9,800円)
  master  → member_master ロール相当 (月額 2,480円 / 年額 24,800円)

設計方針:
  - プラン定義はコードに持つ (DB 不要)
  - ユーザーの現在プランは User.subscription_plan で管理
  - 課金接続前は全員 "free" として動作
  - Stripe 接続後: create_checkout_session() → Webhook → role 昇格
  - role は subscription_plan と独立して admin/HQ が直接変更可能
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.core.config import settings
from app.core.roles import RoleValue
from app.services.base import BaseService, ServiceMode, ServiceResult


# ─────────────────────────────────────────────────────────────────────────────
# Plan definitions
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PlanDef:
    plan_id: str          # "free" | "paid" | "master"
    label: str            # 日本語表示名
    icon: str
    role: str             # 対応する RoleValue
    price_monthly_jpy: int   # 月額 (free は 0)
    price_yearly_jpy: int    # 年額 (free は 0)
    tagline: str          # キャッチコピー
    color: str            # CSSカラーヒント ("blue" | "amber" | "gold")
    # 機能一覧 (UIに表示するもの)
    features_free: list[str] = field(default_factory=list)
    features_locked: list[str] = field(default_factory=list)   # このプランで解放
    # Stripe Price IDs (空 = 未設定)
    stripe_price_monthly: str = ""
    stripe_price_yearly: str = ""
    # ソート順
    sort_order: int = 0

    @property
    def is_paid(self) -> bool:
        return self.price_monthly_jpy > 0

    @property
    def yearly_discount_pct(self) -> int:
        if self.price_monthly_jpy == 0:
            return 0
        monthly_total = self.price_monthly_jpy * 12
        return round((1 - self.price_yearly_jpy / monthly_total) * 100)

    def to_dict(self, include_stripe: bool = False) -> dict:
        d = {
            "plan_id": self.plan_id,
            "label": self.label,
            "icon": self.icon,
            "role": self.role,
            "price_monthly_jpy": self.price_monthly_jpy,
            "price_yearly_jpy": self.price_yearly_jpy,
            "yearly_discount_pct": self.yearly_discount_pct,
            "tagline": self.tagline,
            "color": self.color,
            "features_free": self.features_free,
            "features_locked": self.features_locked,
            "sort_order": self.sort_order,
            "billing_enabled": settings.ENABLE_BILLING and bool(self.stripe_price_monthly),
        }
        if include_stripe:
            d["stripe_price_monthly"] = self.stripe_price_monthly
            d["stripe_price_yearly"] = self.stripe_price_yearly
        return d


PLANS: dict[str, PlanDef] = {
    "free": PlanDef(
        plan_id="free",
        label="フリープラン",
        icon="⚗",
        role=RoleValue.MEMBER_FREE,
        price_monthly_jpy=0,
        price_yearly_jpy=0,
        tagline="まずは無料で始めよう",
        color="blue",
        features_free=[
            "プロンプト鍛冶場 (全工房・無制限)",
            "テンプレートライブラリ閲覧",
            "テンプレート保存・リミックス",
            "プロンプト診断 (基本10項目)",
            "日本語品質チェック",
            "ギルド広場 閲覧・投稿",
            "XP・ランク・称号システム",
            "プロンプト履歴 (ブラウザ保存)",
        ],
        features_locked=[],
        sort_order=0,
    ),
    "paid": PlanDef(
        plan_id="paid",
        label="プロプラン",
        icon="⚔",
        role=RoleValue.MEMBER_PAID,
        price_monthly_jpy=980,
        price_yearly_jpy=9800,
        tagline="副業を本格化するプロの道具",
        color="amber",
        features_free=[
            "フリープランの全機能",
            "キャンペーン鍛冶場 (SNS告知・集客文)",
            "note販促ビルダー (LP・説明文最適化)",
            "リサーチ下書き自動生成",
            "画像プロンプト生成",
            "優先処理レーン (待ち時間短縮)",
            "プロンプト診断 詳細モード",
            "トレンド注入 (最新パターン参照)",
        ],
        features_locked=[
            "Workshop Master AI (上位モデル)",
            "一括生成 (複数プロンプト同時)",
        ],
        stripe_price_monthly=settings.STRIPE_PRICE_PAID_MONTHLY,
        stripe_price_yearly=settings.STRIPE_PRICE_PAID_YEARLY,
        sort_order=1,
    ),
    "master": PlanDef(
        plan_id="master",
        label="マスタープラン",
        icon="✦",
        role=RoleValue.MEMBER_MASTER,
        price_monthly_jpy=2480,
        price_yearly_jpy=24800,
        tagline="最上位の全機能 + 専属サポート",
        color="gold",
        features_free=[
            "プロプランの全機能",
            "Workshop Master AI (最高精度AI)",
            "一括生成 (複数プロンプト同時出力)",
            "優先レーン 最優先枠",
            "マスターバッジ (プロフィール表示)",
        ],
        features_locked=[],
        stripe_price_monthly=settings.STRIPE_PRICE_MASTER_MONTHLY,
        stripe_price_yearly=settings.STRIPE_PRICE_MASTER_YEARLY,
        sort_order=2,
    ),
}

# サブスクリプションプランからロールへのマッピング
PLAN_TO_ROLE: dict[str, str] = {
    "free":   RoleValue.MEMBER_FREE,
    "paid":   RoleValue.MEMBER_PAID,
    "master": RoleValue.MEMBER_MASTER,
}

# ロールからサブスクリプションプランへの逆引き
ROLE_TO_PLAN: dict[str, str] = {v: k for k, v in PLAN_TO_ROLE.items()}


# ─────────────────────────────────────────────────────────────────────────────
# アップグレードパス
# ─────────────────────────────────────────────────────────────────────────────

UPGRADE_PATHS: list[tuple[str, str]] = [
    ("free", "paid"),
    ("paid", "master"),
]


def get_upgrade_target(current_plan: str) -> Optional[str]:
    """現在のプランから次のアップグレード先プラン ID を返す。最高位なら None。"""
    for from_plan, to_plan in UPGRADE_PATHS:
        if from_plan == current_plan:
            return to_plan
    return None


def get_plan_for_role(role: str | None) -> str:
    """ロール文字列からプラン ID を返す。admin/HQ は "master" 相当。"""
    if role in (RoleValue.ADMIN, RoleValue.HEADQUARTERS):
        return "master"
    return ROLE_TO_PLAN.get(role or RoleValue.GUEST, "free")


# ─────────────────────────────────────────────────────────────────────────────
# SubscriptionService
# ─────────────────────────────────────────────────────────────────────────────

class SubscriptionService(BaseService):
    """
    サブスクリプション管理サービス。

    FREE モード: プラン情報の読み取り・ユーザープラン確認
    API モード:  Stripe Checkout セッション作成・Webhook 処理
    """

    FLAG_KEY = ""   # 常時有効 (読み取り)
    PREFER_API = False

    # ── プラン情報 ─────────────────────────────────────────────────

    def get_plans(self) -> ServiceResult:
        """全プラン定義を返す。"""
        plans = [p.to_dict() for p in sorted(PLANS.values(), key=lambda p: p.sort_order)]
        return ServiceResult.free(content={
            "plans": plans,
            "billing_enabled": settings.ENABLE_BILLING,
            "trial_days": settings.BILLING_TRIAL_DAYS,
        })

    def get_plan(self, plan_id: str) -> Optional[PlanDef]:
        """プラン ID から PlanDef を返す。"""
        return PLANS.get(plan_id)

    def get_user_plan_info(self, user) -> ServiceResult:
        """
        ユーザーの現在プラン情報を返す。
        user は User モデルインスタンス、または None (ゲスト)。
        """
        if user is None:
            plan_id = "free"
            role = RoleValue.GUEST
        else:
            plan_id = getattr(user, "subscription_plan", "free") or "free"
            role = getattr(user, "role", RoleValue.MEMBER_FREE)

        # admin / HQ は plan として "master" 扱い (課金不要)
        if role in (RoleValue.ADMIN, RoleValue.HEADQUARTERS):
            plan_id = "master"

        plan = PLANS.get(plan_id, PLANS["free"])
        upgrade_target_id = get_upgrade_target(plan_id)
        upgrade_plan = PLANS.get(upgrade_target_id) if upgrade_target_id else None

        expires_at = getattr(user, "subscription_expires_at", None) if user else None
        sub_status = getattr(user, "subscription_status", "active") if user else "active"

        return ServiceResult.free(content={
            "plan_id": plan_id,
            "plan": plan.to_dict(),
            "role": role,
            "subscription_status": sub_status,
            "subscription_expires_at": expires_at.isoformat() if expires_at else None,
            "upgrade_available": upgrade_plan is not None,
            "upgrade_plan": upgrade_plan.to_dict() if upgrade_plan else None,
            "billing_enabled": settings.ENABLE_BILLING,
        })

    # ── 課金操作 (API モード / Stripe 接続後) ─────────────────────

    def create_checkout_session(
        self,
        user_id: int,
        plan_id: str,
        billing_cycle: str = "monthly",
        success_url: str = "",
        cancel_url: str = "",
    ) -> ServiceResult:
        """
        Stripe Checkout セッションを作成する。

        TODO Phase 17+:
          import stripe
          stripe.api_key = settings.STRIPE_SECRET_KEY
          plan = PLANS.get(plan_id)
          price_id = plan.stripe_price_monthly if billing_cycle == "monthly" else plan.stripe_price_yearly
          session = stripe.checkout.Session.create(
              mode="subscription",
              payment_method_types=["card"],
              line_items=[{"price": price_id, "quantity": 1}],
              success_url=success_url,
              cancel_url=cancel_url,
              metadata={"user_id": str(user_id), "plan_id": plan_id},
              trial_period_days=settings.BILLING_TRIAL_DAYS or None,
          )
          return ServiceResult.api(content={"checkout_url": session.url, "session_id": session.id})
        """
        if not settings.ENABLE_BILLING or not settings.STRIPE_SECRET_KEY:
            return ServiceResult.free(content={
                "available": False,
                "message": "課金機能は現在準備中です。近日公開予定。",
                "plan_id": plan_id,
                "billing_cycle": billing_cycle,
            })
        return ServiceResult.not_implemented(ServiceMode.API)

    def handle_webhook(self, payload: bytes, signature: str) -> ServiceResult:
        """
        Stripe Webhook を処理する。

        TODO Phase 17+:
          import stripe
          event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
          if event.type == "checkout.session.completed":
              ...upgrade user role...
          elif event.type == "customer.subscription.deleted":
              ...downgrade user role...
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def cancel_subscription(self, user_id: int) -> ServiceResult:
        """
        サブスクリプションをキャンセルする。

        TODO Phase 17+: Stripe subscription cancel API
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_api(self, **_) -> ServiceResult:
        return ServiceResult.not_implemented(ServiceMode.API)


# グローバルシングルトン
subscription_service = SubscriptionService()
