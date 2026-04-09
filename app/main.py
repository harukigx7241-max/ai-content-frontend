"""
app/main.py
FastAPI アプリケーションのエントリポイント。
ここは薄く保つ: アプリ生成・ミドルウェア登録・ルーター include のみ。
重い処理は routers / prompts / core に委譲する。
"""
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

# TODO: Phase 1 - app.include_router(auth.router)
# TODO: Phase 2 - app.include_router(admin.router)
# TODO: Phase 3 - app.include_router(community.router)
# TODO: Phase 4 - app.include_router(gamification.router)
# TODO: Phase 5 - app.include_router(invite.router)
