"""
app/db/models/system_setting.py — システム設定の永続化モデル

管理者がダッシュボードから変更した設定を DB に保存する。
起動時に app/core/runtime_config.py に読み込まれ、即時反映される。

管理するキー (定数は app/core/runtime_config.py 参照):
  maintenance_enabled    : bool (true/false)
  maintenance_message    : str
  notice_banner_enabled  : bool
  notice_banner_text     : str
  notice_banner_link     : str
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=_now)
    updated_by = Column(Integer, nullable=True)  # 更新した管理者の user.id

    def __repr__(self) -> str:
        return f"<SystemSetting {self.key}={self.value!r}>"
