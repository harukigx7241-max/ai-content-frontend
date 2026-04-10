"""
app/main.py
FastAPI アプリケーションのエントリポイント。
ここは薄く保つ: アプリ生成・ミドルウェア登録・ルーター include のみ。
重い処理は routers / prompts / core に委譲する。
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import general_exception_handler, validation_exception_handler
from app.core.maintenance import maintenance_middleware
from app.routers import note, cw, fortune, sns, project, remix, system, enhance

# ── アプリ生成 ──────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    # TODO: Phase 2 で管理画面向け docs の認証を追加する
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── 静的ファイル ──────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── ミドルウェア ──────────────────────────────────────────────────────
# メンテナンスモード (ENABLE_MAINTENANCE_MODE=true で API を 503 に)
app.middleware("http")(maintenance_middleware)

# TODO: Phase 1 で allowed_origins を設定から読むようにする
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 例外ハンドラ ──────────────────────────────────────────────────────
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ── ルーター ──────────────────────────────────────────────────────────
app.include_router(system.router)   # /, /health, /api/system/config
app.include_router(note.router)     # /api/note/*
app.include_router(cw.router)       # /api/cw/*
app.include_router(fortune.router)  # /api/fortune/*
app.include_router(sns.router)      # /api/sns/*
app.include_router(project.router)  # /api/project/*
app.include_router(remix.router)    # /api/remix
app.include_router(enhance.router)  # /api/enhance/* (Phase 1)

# ── Phase 2: 認証システム (ENABLE_AUTH_SYSTEM=false で即時無効化可能) ──
if settings.ENABLE_AUTH_SYSTEM:
    os.makedirs("data", exist_ok=True)

    from app.db.base import Base
    from app.db.session import engine
    from app.db import models as _db_models  # noqa: F401 — User モデルを Base.metadata に登録

    Base.metadata.create_all(bind=engine)

    # Phase 4 delta: bio カラムが無い旧 DB へのオンライン追加
    from sqlalchemy import text as _sql_text
    with engine.connect() as _conn:
        try:
            _conn.execute(_sql_text("ALTER TABLE users ADD COLUMN bio TEXT"))
            _conn.commit()
        except Exception:
            pass  # すでに存在する場合は無視

    # 起動時に DB のシステム設定を runtime_config に読み込む
    from app.core import runtime_config
    from app.db.session import SessionLocal
    with SessionLocal() as _startup_db:
        runtime_config.load_from_db(_startup_db)

    from app.auth.router import router as auth_router
    from app.admin.router import router as admin_router
    from app.user.router import router as user_router
    from app.routers.pages import router as pages_router

    app.include_router(auth_router)   # /api/auth/*
    app.include_router(admin_router)  # /api/admin/*
    app.include_router(user_router)   # /api/user/*  (Phase 4)
    app.include_router(pages_router)  # /login, /register, /mypage, /admin

# TODO: Phase 4 - app.include_router(community.router)
# TODO: Phase 4 - app.include_router(gamification.router)
# TODO: Phase 5 - app.include_router(invite.router)
