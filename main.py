from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from duckduckgo_search import DDGS
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
import httpx
import asyncio
import os
import json
import random
import re
import base64

app = FastAPI(title="AI Content Pro Backend", version="73.3.0")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
CONFIG_FILE = "server_config.json"

def get_admin_keys():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return {
                    "openai": data.get("openai_api_key", ""),
                    "anthropic": data.get("anthropic_api_key", ""),
                    "google": data.get("google_api_key", "")
                }
            except: pass
    return {"openai": "", "anthropic": "", "google": ""}

class InquiryData(BaseModel):
    nickname: str
    content: str

class AutoGenerateRequest(BaseModel):
    prompt: str
    user_api_key: Optional[str] = None
    ai_model: Optional[str] = "chatgpt_free"
    image_base64: Optional[str] = None

class ConfigUpdate(BaseModel):
    openai_api_key: str
    anthropic_api_key: Optional[str] = ""
    google_api_key: Optional[str] = ""

class MagicGenerateRequest(BaseModel):
    tool_id: str
    fields: List[Dict[str, Any]]
    target_fid: Optional[str] = None
    prompt_instruction: Optional[str] = None
    user_keys: Optional[Dict[str, str]] = {}
    url: Optional[str] = None
    keyword: Optional[str] = None

async def generate_with_openai(prompt: str, api_key: str, ai_model: str = "chatgpt_free", json_mode: bool = False, image_base64: str = None):
    try:
        client = AsyncOpenAI(api_key=api_key)
        response_format = { "type": "json_object" } if json_mode else None
        model_name = "gpt-4o" if "paid" in ai_model else "gpt-4o-mini"
        messages = []
        if image_base64:
            messages = [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}]
        else:
            messages = [{"role": "user", "content": prompt}]
        response = await client.chat.completions.create(model=model_name, messages=messages, temperature=0.8, response_format=response_format)
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAIエラー: {str(e)}")

async def generate_with_anthropic(prompt: str, api_key: str, ai_model: str = "claude_free", json_mode: bool = False, image_base64: str = None):
    try:
        final_prompt = prompt
        if json_mode: final_prompt += "\n\nIMPORTANT: Output strictly in JSON format only."
        client = AsyncAnthropic(api_key=api_key)
        model_name = "claude-3-7-sonnet-20250219" if "paid" in ai_model else "claude-3-5-haiku-20241022"
        messages = []
        if image_base64:
            messages = [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_base64}},
                {"type": "text", "text": final_prompt}
            ]}]
        else:
            messages = [{"role": "user", "content": final_prompt}]
        response = await client.messages.create(model=model_name, max_tokens=4000, temperature=0.8, messages=messages)
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Anthropicエラー: {str(e)}")

async def generate_with_google(prompt: str, api_key: str, ai_model: str = "gemini_free", json_mode: bool = False, image_base64: str = None):
    try:
        genai.configure(api_key=api_key)
        model_name = 'gemini-1.5-pro' if "paid" in ai_model else 'gemini-2.0-flash'
        model = genai.GenerativeModel(model_name)
        final_prompt = prompt
        if json_mode: final_prompt += "\n\nIMPORTANT: Output strictly in JSON format only."
        contents = [final_prompt]
        if image_base64:
            image_data = base64.b64decode(image_base64)
            contents.append({"mime_type": "image/jpeg", "data": image_data})
        response = await model.generate_content_async(contents)
        text = response.text
        if json_mode and "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif json_mode and "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return text
    except Exception as e:
        raise Exception(f"Googleエラー: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/trends")
async def get_trends():
    try:
        def fetch_trends():
            with DDGS() as ddgs:
                results = list(ddgs.news(keywords="日本 ニュース トレンド", region="jp-jp", safesearch="moderate", timelimit="d", max_results=30))
            filtered = []
            for r in results:
                title = r.get("title", "")
                if not title: continue
                has_japanese = bool(re.search(r'[ぁ-んァ-ン一-龯]', title))
                has_long_english = bool(re.search(r'[a-zA-Z]{8,}', title))
                has_mojibake = bool(re.search(r'[ãäåæçèéêëìíîïðñòóôõö]', title))
                if has_japanese and not has_long_english and not has_mojibake:
                    filtered.append({"title": title, "url": r.get("url", ""), "body": r.get("body", "")[:100]})
            return filtered[:10]
        filtered_results = await asyncio.to_thread(fetch_trends)
        return JSONResponse({"status": "success", "data": filtered_results, "total": len(filtered_results)})
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"トレンド取得エラー: {str(e)}"})

@app.post("/api/admin/update_keys")
async def update_keys(data: ConfigUpdate):
    config_data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try: config_data = json.load(f)
            except: pass
    config_data["openai_api_key"] = data.openai_api_key
    config_data["anthropic_api_key"] = data.anthropic_api_key
    config_data["google_api_key"] = data.google_api_key
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    print(" 管理画面から各種APIキーが保存されました")
    return JSONResponse({"status": "success", "message": "各種APIキーを安全に保存しました"})

@app.post("/api/inquiry")
async def receive_inquiry(data: InquiryData):
    print(f"\n お問い合わせ受信: {data.nickname} 様より\n{data.content}\n")
    return JSONResponse({"status": "success", "message": "Pythonサーバーで完璧に受け取りました!"})

@app.post("/api/magic_generate")
async def magic_generate(req: MagicGenerateRequest):
    is_image_prompt_gen = req.tool_id in ['image', 'eye_catch', 'slide_gen']
    ai_provider = req.prompt_instruction if req.prompt_instruction else "openai"
    admin_keys = get_admin_keys()
    active_key = req.user_keys.get(ai_provider) if req.user_keys else None
    if not active_key:
        active_key = admin_keys.get(ai_provider)
    if not active_key:
        return JSONResponse({"status": "error", "message": f"{ai_provider.upper()} のAPIキーが設定されていません。"})
    
    try:
        if is_image_prompt_gen:
            print(f" 画像プロンプト生成中... (使用AI: {ai_provider.upper()})")
            vals_desc = "\n".join([f"・{f.get('l')}: {f.get('val','(未入力)')}" for f in req.fields])
            prompt = f"""あなたは画像生成AI(Midjourney、Stable Diffusion、DALL-E3など)を完璧に操るプロンプトエンジニアです。
以下の【ユーザーのリクエスト情報】を深く理解し、最高の画像を出力させるための「最強のプロンプト(英語)」を1パターン作成してください。

【重要ルール】
1. 出力は「Markdownの見出し(#)」や「AIとしての解説、前置き」などは一切含めず、**Midjourney等にコピペしてそのまま使える英語のプロンプトテキストのみ**を直接出力すること。
2. 被写体、背景、ライティング、カメラ、スタイルを豊富に盛り込み、プロレベルの高画質な画像が生成されるようにすること。

【ユーザーのリクエスト情報】
{vals_desc}"""
            model_tier = f"{ai_provider}_free"
            if ai_provider == 'openai':
                generated_text = await generate_with_openai(prompt, active_key, ai_model=model_tier, json_mode=False)
            elif ai_provider == 'anthropic':
                generated_text = await generate_with_anthropic(prompt, active_key, ai_model=model_tier, json_mode=False)
            elif ai_provider == 'google':
                generated_text = await generate_with_google(prompt, active_key, ai_model=model_tier, json_mode=False)
            return JSONResponse({"status": "success", "data": generated_text})
        else:
            print(f" 魔法の杖 (動的自動入力)発動中...(使用AI: {ai_provider.upper()})")
            dynamic_keywords = []
            for f in req.fields:
                val = f.get('val', '')
                if isinstance(val, str) and val.strip() and f.get('id') != req.target_fid and len(val) < 30:
                    dynamic_keywords.append(val.strip())
            
            if req.keyword:
                query = f"{req.keyword} 最新トレンド 日本"
            elif dynamic_keywords:
                query = " ".join(dynamic_keywords[:3]) + " 最新トレンド 日本"
            else:
                random_topics = ["副業 ビジネス", "SNS マーケティング", "AI テクノロジー", "投資マネー", "美容 ダイエット", "恋愛心理学", "ライフスタイル"]
                query = f"{random.choice(random_topics)} 最新トレンド 日本"
            
            def search_trends(q):
                with DDGS() as ddgs: return list(ddgs.text(q, region="jp-jp", safesearch="moderate", max_results=3))
            try:
                search_results = await asyncio.to_thread(search_trends, query)
                trend_info = "\n".join([f"・{r['title']}: {r['body']}" for r in search_results]) if search_results else "特に検索結果なし。"
            except Exception as e:
                print("検索エラー:", e)
                trend_info = "Web検索がタイムアウトしました。あなたの持つ知識から、日本の最新トレンドを予測して考慮してください。"
                
            url_info = ""
            if req.url:
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(req.url, headers={'User-Agent': 'Mozilla/5.0'})
                        html = response.text
                        text = re.sub(r'<[^>]+>', '', html)
                        text = re.sub(r'\s+', ' ', text)
                        url_info = f"【参考URLの抽出内容】\n{text[:2000]}\n\n"
                        print(f" URL 抽出成功: {req.url}")
                except Exception as e:
                    print("URLスクレイピングエラー:", e)
                    url_info = "【参考URLの抽出内容】\n(URLの読み取りに失敗しました。この情報は無視してください)\n\n"
                    
            target_fields = [f for f in req.fields if f.get('id') == req.target_fid] if req.target_fid and req.target_fid != 'all' else req.fields
            fields_json_str = json.dumps(target_fields, ensure_ascii=False)
            
            prompt = f"""あなたは日本市場に特化した優秀なマーケターであり、発想力豊かなAIアシスタントです。
以下の【参考URLの抽出内容】や【最新トレンド参考情報】を加味し、ツールの【埋めるべき入力項目とプレースホルダー(例)】を参考にして、ユーザーがそのまま使えるリアルで高品質なダミーデータ(指定されたキーワードやURLに沿った内容)を作成してください。

【重要ルール】
1. 対象読者や内容は必ず「日本人専用(日本の文化、通貨単位、市場、SNSの使われ方などに合った内容)」にすること。
2. プレースホルダー(ph)に記載されている「例」の形式や文字数のボリューム感を参考にすること。
3. 以下の「出力ルール」に従い、JSONフォーマットのみを直接出力すること。

{url_info}

【最新トレンド参考情報】
{trend_info}

【追加キーワード/指示】
{req.keyword if req.keyword else "特になし"}

【埋めるべき入力項目とプレースホルダー(例)】
{fields_json_str}

【出力ルール】
各項目の'id'をキーとし、生成したテキストを値とするJSON形式のみを出力してください。
マークダウン表記や前置き・説明などは一切不要です。
例:{{"prod": "AI ブログ自動化ツール", "target":"毎日残業で忙しい30代の会社員"}}"""
            
            model_tier = f"{ai_provider}_free"
            result_json_str = ""
            if ai_provider == 'openai':
                result_json_str = await generate_with_openai(prompt, active_key, ai_model=model_tier, json_mode=True)
            elif ai_provider == 'anthropic':
                result_json_str = await generate_with_anthropic(prompt, active_key, ai_model=model_tier, json_mode=True)
            elif ai_provider == 'google':
                result_json_str = await generate_with_google(prompt, active_key, ai_model=model_tier, json_mode=True)
                
            if "```json" in result_json_str:
                result_json_str = result_json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in result_json_str:
                result_json_str = result_json_str.split("```")[1].split("```")[0].strip()
            
            result_json = json.loads(result_json_str)
            print(" 魔法の杖によるデータ生成完了!")
            return JSONResponse({"status": "success", "data": result_json})
    except Exception as e:
        print(" 生成エラー:", e)
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/auto_generate")
async def auto_generate(req: AutoGenerateRequest):
    admin_keys = get_admin_keys()
    try:
        print(f" AI自動生成スタート... (モデル: {req.ai_model})")
        if "claude" in req.ai_model.lower():
            active_key = req.user_api_key if req.user_api_key else admin_keys.get('anthropic')
            if not active_key:
                return JSONResponse({"status": "error", "message": "ANTHROPIC のAPIキーが設定されていません。"})
            generated_text = await generate_with_anthropic(req.prompt, active_key, ai_model=req.ai_model, json_mode=False, image_base64=req.image_base64)
        elif "gemini" in req.ai_model.lower():
            active_key = req.user_api_key if req.user_api_key else admin_keys.get('google')
            if not active_key:
                return JSONResponse({"status": "error", "message": "GOOGLEのAPIキーが設定されていません。"})
            generated_text = await generate_with_google(req.prompt, active_key, ai_model=req.ai_model, json_mode=False, image_base64=req.image_base64)
        else:
            active_key = req.user_api_key if req.user_api_key else admin_keys.get('openai')
            if not active_key:
                return JSONResponse({"status": "error", "message": "OPENAIのAPIキーが設定されていません。"})
            generated_text = await generate_with_openai(req.prompt, active_key, ai_model=req.ai_model, json_mode=False, image_base64=req.image_base64)
            
        print(" AI自動生成完了!")
        return JSONResponse({"status": "success", "result": generated_text})
    except Exception as e:
        print(" AI生成エラー:", e)
        return JSONResponse({"status": "error", "message": f"API エラー: {str(e)}"})

@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok", "version": "v73.0.0"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)