"""
app/schemas/user.py — 一般ユーザー向け Pydantic モデル

認証系 (login/register/password) は app/schemas/auth.py に残す。
ここはプロフィール編集・利用状況など「ログイン後の自己操作」を扱う。
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    """
    プロフィール更新リクエスト。
    sns_platform / sns_handle はログイン ID のため変更不可 — このスキーマには含めない。
    TODO: Phase N+ SNS アカウント変更フロー (確認ステップ付き) を別エンドポイントで実装
    """
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    profile_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=500)
    # profile_url / bio に空文字 "" を送ると削除する
    # None を送った場合は変更しない (PATCH セマンティクス)


class UserStatsResponse(BaseModel):
    """
    ユーザー自身が見る利用状況サマリー。
    DB から取得可能な値のみを返す。生成回数はフロントの localStorage から補完する。

    TODO: Phase N+ generation_log 実装後に generation_count を実値に置き換える
    TODO: Phase N+ favorite_count も generation_log から集計する
    """
    user_id: int
    created_at: datetime
    last_login_at: Optional[datetime]
    # 将来フィールド (Phase N+)
    # generation_count: int  # TODO
    # favorite_count: int    # TODO
    # invite_count: int      # TODO
    # achievement_count: int # TODO
