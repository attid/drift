from drift_tg_bot.config import Settings


def test_settings_parse_comma_separated_ids() -> None:
    settings = Settings(
        telegram_bot_token="tg-token",
        drift_api_token="dft-token",
        allowed_user_ids="10, 20",
        allowed_group_chat_ids="-1001,-1002",
    )

    assert settings.allowed_users == frozenset({10, 20})
    assert settings.allowed_group_chats == frozenset({-1001, -1002})


def test_settings_parse_empty_id_lists() -> None:
    settings = Settings(
        telegram_bot_token="tg-token",
        drift_api_token="dft-token",
        allowed_user_ids="",
        allowed_group_chat_ids="",
    )

    assert settings.allowed_users == frozenset()
    assert settings.allowed_group_chats == frozenset()


def test_settings_parse_ids_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tg-token")
    monkeypatch.setenv("DRIFT_API_TOKEN", "dft-token")
    monkeypatch.setenv("ALLOWED_USER_IDS", "10,20")
    monkeypatch.setenv("ALLOWED_GROUP_CHAT_IDS", "-1001")

    settings = Settings(_env_file=None)

    assert settings.allowed_users == frozenset({10, 20})
    assert settings.allowed_group_chats == frozenset({-1001})
