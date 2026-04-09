"""
app/services/image_prompt_service.py
画像生成プロンプトサービス。

image_type の拡張マッピング:
  thumbnail   → thumbnail  (16:9 サムネイル)
  illustration → section   (記事内挿絵)
  sns_visual  → social     (SNS 告知用)
  cover       → cover      (カバー画像)

既存の build_image_prompt ビルダーをラップする。
"""
from app.schemas.enhance import ImagePromptRequest
from app.prompts.builders.enhance import build_image_prompt

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


class ImagePromptService:
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
        """画像生成プロンプトを構築して返す。"""
        req = ImagePromptRequest(
            theme=self.theme,
            image_type=self.image_type,
            style=self.style,
            platform=self.image_platform,
            ai_mode=self.ai_mode,
        )
        return build_image_prompt(req)

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
