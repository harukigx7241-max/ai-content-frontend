"""
app/schemas/options.py — GenerateOptions
全リクエストスキーマに optional で付加できる生成オプション。
フロントエンドが送らない場合は None になり、既存動作と完全互換。

フィールド一覧:
  ai_provider   : ChatGPT / Gemini / Claude  (既存 ai_mode の上位互換)
  ai_plan       : free / plus / pro / unknown
  quality_mode  : lite / standard / deep
  input_mode    : normal / auto_assist / full_auto
  output_mode   : prompt / final_text / note_styled / image_prompt
  image_type    : thumbnail / illustration / sns_visual  (output_mode=image_prompt 時)
  image_platform: Midjourney / DALL-E / StableDiffusion / Adobe Firefly
"""
from pydantic import BaseModel, Field


class GenerateOptions(BaseModel):
    # AI プロバイダーと利用プラン
    ai_provider: str = Field(default="ChatGPT", max_length=20)
    ai_plan: str = Field(default="unknown", max_length=20)

    # 品質モード
    quality_mode: str = Field(default="standard", max_length=20)

    # 入力モード
    input_mode: str = Field(default="normal", max_length=20)

    # 出力モード
    output_mode: str = Field(default="prompt", max_length=20)

    # 画像生成オプション (output_mode=image_prompt 時のみ使用)
    image_type: str = Field(default="thumbnail", max_length=30)
    image_platform: str = Field(default="Midjourney", max_length=30)
