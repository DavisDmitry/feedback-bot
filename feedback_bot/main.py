import logging
import os

from aiogram import Bot, Dispatcher, executor, types

from feedback_bot import utils

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TOKEN = os.environ["BOT_TOKEN"]
DOMAIN = os.environ["BOT_DOMAIN"]
TEXTS_PATH = os.getenv("TEXTS_PATH", "/data")
WH_PATH = "/" + utils.generate_random_string()


logging.basicConfig(level=LOG_LEVEL.upper())


bot = Bot(TOKEN, parse_mode="html")
dp = Dispatcher(bot)


@dp.message_handler(commands=("start", "help"))
async def start_help(msg: types.Message):
    await msg.answer(msg.bot.data.get("texts").get("start"))


async def on_startup(dp: Dispatcher):
    path = TEXTS_PATH.rstrip("/")
    keys = ("start",)
    dp.bot.data["texts"] = texts = {}
    for key in keys:
        with open(f"{path}/{key}.txt", "r") as file:
            texts[key] = file.read()

    await dp.bot.set_webhook(DOMAIN + WH_PATH)


def main() -> None:
    executor.start_webhook(dp, WH_PATH, on_startup=on_startup)


if __name__ == "__main__":
    main()
