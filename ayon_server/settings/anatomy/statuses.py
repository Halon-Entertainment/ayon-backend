from typing import Literal

from pydantic import validator

from ayon_server.settings.common import BaseSettingsModel
from ayon_server.settings.settings_field import SettingsField

State = Literal["not_started", "in_progress", "done", "blocked"]


def get_state_enum():
    return [
        {"value": "not_started", "label": "Not Started"},
        {"value": "in_progress", "label": "In Progress"},
        {"value": "done", "label": "Done"},
        {"value": "blocked", "label": "Blocked"},
    ]


class Status(BaseSettingsModel):
    _layout: str = "compact"
    name: str = SettingsField(
        ..., title="Name", min_length=1, max_length=100, example="In progress"
    )
    shortName: str = SettingsField("", title="Short name", example="PRG")
    state: State = SettingsField(
        "not_started",
        title="State",
        enum_resolver=get_state_enum,
        example="in_progress",
    )
    icon: str = SettingsField("", title="Icon", widget="icon", example="play_arrow")
    color: str = SettingsField(
        "#cacaca", title="Color", widget="color", example="#3498db"
    )
    original_name: str | None = SettingsField(None, scope=[])  # Used for renaming

    @validator("original_name")
    def validate_original_name(cls, v, values):
        if v is None:
            return values["name"]
        return v

    def __hash__(self):
        return hash(self.name)


default_statuses = [
    Status(
        name="Not ready",
        shortName="NRD",
        icon="fiber_new",
        color="#434a56",
        state="not_started",
    ),
    Status(
        name="Ready to start",
        shortName="RDY",
        icon="timer",
        color="#bababa",
        state="not_started",
    ),
    Status(
        name="In progress",
        shortName="PRG",
        icon="play_arrow",
        color="#3498db",
        state="in_progress",
    ),
    Status(
        name="Pending review",
        shortName="RVW",
        icon="visibility",
        color="#ff9b0a",
        state="in_progress",
    ),
    Status(
        name="Approved",
        shortName="APP",
        icon="task_alt",
        color="#00f0b4",
        state="done",
    ),
    Status(
        name="On hold",
        shortName="HLD",
        icon="back_hand",
        color="#fa6e46",
        state="blocked",
    ),
    Status(
        name="Omitted",
        shortName="OMT",
        icon="block",
        color="#cb1a1a",
        state="blocked",
    ),
]
