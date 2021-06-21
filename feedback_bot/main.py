import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import IDFilter

from feedback_bot import utils

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TOKEN = os.environ["BOT_TOKEN"]
DOMAIN = os.environ["BOT_DOMAIN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
TEXTS_PATH = os.getenv("TEXTS_PATH", "/data")
WH_PATH = "/" + utils.generate_random_string()


logging.basicConfig(level=LOG_LEVEL.upper())


bot = Bot(TOKEN, parse_mode="html")
dp = Dispatcher(bot)


@dp.message_handler(commands=("start", "help"))
async def start_help(msg: types.Message):
    await msg.answer(msg.bot.data.get("texts").get("start"))


@dp.message_handler(
    IDFilter(chat_id=ADMIN_ID),
    content_types=types.ContentType.ANY,
    run_task=True,
    is_reply=True,
)
async def reply_from_admin(msg: types.Message):
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


@dp.message_handler(content_types=types.ContentType.ANY, run_task=True)
async def msg_from_user(msg: types.Message):
    msg_to_reply = await msg.forward(ADMIN_ID)
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
