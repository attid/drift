from dataclasses import dataclass

GROUP_CHAT_TYPES = {"group", "supergroup"}


@dataclass(frozen=True)
class IncomingMessage:
    chat_id: int
    chat_type: str
    from_user_id: int | None
    text: str
    is_reply_to_bot: bool = False


def normalize_prompt(text: str, bot_username: str) -> str:
    mention = f"@{bot_username.lstrip('@')}"
    words = text.strip().split()
    filtered = [word for word in words if word.lower() != mention.lower()]
    return " ".join(filtered).strip()


class MessagePolicy:
    def __init__(
        self,
        *,
        allowed_user_ids: frozenset[int],
        allowed_group_chat_ids: frozenset[int],
        bot_username: str,
    ) -> None:
        self._allowed_user_ids = allowed_user_ids
        self._allowed_group_chat_ids = allowed_group_chat_ids
        self._bot_username = bot_username.lstrip("@")

    def should_handle(self, message: IncomingMessage) -> bool:
        if message.from_user_id is None or message.from_user_id not in self._allowed_user_ids:
            return False

        if message.chat_type == "private":
            return True

        if message.chat_type in GROUP_CHAT_TYPES:
            return (
                message.chat_id in self._allowed_group_chat_ids
                and (self._has_bot_mention(message.text) or message.is_reply_to_bot)
            )

        return False

    def _has_bot_mention(self, text: str) -> bool:
        mention = f"@{self._bot_username}".lower()
        return mention in {word.strip(".,:;!?()[]{}").lower() for word in text.split()}
