"""
app/services/image_prompt_service.py
画像生成プロンプトサービス。

Tiers:
  FREE  — 画像プロンプト文字列の生成のみ (APIコールなし、常に動作)
  API   — DALL-E / Stable Diffusion 等への実際の画像生成APIコール (未実装)
  DISABLED — ENABLE_IMAGE_GENERATION=false 時

image_type の拡張マッピング:
  thumbnail   → thumbnail  (16:9 サムネイル)
  illustration → section   (記事内挿絵)
  sns_visual  → social     (SNS 告知用)
  cover       → cover      (カバー画像)

既存の build_image_prompt ビルダーをラップする。
"""
from app.schemas.enhance import ImagePromptRequest
from app.prompts.builders.enhance import build_image_prompt
from app.services.base import BaseService, ServiceMode, ServiceResult

# 新 image_type 名 → 既存 image_type 名 のエイリアス
_TYPE_ALIAS: dict[str, str] = {
    "illustration": "section",
    "sns_visual": "social",
    # 既存値はそのまま通す
    "thumbnail": "thumbnail",
    "section": "section",
    "social": "social",
    "cover": "cover",
}


class ImagePromptService(BaseService):
    FLAG_KEY = "IMAGE_GENERATION"
    PREFER_API = False  # 現時点では画像API未実装のためFREE固定
    def __init__(
        self,
        theme: str,
        image_type: str = "thumbnail",
        image_platform: str = "Midjourney",
        style: str = "モダン・クリーン・プロフェッショナル",
        ai_mode: str = "ChatGPT",
    ):
        self.theme = theme
        self.image_type = _TYPE_ALIAS.get(image_type, image_type)
        self.image_platform = image_platform
        self.style = style
        self.ai_mode = ai_mode

    def build(self) -> str:
        """画像生成プロンプトを構築して返す (後方互換)。"""
        req = ImagePromptRequest(
            theme=self.theme,
            image_type=self.image_type,
            style=self.style,
            platform=self.image_platform,
            ai_mode=self.ai_mode,
        )
        return build_image_prompt(req)

    def build_as_result(self) -> ServiceResult:
        """ServiceResult 形式で返すバリアント。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        prompt = self.build()
        return ServiceResult.free(
            content={"prompt": prompt},
            hint="画像プロンプトをMidjourney・DALL-Eに貼り付けて使用してください",
        )

    @classmethod
    def from_request(cls, p: ImagePromptRequest) -> "ImagePromptService":
        """ImagePromptRequest から直接インスタンスを作成する。"""
        return cls(
            theme=p.theme,
            image_type=p.image_type,
            image_platform=p.platform,
            style=p.style,
            ai_mode=p.ai_mode,
        )
