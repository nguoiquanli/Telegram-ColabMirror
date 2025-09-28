# copyright 2024 © Xron Trix | https://github.com/Xrontrix10


import logging, os
from pyrogram import filters
from datetime import datetime
from asyncio import sleep, get_event_loop
from colab_leecher import colab_bot, OWNER
from colab_leecher.utility.handler import cancelTask
from .utility.variables import BOT, MSG, BotTimes, Paths
from .utility.task_manager import taskScheduler, task_starter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utility.helper import isLink, setThumbnail, message_deleter, send_settings


src_request_msg = None
PENDING = {}  # (chat_id, msg_id) -> {'type': 'link'|'tg_media', 'data': [...]/message_id, 'ytdl': bool}


@colab_bot.on_message((filters.command("start")) & (filters.private | filters.group) & ~filters.channel)
async def start(client, message):
    await message.delete()
    text = "**Hey There, 👋🏼 It's Colab Leecher**\n\n◲ I am a Powerful File Transloading Bot 🚀\n◲ I can Transfer Files to Telegram or Filebin From Various Sources 🦐"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Repository 🦄",
                    url="https://github.com/nguoiquanli/Telegram-ColabMirror",
                ),
                InlineKeyboardButton("Support 💝", url="https://t.me/Colab_Leecher"),
            ],
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)


@colab_bot.on_message(filters.command("tupload") & filters.group)
async def telegram_upload(client, message):
    from .utility.variables import BOT
    from .utility.task_manager import taskScheduler
    args = message.text.split(maxsplit=1)
    if len(args) >= 2:
        BOT.Mode.mode = "leech"
        BOT.Mode.ytdl = False
        BOT.Mode.dest = "telegram"
        BOT.Mode.type = "normal"
        BOT.SOURCE = [args[1].strip()]
        await taskScheduler()
        return
    if message.reply_to_message and (message.reply_to_message.document or message.reply_to_message.video or message.reply_to_message.audio):
        await message.reply_text("📎 File đang ở Telegram sẵn rồi — không cần /tupload.", quote=True)
        return
    await message.reply_text("Dùng: `/tupload https://link` hoặc gửi link rồi chọn nơi upload.", quote=True)

def help_command(client, message):
    msg = await message.reply_text(
        "Send /start To Check If I am alive 🤨\n\nSend /colabxr and follow prompts to start transloading 🚀\n\nSend /settings to edit bot settings ⚙️\n\nSend /setname To Set Custom File Name 📛\n\nSend /zipaswd To Set Password For Zip File 🔐\n\nSend /unzipaswd To Set Password to Extract Archives 🔓\n\n⚠️ **You can ALWAYS SEND an image To Set it as THUMBNAIL for your files 🌄**",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Instructions 📖",
                        url="https://github.com/nguoiquanli/Telegram-ColabMirror/wiki/INSTRUCTIONS",
                    ),
                ],
                [
                    InlineKeyboardButton(  # Opens a web URL
                        "Channel 📣",
                        url="https://t.me/Colab_Leecher",
                    ),
                    InlineKeyboardButton(  # Opens a web URL
                        "Group 💬",
                        url="https://t.me/Colab_Leecher_Discuss",
                    ),
                ],
            ]
        ),
    )
    await sleep(15)
    await message_deleter(message, msg)


logging.info("Colab Leecher Started !")
colab_bot.run()
@colab_bot.on_message((filters.document | filters.video | filters.audio) & filters.group)
async def incoming_media(client, message):
    # Prompt for destination when a file is sent without command
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    PENDING.setdefault((message.chat.id, message.id), {"type":"tg_media", "data": message.id, "ytdl": False})
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Upload lên Filebin", callback_data="dest_fb")],
                               [InlineKeyboardButton("Upload lên Telegram", callback_data="dest_tg")]])
    await message.reply_text("Bạn muốn upload file này lên đâu?", reply_markup=kb, quote=True)


