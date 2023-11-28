from pydantic import Field

from ayon_server.entities import UserEntity
from ayon_server.types import OPModel


class LoginResponseModel(OPModel):
    detail: str | None = Field(None, examples=["Logged in as NAME"])
    error: str | None = Field(None, examples=["Unauthorized"])
    token: str | None = Field(None, title="Access token", examples=["TOKEN"])
    user: UserEntity.model.main_model | None = Field(  # type: ignore
        None,
        title="User data",
    )


class LogoutResponseModel(OPModel):
    detail: str = Field(
        "Logged out",
        title="Response detail",
        description="Text description, which may be displayed to the user",
        examples=["Logged out"],
    )
