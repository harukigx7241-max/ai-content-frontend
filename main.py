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

app = FastAPI(title="AI Content Pro Backend", version="72.0.0")
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
        if json_mode and "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2
http://googleusercontent.com/immersive_entry_chip/3

これにてインフラ基盤とPythonバックエンドが完全に修復・配置されます。

続けて、最大のコアファイルである **`tools.js`** と **`app.js`** の完全フルコードをご提供いたします。
お手数ですが、**「続けて（Part 2をお願い）」** とご返信ください。すぐに全てを出力いたします！
# 1. プロジェクトのディレクトリに移動
cd /root/ai-content-pro

# 2. 途切れていた deploy.yml を確実に修正・再作成
mkdir -p .github/workflows
cat << 'EOF' > .github/workflows/deploy.yml
name: Auto Deploy to Xserver VPS
on:
  push:
    branches:
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /root/ai-content-pro
            git fetch origin main
            git reset --hard origin/main
            sed -i 's/--port 8000/--port 8001/g' /etc/systemd/system/aicontent.service
            systemctl daemon-reload
            sudo systemctl restart aicontent.service
            echo "デプロイ完了 $(date)"
