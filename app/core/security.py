"""
app/core/security.py — パスワードハッシュ + JWT ユーティリティ
認証まわりの重い処理をここに集約し、router / service からは関数を呼ぶだけにする。

使用ライブラリ:
  bcrypt — パスワードハッシュ (cost=12)
  stdlib (hmac / hashlib / base64 / json) — HS256 JWT (外部依存なし)
"""
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from fastapi import HTTPException

from app.core.config import settings

# タイミング攻撃対策用ダミーハッシュ (モジュールロード時に1回だけ生成)
_DUMMY_HASH: bytes = _bcrypt.hashpw(b"_timing_attack_prevention_dummy_", _bcrypt.gensalt(rounds=12))

_ALGORITHM = "HS256"
_HEADER_B64 = base64.urlsafe_b64encode(
    json.dumps({"alg": _ALGORITHM, "typ": "JWT"}).encode()
).rstrip(b"=").decode()


# ── パスワード ──────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """パスワードを bcrypt でハッシュ化する (cost=12)。"""
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """パスワードを検証する。"""
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT (stdlib HS256) ─────────────────────────────────────────────

def _b64enc(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64dec(s: str) -> bytes:
    # padding を補完
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def create_access_token(user_id: int, role: str) -> str:
    """アクセストークンを生成する。有効期限は settings.JWT_EXPIRE_DAYS 日。"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.JWT_EXPIRE_DAYS)).timestamp()),
    }
    payload_b64 = _b64enc(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{_HEADER_B64}.{payload_b64}"
    sig = hmac.new(
        settings.JWT_SECRET.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64enc(sig)}"


def decode_access_token(token: str) -> dict:
    """
    トークンをデコードして payload を返す。
    期限切れ・不正トークンは HTTPException(401) を raise する。
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(401, "認証トークンが無効です")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}"
    expected_sig = hmac.new(
        settings.JWT_SECRET.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()

    try:
        given_sig = _b64dec(sig_b64)
    except Exception:
        raise HTTPException(401, "認証トークンが無効です")

    if not hmac.compare_digest(expected_sig, given_sig):
        raise HTTPException(401, "認証トークンが無効です")

    try:
        payload = json.loads(_b64dec(payload_b64))
    except Exception:
        raise HTTPException(401, "認証トークンが無効です")

    if payload.get("exp", 0) < datetime.now(timezone.utc).timestamp():
        raise HTTPException(401, "セッションが期限切れです。再度ログインしてください")

    return payload


def timing_safe_verify(plain: str, hashed: str | None) -> bool:
    """
    ユーザーが存在しない場合もダミーハッシュで検証し、
    処理時間によるユーザー存在確認を防ぐ。
    """
    if hashed is None:
        _bcrypt.checkpw(plain.encode(), _DUMMY_HASH)
        return False
    return _bcrypt.checkpw(plain.encode(), hashed.encode())
