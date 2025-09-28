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
PENDING = {}


@colab_bot.on_message((filters.command("start")) & (filters.private | filters.group) & ~filters.channel)
async def start(client, message):
    await message.delete()
    text = "**Hey There, 👋🏼 It's Colab Leecher**\n\n◲ I am a Powerful File Transloading Bot 🚀\n◲ I can Transfer Files To Telegram or Your Google Drive From Various Sources 🦐"
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
        BOT.Mode.type = "normal"
        BOT.Mode.dest = "telegram"
        BOT.SOURCE = [args[1].strip()]
        await taskScheduler()
        return
    if message.reply_to_message and (getattr(message.reply_to_message, "document", None) or getattr(message.reply_to_message, "video", None) or getattr(message.reply_to_message, "audio", None)):
        await message.reply_text("📎 File đang ở Telegram sẵn rồi — không cần /tupload.", quote=True)
        return
    await message.reply_text("Dùng: `/tupload https://link` hoặc gửi link rồi chọn nơi upload.", quote=True)

@colab_bot.on_message(filters.command("gdupload_disabled"))
async def drive_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("drupload_disabled"))
async def directory_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me FOLDER PATH 🔗»</b>\n\n🦀 Below is an example\n\n<code>/home/user/Downloads/bot</code>"

    src_request_msg = await task_starter(message, text)



@colab_bot.on_message(filters.command("ytd") & filters.group)
async def ytd_command(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("Vui lòng gửi kèm link ngay sau lệnh, ví dụ: `/ytd https://youtu.be/...`", quote=True)
        return
    link = args[1].strip()
    PENDING.setdefault((message.chat.id, message.id), {"type":"link", "data":[link], "ytdl": True})
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Upload lên Telegram", callback_data="dest_tg")],
                               [InlineKeyboardButton("Upload lên Filebin", callback_data="dest_fb")]])
    await message.reply_text("Chọn nơi upload:", reply_markup=kb, quote=True)

@colab_bot.on_message((filters.command("settings")) & (filters.private | filters.group) & ~filters.channel)
async def settings(client, message):
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


@colab_bot.on_message(filters.reply)
async def setPrefix(client, message):
    global BOT, SETTING
    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False

        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False

        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()



@colab_bot.on_message(filters.create(isLink) & ~filters.photo & filters.group)
async def handle_url(client, message):
    # Ask destination when a link is posted without command
    PENDING.setdefault((message.chat.id, message.id), {"type":"link", "data": message.text.splitlines(), "ytdl": False})
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Upload lên Telegram", callback_data="dest_tg")],
                               [InlineKeyboardButton("Upload lên Filebin", callback_data="dest_fb")]])
    await message.reply_text("Chọn nơi upload:", reply_markup=kb, quote=True)

@colab_bot.on_message(filters.photo & filters.private)
async def handle_image(client, message):
    msg = await message.reply_text("<i>Trying To Save Thumbnail...</i>")
    success = await setThumbnail(message)
    if success:
        await msg.edit_text("**Thumbnail Successfully Changed ✅**")
        await message.delete()
    else:
        await msg.edit_text(
            "🥲 **Couldn't Set Thumbnail, Please Try Again !**", quote=True
        )
    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message((filters.command("setname")) & (filters.private | filters.group) & ~filters.channel)
async def custom_name(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/setname <code>custom_fileame.extension</code>\nTo Set Custom File Name 📛",
            quote=True,
        )
    else:
        BOT.Options.custom_name = message.command[1]
        msg = await message.reply_text(
            "Custom Name Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message((filters.command("zipaswd")) & (filters.private | filters.group) & ~filters.channel)
async def zip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/zipaswd <code>password</code>\nTo Set Password for Output Zip File. 🔐",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text(
            "Zip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message((filters.command("unzipaswd")) & (filters.private | filters.group) & ~filters.channel)
async def unzip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/unzipaswd <code>password</code>\nTo Set Password for Extracting Archives. 🔓",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text(
            "Unzip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)




@colab_bot.on_message(filters.command("fbupload") & filters.group)
async def fbupload(client, message):
    from .utility.variables import BOT
    from .utility.task_manager import taskScheduler
    from .uploader.filebin import upload_to_filebin
    import os
    args = message.text.split(maxsplit=1)
    if len(args) >= 2:
        BOT.Mode.mode = "leech"
        BOT.Mode.ytdl = False
        BOT.Mode.dest = "filebin"
        BOT.Mode.type = "normal"
        BOT.SOURCE = [args[1].strip()]
        await taskScheduler()
        return
    if message.reply_to_message and (getattr(message.reply_to_message, "document", None) or getattr(message.reply_to_message, "video", None) or getattr(message.reply_to_message, "audio", None)):
        tmp = await message.reply_to_message.download()
        link = await upload_to_filebin(tmp)
        await message.reply_text(f"[📦 Tải về]({link})", disable_web_page_preview=True)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return
    await message.reply_text("Hãy dùng `/fbupload https://link` hoặc reply vào một file bất kỳ.", quote=True)



@colab_bot.on_message((filters.document | filters.video | filters.audio) & filters.group)
async def incoming_media(client, message):
    PENDING.setdefault((message.chat.id, message.id), {"type":"tg_media", "data": message.id, "ytdl": False})
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Upload lên Filebin", callback_data="dest_fb")],
                               [InlineKeyboardButton("Upload lên Telegram", callback_data="dest_tg")]])
    await message.reply_text("Bạn muốn upload file này lên đâu?", reply_markup=kb, quote=True)

@colab_bot.on_callback_query(filters.regex("^(dest_tg|dest_fb)$"))
async def handle_destination(client, callback_query):
    from .utility.variables import BOT
    from .utility.task_manager import taskScheduler
    data = callback_query.data
    key = (callback_query.message.chat.id, callback_query.message.reply_to_message_id)
    info = PENDING.get(key)
    if not info:
        await callback_query.answer("Hết hạn hoặc không tìm thấy dữ liệu.", show_alert=True)
        return
    if data == "dest_tg":
        BOT.Mode.mode = "leech"
        BOT.Mode.dest = "telegram"
    else:
        BOT.Mode.mode = "filebin"
        BOT.Mode.dest = "filebin"
    BOT.Mode.type = "normal"
    BOT.Mode.ytdl = bool(info.get("ytdl"))
    if info["type"] == "link":
        BOT.SOURCE = info["data"]
        await taskScheduler()
    else:
        # For Telegram media: if dest is Filebin -> download file and upload to Filebin; else just notify
        if BOT.Mode.dest == "filebin":
            tmp = await callback_query.message.reply_to_message.download()
            from .uploader.filebin import upload_to_filebin
            link = await upload_to_filebin(tmp)
            await callback_query.message.reply_text(f"[📦 Tải về]({link})", disable_web_page_preview=True)
            try:
                import os; os.remove(tmp)
            except Exception: pass
        else:
            await callback_query.message.reply_text("📎 File đang ở Telegram sẵn rồi.")
    await callback_query.answer("Bắt đầu!", show_alert=False)

@colab_bot.on_message((filters.command("help")) & (filters.private | filters.group) & ~filters.channel)
async def help_command(client, message):
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
