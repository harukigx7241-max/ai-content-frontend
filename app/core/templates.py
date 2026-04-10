"""
app/core/templates.py
Jinja2Templates のシングルトン。
ルーターから直接インポートして使う。
"""
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
