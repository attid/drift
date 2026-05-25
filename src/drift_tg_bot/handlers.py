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
        )
        if not text or not policy.should_handle(incoming):
            return

        prompt = normalize_prompt(text, bot_username)
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
