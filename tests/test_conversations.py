from drift_tg_bot.conversations import ConversationStore


def test_conversation_store_persists_chat_mapping(tmp_path) -> None:
    db_path = tmp_path / "bot.sqlite3"
    store = ConversationStore(str(db_path))

    assert store.get(-100) is None

    store.set(-100, 1234)

    reopened = ConversationStore(str(db_path))
    assert reopened.get(-100) == 1234
