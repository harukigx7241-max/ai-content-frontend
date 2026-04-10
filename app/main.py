"""
app/main.py
FastAPI アプリケーションのエントリポイント。
ここは薄く保つ: アプリ生成・ミドルウェア登録・ルーター include のみ。

重い初期化処理の委譲先:
  app/core/startup.py      — DB 初期化・マイグレーション・runtime_config 読み込み
  app/db/migrations.py     — カラムマイグレーション一覧とロジック
  app/routers/loader.py    — 機能フラグ別ルーター登録
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
    # TODO: Phase N+ 管理画面向け docs に認証を追加する
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── 静的ファイル ──────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── ミドルウェア ──────────────────────────────────────────────────────
# メンテナンスモード (ENABLE_MAINTENANCE_MODE=true で API を 503 に)
app.middleware("http")(maintenance_middleware)

# CORS: 開発時は BACKEND_CORS_ORIGINS 未設定で ["*"]、本番では環境変数で制限する
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 例外ハンドラ ──────────────────────────────────────────────────────
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ── コアルーター (常時有効) ─────────────────────────────────────────
app.include_router(system.router)   # /, /health, /api/system/config
app.include_router(note.router)     # /api/note/*
app.include_router(cw.router)       # /api/cw/*
app.include_router(fortune.router)  # /api/fortune/*
app.include_router(sns.router)      # /api/sns/*
app.include_router(project.router)  # /api/project/*
app.include_router(remix.router)    # /api/remix
app.include_router(enhance.router)  # /api/enhance/*

# ── 認証システム (ENABLE_AUTH_SYSTEM=false で全体を無効化可能) ────────
if settings.ENABLE_AUTH_SYSTEM:
    from app.core.startup import bootstrap_db
    from app.routers.loader import include_feature_routers

    bootstrap_db()
    include_feature_routers(app)
