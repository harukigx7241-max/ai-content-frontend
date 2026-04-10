"""
app/services/input_mode_service.py
入力モード別の補足文サービス。
"""
from app.prompts.suffixes.input_mode import input_mode_suffix


def get_supplement(mode: str) -> str:
    """input_mode に対応する補足文字列を返す。normal は空文字。"""
    return input_mode_suffix(mode)
