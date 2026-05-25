from types import SimpleNamespace

from drift_tg_bot.handlers import _should_include_reply_context, build_prompt


def test_build_prompt_without_reply_removes_bot_mention() -> None:
    prompt = build_prompt(
        text="@drift_bot смотри как это сделать",
        bot_username="drift_bot",
        reply_text=None,
        include_reply_context=True,
    )

    assert prompt == "смотри как это сделать"


def test_build_prompt_with_reply_includes_replied_message_context() -> None:
    prompt = build_prompt(
        text="@drift_bot смотри как это сделать",
        bot_username="drift_bot",
        reply_text="Вот функция, которая падает на None",
        include_reply_context=True,
    )

    assert prompt == (
        "Пользователь ответил на сообщение в Telegram.\n\n"
        "Сообщение, на которое ответили:\n"
        "Вот функция, которая падает на None\n\n"
        "Комментарий пользователя:\n"
        "смотри как это сделать"
    )


def test_build_prompt_can_skip_reply_context() -> None:
    prompt = build_prompt(
        text="продолжи",
        bot_username="drift_bot",
        reply_text="Предыдущий ответ бота",
        include_reply_context=False,
    )

    assert prompt == "продолжи"


def test_skip_reply_context_for_recent_reply_to_bot_message() -> None:
    message = SimpleNamespace(
        message_id=110,
        bot=SimpleNamespace(id=42),
        reply_to_message=SimpleNamespace(
            message_id=101,
            from_user=SimpleNamespace(id=42, is_bot=True),
        ),
    )

    assert not _should_include_reply_context(message)


def test_include_reply_context_for_old_reply_to_bot_message() -> None:
    message = SimpleNamespace(
        message_id=120,
        bot=SimpleNamespace(id=42),
        reply_to_message=SimpleNamespace(
            message_id=101,
            from_user=SimpleNamespace(id=42, is_bot=True),
        ),
    )

    assert _should_include_reply_context(message)


def test_include_reply_context_for_reply_to_non_bot_message() -> None:
    message = SimpleNamespace(
        message_id=110,
        bot=SimpleNamespace(id=42),
        reply_to_message=SimpleNamespace(
            message_id=101,
            from_user=SimpleNamespace(id=99, is_bot=False),
        ),
    )

    assert _should_include_reply_context(message)
