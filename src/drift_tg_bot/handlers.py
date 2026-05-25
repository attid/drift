import logging

import httpx
from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from drift_tg_bot.conversations import ConversationStore
from drift_tg_bot.drift import DriftClient
from drift_tg_bot.policy import IncomingMessage, MessagePolicy, normalize_prompt

logger = logging.getLogger(__name__)


def create_router(
    *,
    policy: MessagePolicy,
    store: ConversationStore,
    drift: DriftClient,
    bot_username: str,
) -> Router:
    router = Router(name=__name__)

    @router.message()
    async def handle_message(message: Message) -> None:
        text = message.text or message.caption or ""
        incoming = IncomingMessage(
            chat_id=message.chat.id,
            chat_type=message.chat.type,
            from_user_id=message.from_user.id if message.from_user else None,
            text=text,
            is_reply_to_bot=_is_reply_to_bot(message),
        )
        if not text or not policy.should_handle(incoming):
            return

        prompt = build_prompt(
            text=text,
            bot_username=bot_username,
            reply_text=_reply_text(message),
            include_reply_context=_should_include_reply_context(message),
        )
        if not prompt:
            return

        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        try:
            conversation_id = await _get_or_create_conversation(message, store, drift)
            answer = await drift.send_message(prompt=prompt, conversation_id=conversation_id)
        except httpx.HTTPStatusError as exc:
            logger.exception("Drift API returned an error")
            await message.answer(f"Drift API error: {exc.response.status_code}")
            return
        except httpx.HTTPError:
            logger.exception("Drift API request failed")
            await message.answer("Drift API request failed.")
            return

        if answer:
            await message.answer(answer)
        else:
            await message.answer("Drift returned an empty response.")

    return router


def _is_reply_to_bot(message: Message) -> bool:
    reply = message.reply_to_message
    reply_from = reply.from_user if reply else None
    return bool(reply_from and reply_from.is_bot and reply_from.id == message.bot.id)


def _reply_text(message: Message) -> str | None:
    reply = message.reply_to_message
    if not reply:
        return None
    text = reply.text or reply.caption
    return text.strip() if text else None


def _should_include_reply_context(message: Message) -> bool:
    reply = message.reply_to_message
    if not reply or not _is_reply_to_bot(message):
        return True
    return abs(message.message_id - reply.message_id) > 10


def build_prompt(
    *,
    text: str,
    bot_username: str,
    reply_text: str | None,
    include_reply_context: bool,
) -> str:
    user_text = normalize_prompt(text, bot_username)
    if not reply_text or not include_reply_context:
        return user_text

    return (
        "Пользователь ответил на сообщение в Telegram.\n\n"
        "Сообщение, на которое ответили:\n"
        f"{reply_text}\n\n"
        "Комментарий пользователя:\n"
        f"{user_text}"
    )


async def _get_or_create_conversation(
    message: Message,
    store: ConversationStore,
    drift: DriftClient,
) -> int:
    existing = store.get(message.chat.id)
    if existing is not None:
        return existing

    title = _conversation_title(message)
    conversation_id = await drift.create_conversation(title)
    store.set(message.chat.id, conversation_id)
    return conversation_id


def _conversation_title(message: Message) -> str:
    if message.chat.title:
        return f"Telegram: {message.chat.title}"
    if message.from_user and message.from_user.username:
        return f"Telegram: @{message.from_user.username}"
    return f"Telegram chat {message.chat.id}"
