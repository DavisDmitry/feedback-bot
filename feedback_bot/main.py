import asyncio
import logging
import os
import sqlite3 as sqlite

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import IDFilter

from feedback_bot import utils
from feedback_bot.chat_repository import SQLiteChatRepository as ChatRepository

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TOKEN = os.environ["BOT_TOKEN"]
DOMAIN = os.environ["BOT_DOMAIN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/database.db")
DEFAULT_CHAT_ID = int(os.getenv("DEFAULT_CHAT_ID", ADMIN_ID))
MESSAGES_PATH = os.getenv("MESSAGES_PATH", "/data/messages.yml")
WH_PATH = "/" + utils.generate_random_string()


logging.basicConfig(level=LOG_LEVEL.upper())


bot = Bot(TOKEN, parse_mode="html")
dp = Dispatcher(bot)


@dp.message_handler(commands=("start", "help"))
async def handle_start_and_help_commands(msg: types.Message):
    await msg.answer(msg.bot.data["messages"]["start"])


@dp.message_handler(
    IDFilter(chat_id=DEFAULT_CHAT_ID),
    content_types=types.ContentType.ANY,
    run_task=True,
    is_reply=True,
)
async def handle_reply_from_admin(msg: types.Message):
    entities = msg.reply_to_message.entities

    if not len(entities) == 1 or not str(entities[0].type) == "hashtag":
        return

    entity = entities[0]
    tg_id = int(
        msg.reply_to_message.text[entity.offset + 3 : entity.offset + entity.length]
    )
    await msg.copy_to(tg_id)
    msg_to_delete = await msg.reply(
        msg.bot.data["messages"]["forwarded_to_user"].format(user_id=tg_id)
    )
    await asyncio.sleep(5)
    await msg_to_delete.delete()


@dp.message_handler(
    IDFilter(user_id=ADMIN_ID), regexp=r"/link .*", chat_type=types.ChatType.GROUP
)
async def handle_link_command_from_admin(msg: types.Message):
    try:
        user_id = int(msg.text.split(" ", 1)[1])
    except (IndexError, ValueError):
        return await msg.reply(msg.bot.data["messages"]["invalid_link_command"])

    chat_repo = ChatRepository(msg.bot.data["db_conn"])

    if await chat_repo.is_admin_chat(msg.chat.id):
        return await msg.reply(msg.bot.data["messages"]["chat_using_for_another_user"])

    if await chat_repo.get_by_user_id(user_id):
        return await msg.reply(msg.bot.data["messages"]["exist_chat_for_this_user"])

    await chat_repo.create(msg.chat.id, user_id)
    await msg.reply(msg.bot.data["messages"]["chat_linked"].format(user_id=user_id))


@dp.message_handler(
    IDFilter(user_id=ADMIN_ID), commands="unlink", chat_type=types.ChatType.GROUP
)
async def handle_unlink_command_from_admin(msg: types.Message):
    chat_repo = ChatRepository(msg.bot.data["db_conn"])
    if not await chat_repo.is_admin_chat(msg.chat.id):
        return

    await chat_repo.remove_by_chat_id(msg.chat.id)


@dp.message_handler(IDFilter(user_id=ADMIN_ID), chat_type=types.ChatType.GROUP)
async def handle_message_in_admin_group(msg: types.Message):
    chat_repo = ChatRepository(msg.bot.data["db_conn"])
    chat_from_db = await chat_repo.get_by_chat_id(msg.chat.id)
    if not chat_from_db:
        return

    await msg.copy_to(chat_from_db.user_id)


@dp.message_handler(
    chat_type=types.ChatType.PRIVATE, content_types=types.ContentType.ANY, run_task=True
)
async def handle_message_from_user(msg: types.Message):
    chat_repo = ChatRepository(msg.bot.data["db_conn"])
    admin_chat_to_forward = await chat_repo.get_by_user_id(msg.chat.id)
    chat_to_forward = (
        admin_chat_to_forward.chat_id if admin_chat_to_forward else ADMIN_ID
    )
    msg_to_reply = await msg.forward(chat_to_forward)
    msg_to_delete = await msg.reply(msg.bot.data["messages"]["forwarded_to_owner"])
    if not admin_chat_to_forward:
        await msg_to_reply.reply(f"Message from #ID{msg.from_user.id}")
    await asyncio.sleep(5)
    await msg_to_delete.delete()


@dp.my_chat_member_handler(chat_type=types.ChatType.GROUP)
async def handle_bot_removed_from_group(cmu: types.ChatMemberUpdated):
    if cmu.new_chat_member.status != "left":
        return

    chat_repo = ChatRepository(cmu.bot.data["db_conn"])
    if not await chat_repo.is_admin_chat(cmu.chat.id):
        return

    await chat_repo.remove_by_chat_id(cmu.chat.id)


async def on_startup(dp: Dispatcher):
    dp.bot.data["messages"] = utils.parse_messages(MESSAGES_PATH)

    dp.bot.data["db_conn"] = db_conn = sqlite.connect(DATABASE_PATH)
    ChatRepository(db_conn).create_table()

    await dp.bot.set_webhook(DOMAIN + WH_PATH)


async def on_shutdown(dp: Dispatcher):
    dp.bot.data["db_conn"].close()


def main() -> None:
    executor.start_webhook(dp, WH_PATH, on_startup=on_startup)


if __name__ == "__main__":
    main()
