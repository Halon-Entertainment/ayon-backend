import re

from pydantic import BaseModel, ConfigDict

pattern = re.compile(r"(?<!^)(?=[A-Z])")


class BaseSettingsModel(BaseModel):
    _isGroup: bool = False
    _title: str | None = None
    _layout: str | None = None
    _required: bool = False
    _has_studio_overrides: bool | None = None
    _has_project_overrides: bool | None = None
    _has_site_overrides: bool | None = None
    model_config = ConfigDict(populate_by_name=True)
