import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import IDFilter

from feedback_bot import utils
from feedback_bot.chat_repository import AbstractChatRepository

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TOKEN = os.environ["BOT_TOKEN"]
DOMAIN = os.environ["BOT_DOMAIN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
DEFAULT_CHAT_ID = int(os.getenv("DEFAULT_CHAT_ID", ADMIN_ID))
TEXTS_PATH = os.getenv("TEXTS_PATH", "/data")
WH_PATH = "/" + utils.generate_random_string()


logging.basicConfig(level=LOG_LEVEL.upper())


bot = Bot(TOKEN, parse_mode="html")
dp = Dispatcher(bot)


@dp.message_handler(commands=("start", "help"))
async def handle_start_and_help_commands(msg: types.Message):
    await msg.answer(msg.bot.data.get("texts").get("start"))


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
        msg.bot.data.get("texts").get("forwarded_to_user").format(str(tg_id))
    )
    await asyncio.sleep(5)
    await msg_to_delete.delete()


@dp.message_handler(IDFilter(user_id=ADMIN_ID), regexp=r"/link .*")
async def handle_set_command_from_admin(msg: types.Message):
    try:
        user_id = int(msg.text.split(" ", 1)[1])
    except (IndexError, ValueError):
        # TODO: add getting text from messages.yml
        return await msg.reply(
            "Invalid command. It should be <code>/link <USER ID></code>."
        )

    chat_repo = AbstractChatRepository()  # TODO: replace this with implementation

    if await chat_repo.get_by_chat_id(msg.chat.id):
        # TODO: add getting text from messages.yml
        return await msg.reply("This chat using for communication with another user.")

    if await chat_repo.get_by_user_id(user_id):
        # TODO: add getting text from messages.yml
        return await msg.reply(
            "A chat already exists for communicating with this user."
        )

    await chat_repo.create_chat(msg.chat.id, user_id)
    # TODO: add getting text from messages.yml
    await msg.reply(
        "The chat has been successfully linked to the user with id "
        f"<code>{user_id}</code>."
    )


@dp.message_handler(
    chat_type=types.ChatType.PRIVATE, content_types=types.ContentType.ANY, run_task=True
)
async def handle_message_from_user(msg: types.Message):
    chat_repo = AbstractChatRepository()  # TODO: replace this with implementation
    admin_chat_to_forward = await chat_repo.get_by_user_id(msg.chat.id)
    chat_to_forward = admin_chat_to_forward if admin_chat_to_forward else ADMIN_ID
    msg_to_reply = await msg.forward(chat_to_forward)
    msg_to_delete = await msg.reply(msg.bot.data.get("texts").get("forwarded_to_owner"))
    await msg_to_reply.reply(f"Message from #ID{msg.from_user.id}")
    await asyncio.sleep(5)
    await msg_to_delete.delete()


async def on_startup(dp: Dispatcher):
    path = TEXTS_PATH.rstrip("/")
    keys = ("start", "forwarded_to_owner", "forwarded_to_user")
    dp.bot.data["texts"] = texts = {}
    for key in keys:
        with open(f"{path}/{key}.txt", "r") as file:
            texts[key] = file.read()

    await dp.bot.set_webhook(DOMAIN + WH_PATH)


def main() -> None:
    executor.start_webhook(dp, WH_PATH, on_startup=on_startup)


if __name__ == "__main__":
    main()
