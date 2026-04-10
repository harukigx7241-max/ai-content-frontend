"""app/schemas/enhance.py — Phase 1: プロンプト強化系リクエストモデル"""
from pydantic import BaseModel, Field


class DirectOutputRequest(BaseModel):
    """前置き不要モード: 既存プロンプトに直接出力指示を追加する。"""
    prompt: str = Field(..., min_length=10, max_length=8000)


class NoteFormatRequest(BaseModel):
    """note.com 装飾モード: 既存プロンプトに note 向け装飾指示を追加する。"""
    prompt: str = Field(..., min_length=10, max_length=8000)


class AiOptimizeRequest(BaseModel):
    """AI 深層最適化モード: AI プラン別の詳細な最適化指示を追加する。"""
    prompt: str = Field(..., min_length=10, max_length=8000)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


class AutocompleteRequest(BaseModel):
    """
    空欄補完モード: カテゴリ・ツール・ヒントからフォーム入力案を生成する。
    category: "note" | "cw" | "fortune" | "sns"
    tool: "article" | "proposal" | "reading" | "twitter" | etc.
    """
    category: str = Field(..., max_length=20)
    tool: str = Field(..., max_length=50)
    hint: str = Field(..., min_length=1, max_length=500)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


class ImagePromptRequest(BaseModel):
    """
    画像生成プロンプト生成: 記事テーマから画像 AI 向けプロンプトを作成する。
    image_type: "thumbnail" | "section" | "social" | "cover"
    platform: "Midjourney" | "DALL-E" | "StableDiffusion" | "Adobe Firefly"
    """
    theme: str = Field(..., min_length=1, max_length=200)
    image_type: str = Field(default="thumbnail", max_length=30)
    style: str = Field(default="モダン・クリーン・プロフェッショナル", max_length=100)
    platform: str = Field(default="Midjourney", max_length=30)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
