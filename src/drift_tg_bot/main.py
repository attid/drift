import asyncio
import logging

from aiogram import Bot, Dispatcher

from drift_tg_bot.config import Settings
from drift_tg_bot.conversations import ConversationStore
from drift_tg_bot.drift import DriftClient
from drift_tg_bot.handlers import create_router
from drift_tg_bot.policy import MessagePolicy


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = Settings()

    bot = Bot(token=settings.telegram_bot_token)
    me = await bot.get_me()
    if not me.username:
        raise RuntimeError("Telegram bot has no username")

    policy = MessagePolicy(
        allowed_user_ids=settings.allowed_users,
        allowed_group_chat_ids=settings.allowed_group_chats,
        bot_username=me.username,
    )
    store = ConversationStore(settings.sqlite_path)
    drift = DriftClient(
        base_url=settings.drift_base_url,
        api_token=settings.drift_api_token,
        model=settings.drift_model,
        timeout_seconds=settings.request_timeout_seconds,
    )

    dispatcher = Dispatcher()
    dispatcher.include_router(
        create_router(policy=policy, store=store, drift=drift, bot_username=me.username)
    )

    try:
        await dispatcher.start_polling(bot)
    finally:
        await drift.close()
        await bot.session.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
