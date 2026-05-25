from functools import cached_property

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_ids(value: str | list[int] | tuple[int, ...] | None) -> frozenset[int]:
    if value is None or value == "":
        return frozenset()
    if isinstance(value, str):
        return frozenset(int(part.strip()) for part in value.split(",") if part.strip())
    return frozenset(int(item) for item in value)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    telegram_bot_token: str = Field(validation_alias=AliasChoices("TELEGRAM_BOT_TOKEN"))
    drift_api_token: str = Field(validation_alias=AliasChoices("DRIFT_API_TOKEN"))
    allowed_user_ids: str = Field(
        default="",
        validation_alias=AliasChoices("ALLOWED_USER_IDS"),
        description="Comma-separated Telegram user IDs allowed to use the bot.",
    )
    allowed_group_chat_ids: str = Field(
        default="",
        validation_alias=AliasChoices("ALLOWED_GROUP_CHAT_IDS"),
        description=(
            "Comma-separated Telegram group/supergroup chat IDs where mentions are accepted."
        ),
    )
    drift_base_url: str = Field(
        default="https://drift.neuraldeep.ru/v1",
        validation_alias=AliasChoices("DRIFT_BASE_URL"),
    )
    drift_model: str = Field(
        default="gpt-oss-120b",
        validation_alias=AliasChoices("DRIFT_MODEL"),
    )
    sqlite_path: str = Field(
        default="/data/bot.sqlite3",
        validation_alias=AliasChoices("SQLITE_PATH"),
    )
    request_timeout_seconds: float = Field(
        default=180.0,
        validation_alias=AliasChoices("REQUEST_TIMEOUT_SECONDS"),
    )

    @field_validator("allowed_user_ids", "allowed_group_chat_ids", mode="before")
    @classmethod
    def _keep_id_list_input(cls, value: object) -> object:
        return value

    @cached_property
    def allowed_users(self) -> frozenset[int]:
        return _parse_ids(self.allowed_user_ids)

    @cached_property
    def allowed_group_chats(self) -> frozenset[int]:
        return _parse_ids(self.allowed_group_chat_ids)
