import os, json, uuid, hmac, hashlib, secrets, asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List

import httpx
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ── Setup ─────────────────────────────────────────────────
app = FastAPI(title="AI Content Pro", version="74.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

for d in ["static/css", "static/js", "templates"]:
    os.makedirs(d, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

APP_VERSION = "74.0.0"
DATA_FILE   = "data.json"
CONFIG_FILE = "server_config.json"

# ── Data helpers ───────────────────────────────────────────
def load_config() -> Dict:
    if not os.path.exists(CONFIG_FILE):
        cfg = {"openai_api_key": "", "anthropic_api_key": "", "google_api_key": "",
               "admin_password": "admin1234",
               "secret_key": secrets.token_hex(32),
               "credit_per_generation": 1, "new_user_credits": 150, "invite_bonus_credits": 50}
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
        return cfg
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def load_data() -> Dict:
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "invite_codes": {}, "passphrases": {}, "notices": [], "sessions": {}}
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_user(u: Dict) -> Dict:
    return {k: v for k, v in u.items() if k != "password_hash"}

# ── Auth helpers ───────────────────────────────────────────
def hash_pw(pw: str) -> str:
    secret = load_config().get("secret_key", "default")
    return hmac.new(secret.encode(), pw.encode(), hashlib.sha256).hexdigest()

def create_session(uid: str) -> str:
    token = secrets.token_urlsafe(32)
    d = load_data()
    d["sessions"][token] = {"user_id": uid, "created_at": datetime.now().isoformat()}
    save_data(d)
    return token

def get_user(token: str) -> Optional[Dict]:
    d = load_data()
    s = d["sessions"].get(token)
    return d["users"].get(s["user_id"]) if s else None

def auth(authorization: str = Header(None)) -> Dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "認証が必要です")
    u = get_user(authorization[7:])
    if not u:
        raise HTTPException(401, "無効なトークンです")
    if u.get("status") == "frozen":
        raise HTTPException(403, "アカウントが凍結されています")
    return u

def admin_auth(authorization: str = Header(None)) -> Dict:
    u = auth(authorization)
    if not u.get("is_admin"):
        raise HTTPException(403, "管理者権限が必要です")
    return u

# ── AI callers ─────────────────────────────────────────────
async def call_openai(msgs: List[Dict], key: str, model: str) -> str:
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post("https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": msgs, "max_tokens": 4000})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

async def call_anthropic(msgs: List[Dict], key: str, model: str) -> str:
    system = next((m["content"] for m in msgs if m["role"] == "system"), None)
    user_msgs = [m for m in msgs if m["role"] != "system"]
    payload: Dict[str, Any] = {"model": model, "max_tokens": 4000, "messages": user_msgs}
    if system:
        payload["system"] = system
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"},
            json=payload)
        r.raise_for_status()
        return r.json()["content"][0]["text"]

async def call_google(msgs: List[Dict], key: str, model: str) -> str:
    system = next((m["content"] for m in msgs if m["role"] == "system"), None)
    contents = [{"role": "user" if m["role"] == "user" else "model",
                 "parts": [{"text": m["content"]}]}
                for m in msgs if m["role"] != "system"]
    payload: Dict[str, Any] = {"contents": contents}
    if system:
        payload["system_instruction"] = {"parts": [{"text": system}]}
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
            json=payload)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

async def generate_with_fallback(msgs: List[Dict], user: Dict, model_type: str = "free"):
    cfg = load_config()
    uk = user.get("api_keys", {})
    preferred = user.get("settings", {}).get("preferred_ai", "openai")
    FREE = {"openai": "gpt-4o-mini", "anthropic": "claude-haiku-4-5-20251001", "google": "gemini-1.5-flash"}
    PRO  = {"openai": "gpt-4o",      "anthropic": "claude-sonnet-4-6",         "google": "gemini-1.5-pro"}
    mods = PRO if model_type == "pro" else FREE
    callers = {"openai": call_openai, "anthropic": call_anthropic, "google": call_google}

    order = [preferred] + [p for p in ["openai", "anthropic", "google"] if p != preferred]
    providers = []
    for name in order:
        ukey = uk.get(name, "")
        skey = cfg.get(f"{name}_api_key", "")
        if ukey:
            providers.append((name, ukey, mods[name], True))
        elif skey:
            providers.append((name, skey, mods[name], False))

    if not providers:
        raise HTTPException(503, "APIキーが未設定です。個人設定からAPIキーを登録するか、管理者にクレジット付与を依頼してください。")

    last_err = ""
    for name, key, model, is_byok in providers:
        try:
            result = await callers[name](msgs, key, model)
            return result, is_byok
        except Exception as e:
            last_err = str(e)
    raise HTTPException(503, f"全AIプロバイダーでエラー: {last_err}")

# ── Routes ─────────────────────────────────────────────────
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "version": APP_VERSION})

# Auth
class RegisterReq(BaseModel):
    email: str; password: str; username: str; invite_code: str

class LoginReq(BaseModel):
    email: str; password: str

@app.post("/api/auth/register")
async def register(req: RegisterReq):
    d = load_data(); cfg = load_config()
    code = req.invite_code.strip().upper()
    inv = d["invite_codes"].get(code)
    if not inv or inv.get("used_by"):
        raise HTTPException(400, "無効または使用済みの招待コードです")
    if any(u["email"] == req.email for u in d["users"].values()):
        raise HTTPException(400, "このメールアドレスは既に登録されています")
    uid = str(uuid.uuid4())
    user = {
        "id": uid, "email": req.email, "username": req.username,
        "password_hash": hash_pw(req.password), "status": "active",
        "credits": cfg.get("new_user_credits", 150),
        "api_keys": {"openai": "", "anthropic": "", "google": ""},
        "settings": {"persona": {"base_personality": "friendly", "first_person": "私", "custom_style": ""},
                     "default_model": "free", "preferred_ai": "openai"},
        "total_generations": 0, "created_at": datetime.now().isoformat(),
        "last_login": None, "is_admin": False,
    }
    d["users"][uid] = user
    d["invite_codes"][code]["used_by"] = uid
    d["invite_codes"][code]["used_at"] = datetime.now().isoformat()
    inviter_id = inv.get("created_by_user_id")
    if inviter_id and inviter_id in d["users"]:
        d["users"][inviter_id]["credits"] += cfg.get("invite_bonus_credits", 50)
    save_data(d)
    return {"token": create_session(uid), "user": clean_user(user)}

@app.post("/api/auth/login")
async def login(req: LoginReq):
    d = load_data()
    user = next((u for u in d["users"].values() if u["email"] == req.email), None)
    if not user or user["password_hash"] != hash_pw(req.password):
        raise HTTPException(401, "メールアドレスまたはパスワードが間違っています")
    if user.get("status") == "frozen":
        raise HTTPException(403, "アカウントが凍結されています")
    d["users"][user["id"]]["last_login"] = datetime.now().isoformat()
    save_data(d)
    return {"token": create_session(user["id"]), "user": clean_user(user)}

@app.post("/api/auth/logout")
async def logout(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        d = load_data()
        d["sessions"].pop(authorization[7:], None)
        save_data(d)
    return {"ok": True}

@app.get("/api/user/me")
async def me(authorization: str = Header(None)):
    return clean_user(auth(authorization))

@app.put("/api/user/settings")
async def update_settings(body: Dict[str, Any], authorization: str = Header(None)):
    user = auth(authorization)
    d = load_data(); u = d["users"][user["id"]]
    for field in ["settings", "api_keys", "username"]:
        if field in body:
            if isinstance(body[field], dict):
                u[field].update(body[field])
            else:
                u[field] = body[field]
    save_data(d)
    return clean_user(u)

# Generate
class GenerateReq(BaseModel):
    tool_id: str
    messages: List[Dict[str, str]]
    ab_test: bool = False
    model_type: str = "free"

@app.post("/api/generate")
async def generate(req: GenerateReq, authorization: str = Header(None)):
    user = auth(authorization)
    d = load_data(); cfg = load_config()
    has_byok = any(user.get("api_keys", {}).get(k) for k in ["openai", "anthropic", "google"])
    if not has_byok and user.get("credits", 0) <= 0:
        raise HTTPException(402, "クレジットが不足しています。APIキーを登録するか管理者にお問い合わせください。")

    msgs = list(req.messages)
    custom = user.get("settings", {}).get("persona", {}).get("custom_style", "")
    if custom:
        for m in msgs:
            if m["role"] == "system":
                m["content"] = custom + "\n\n" + m["content"]; break

    if req.ab_test:
        for m in msgs:
            if m["role"] == "user":
                m["content"] += "\n\n【重要】全く異なる2つの切り口で「バリエーションA」「バリエーションB」として2パターン出力してください。"
                break

    if req.model_type == "pro":
        for m in msgs:
            if m["role"] == "system":
                m["content"] += "\n\n最新トレンドや統計情報が必要な場合は、必ずWeb検索を活用して最新情報で回答してください。"
                break

    result, is_byok = await generate_with_fallback(msgs, user, req.model_type)
    if not is_byok:
        d["users"][user["id"]]["credits"] -= cfg.get("credit_per_generation", 1)
    d["users"][user["id"]]["total_generations"] = d["users"][user["id"]].get("total_generations", 0) + 1
    save_data(d)
    return {"result": result, "credits": d["users"][user["id"]]["credits"], "used_byok": is_byok}

class MagicReq(BaseModel):
    tool_id: str; tool_name: str
    partial_vals: Dict[str, Any] = {}
    model_type: str = "free"

@app.post("/api/magic_generate")
async def magic_generate(req: MagicReq, authorization: str = Header(None)):
    user = auth(authorization)
    d = load_data(); cfg = load_config()
    has_byok = any(user.get("api_keys", {}).get(k) for k in ["openai", "anthropic", "google"])
    if not has_byok and user.get("credits", 0) <= 0:
        raise HTTPException(402, "クレジットが不足しています")

    search_ctx = ""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text("日本 SNS コンテンツ トレンド 副業 2026", max_results=5))
            search_ctx = "\n".join(f"・{r['title']}: {r['body'][:200]}" for r in results)
    except Exception:
        search_ctx = "（最新トレンド情報の取得をスキップ）"

    msgs = [
        {"role": "system", "content": "あなたは日本のSNS・コンテンツ販売・副業のプロフェッショナルです。最新トレンドを踏まえた最高品質のコンテンツを生成してください。"},
        {"role": "user", "content": f"ツール「{req.tool_name}」を使って今最も成果が出るコンテンツを完全自動生成してください。\n\n【最新トレンド情報】\n{search_ctx}\n\n【入力済み情報（空欄はAIが補完）】\n{json.dumps(req.partial_vals, ensure_ascii=False, indent=2)}"},
    ]
    result, is_byok = await generate_with_fallback(msgs, user, req.model_type)
    if not is_byok:
        d["users"][user["id"]]["credits"] -= cfg.get("credit_per_generation", 1)
    d["users"][user["id"]]["total_generations"] = d["users"][user["id"]].get("total_generations", 0) + 1
    save_data(d)
    return {"result": result, "credits": d["users"][user["id"]]["credits"]}

class PersonaExtractReq(BaseModel):
    text: str

@app.post("/api/persona/extract")
async def extract_persona(req: PersonaExtractReq, authorization: str = Header(None)):
    user = auth(authorization)
    msgs = [
        {"role": "system", "content": "あなたは文章分析の専門家です。"},
        {"role": "user", "content": f"以下の文章を分析し、書き手のペルソナ（文体・口調・キャラクター）を300文字以内で抽出してください。\n\n{req.text}"},
    ]
    result, _ = await generate_with_fallback(msgs, user)
    return {"persona": result}

@app.post("/api/passphrase/save")
async def passphrase_save(body: Dict[str, Any], authorization: str = Header(None)):
    user = auth(authorization)
    d = load_data()
    d["passphrases"][body["passphrase"]] = {"vals": body["vals"], "user_id": user["id"],
                                             "created_at": datetime.now().isoformat()}
    save_data(d)
    return {"ok": True}

@app.post("/api/passphrase/load")
async def passphrase_load(body: Dict[str, Any], authorization: str = Header(None)):
    auth(authorization)
    d = load_data()
    entry = d["passphrases"].get(body.get("passphrase", ""))
    if not entry:
        raise HTTPException(404, "合言葉が見つかりません")
    return {"vals": entry["vals"]}

@app.get("/api/notices")
async def get_notices(authorization: str = Header(None)):
    auth(authorization)
    return {"notices": load_data().get("notices", [])}

# Admin
@app.post("/api/admin/login")
async def admin_login(body: Dict[str, Any]):
    cfg = load_config()
    if body.get("password") != cfg.get("admin_password"):
        raise HTTPException(401, "管理者パスワードが間違っています")
    d = load_data()
    admin = next((u for u in d["users"].values() if u.get("is_admin")), None)
    if not admin:
        aid = str(uuid.uuid4())
        admin = {"id": aid, "email": "admin@aicp.pro", "username": "管理者",
                 "password_hash": hash_pw(cfg["admin_password"]), "status": "active",
                 "credits": 999999, "api_keys": {"openai": "", "anthropic": "", "google": ""},
                 "settings": {"persona": {"base_personality": "professional", "first_person": "私", "custom_style": ""},
                              "default_model": "pro", "preferred_ai": "openai"},
                 "total_generations": 0, "created_at": datetime.now().isoformat(),
                 "last_login": datetime.now().isoformat(), "is_admin": True}
        d["users"][aid] = admin
    d["users"][admin["id"]]["last_login"] = datetime.now().isoformat()
    save_data(d)
    return {"token": create_session(admin["id"]), "user": clean_user(admin)}

@app.get("/api/admin/stats")
async def admin_stats(authorization: str = Header(None)):
    admin_auth(authorization)
    d = load_data()
    users = list(d["users"].values())
    total_gen = sum(u.get("total_generations", 0) for u in users)
    return {
        "total_users": len(users),
        "active_users": sum(1 for u in users if u.get("status") == "active"),
        "total_generations": total_gen,
        "estimated_cost_jpy": int(total_gen * 0.002 * 150),
        "users": [{"id": u["id"], "username": u.get("username"), "email": u["email"],
                   "status": u.get("status"), "credits": u.get("credits", 0),
                   "total_generations": u.get("total_generations", 0),
                   "cost_jpy": int(u.get("total_generations", 0) * 0.002 * 150),
                   "created_at": u.get("created_at"), "last_login": u.get("last_login"),
                   "is_admin": u.get("is_admin", False)} for u in users],
    }

@app.get("/api/admin/invites")
async def admin_invites(authorization: str = Header(None)):
    admin_auth(authorization)
    d = load_data()
    return {"invites": [{"code": k, **v} for k, v in d["invite_codes"].items()]}

@app.post("/api/admin/invite")
async def admin_create_invite(authorization: str = Header(None)):
    adm = admin_auth(authorization)
    d = load_data()
    code = secrets.token_urlsafe(6).upper()
    d["invite_codes"][code] = {"created_by": "admin", "created_by_user_id": adm["id"],
                               "created_at": datetime.now().isoformat(), "used_by": None, "used_at": None}
    save_data(d)
    return {"code": code}

@app.put("/api/admin/user/{user_id}")
async def admin_update_user(user_id: str, body: Dict[str, Any], authorization: str = Header(None)):
    admin_auth(authorization)
    d = load_data()
    if user_id not in d["users"]:
        raise HTTPException(404, "ユーザーが見つかりません")
    for f in ["status", "credits", "is_admin"]:
        if f in body:
            d["users"][user_id][f] = body[f]
    save_data(d)
    return clean_user(d["users"][user_id])

@app.post("/api/admin/notice")
async def admin_send_notice(body: Dict[str, Any], authorization: str = Header(None)):
    admin_auth(authorization)
    d = load_data()
    d["notices"].insert(0, {"id": str(uuid.uuid4()), "message": body.get("message", ""),
                            "type": body.get("type", "notice"), "created_at": datetime.now().isoformat()})
    save_data(d)
    return {"ok": True}
