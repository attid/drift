from drift_tg_bot.policy import IncomingMessage, MessagePolicy, normalize_prompt


def test_private_chat_allowed_user_can_write_without_mention() -> None:
    policy = MessagePolicy(
        allowed_user_ids=frozenset({10}),
        allowed_group_chat_ids=frozenset({-100}),
        bot_username="drift_bot",
    )

    message = IncomingMessage(chat_id=10, chat_type="private", from_user_id=10, text="hello")

    assert policy.should_handle(message)


def test_private_chat_rejects_unknown_user() -> None:
    policy = MessagePolicy(
        allowed_user_ids=frozenset({10}),
        allowed_group_chat_ids=frozenset(),
        bot_username="drift_bot",
    )

    message = IncomingMessage(chat_id=99, chat_type="private", from_user_id=99, text="hello")

    assert not policy.should_handle(message)


def test_group_chat_requires_allowed_chat_allowed_user_and_mention() -> None:
    policy = MessagePolicy(
        allowed_user_ids=frozenset({10}),
        allowed_group_chat_ids=frozenset({-100}),
        bot_username="drift_bot",
    )

    message = IncomingMessage(
        chat_id=-100,
        chat_type="supergroup",
        from_user_id=10,
        text="@drift_bot расскажи статус",
    )

    assert policy.should_handle(message)


def test_group_chat_ignores_messages_without_mention() -> None:
    policy = MessagePolicy(
        allowed_user_ids=frozenset({10}),
        allowed_group_chat_ids=frozenset({-100}),
        bot_username="drift_bot",
    )

    message = IncomingMessage(
        chat_id=-100,
        chat_type="group",
        from_user_id=10,
        text="расскажи статус",
    )

    assert not policy.should_handle(message)


def test_normalize_prompt_removes_bot_mention() -> None:
    assert normalize_prompt("@drift_bot расскажи статус", "drift_bot") == "расскажи статус"
