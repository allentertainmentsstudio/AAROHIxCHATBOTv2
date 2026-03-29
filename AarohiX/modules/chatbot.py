import random
from Abg.chat_status import adminsOnly

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message

from config import MONGO_URL
from AarohiX import AarohiX
from AarohiX.modules.helpers import CHATBOT_ON


@AarohiX.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_(_, m: Message):
    await m.reply_text(
        f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )


# ================= TEXT HANDLER ================= #

@AarohiX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot,
    group=4,
)
async def chatbot_text(client: Client, message: Message):

    try:
        if message.text and message.text.startswith(("!", "/", "?", "@", "#")):
            return
    except Exception:
        pass

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    # ----------- NO REPLY CASE ----------- #
    if not message.reply_to_message:
        dil = MongoClient(MONGO_URL)["DilDb"]["Dil"]
        is_dil = dil.find_one({"chat_id": message.chat.id})

        if not is_dil:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)

            data = list(chatai.find({"word": message.text}))
            if data:
                reply = random.choice(data)
                if reply["check"] == "sticker":
                    await message.reply_sticker(reply["text"])
                else:
                    await message.reply_text(reply["text"])

    # ----------- REPLY CASE ----------- #
    else:
        user = message.reply_to_message.from_user

        dil = MongoClient(MONGO_URL)["DilDb"]["Dil"]
        is_dil = dil.find_one({"chat_id": message.chat.id})

        # Reply to bot
        if user and user.id == client.id:
            if not is_dil:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)

                data = list(chatai.find({"word": message.text}))
                if data:
                    reply = random.choice(data)
                    if reply["check"] == "sticker":
                        await message.reply_sticker(reply["text"])
                    else:
                        await message.reply_text(reply["text"])

        # Learning mode
        elif user and user.id != client.id:
            if message.sticker:
                if not chatai.find_one({
                    "word": message.reply_to_message.text,
                    "id": message.sticker.file_unique_id
                }):
                    chatai.insert_one({
                        "word": message.reply_to_message.text,
                        "text": message.sticker.file_id,
                        "check": "sticker",
                        "id": message.sticker.file_unique_id
                    })

            if message.text:
                if not chatai.find_one({
                    "word": message.reply_to_message.text,
                    "text": message.text
                }):
                    chatai.insert_one({
                        "word": message.reply_to_message.text,
                        "text": message.text,
                        "check": "none"
                    })


# ================= STICKER HANDLER ================= #

@AarohiX.on_message(
    (filters.sticker | filters.group) & ~filters.private & ~filters.bot,
    group=4,
)
async def chatbot_sticker(client: Client, message: Message):

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if message.reply_to_message:
        user = message.reply_to_message.from_user

        # Reply to bot
        if user and user.id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Learning
        elif user and user.id != client.id:

            if message.text:
                if not chatai.find_one({
                    "word": message.reply_to_message.sticker.file_unique_id,
                    "text": message.text
                }):
                    chatai.insert_one({
                        "word": message.reply_to_message.sticker.file_unique_id,
                        "text": message.text,
                        "check": "text"
                    })

            if message.sticker:
                if not chatai.find_one({
                    "word": message.reply_to_message.sticker.file_unique_id,
                    "text": message.sticker.file_id
                }):
                    chatai.insert_one({
                        "word": message.reply_to_message.sticker.file_unique_id,
                        "text": message.sticker.file_id,
                        "check": "none"
                    })


# ================= PRIVATE TEXT ================= #

@AarohiX.on_message(
    (filters.text | filters.sticker) & filters.private & ~filters.bot,
    group=4,
)
async def chatbot_pvt(client: Client, message: Message):

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        data = list(chatai.find({"word": message.text}))
        if data:
            reply = random.choice(data)

            if reply["check"] == "sticker":
                await message.reply_sticker(reply["text"])
            else:
                await message.reply_text(reply["text"])

    else:
        user = message.reply_to_message.from_user

        if user and user.id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)


# ================= PRIVATE STICKER ================= #

@AarohiX.on_message(
    (filters.sticker) & filters.private & ~filters.bot,
    group=4,
)
async def chatbot_sticker_pvt(client: Client, message: Message):

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        data = list(chatai.find({"word": message.sticker.file_unique_id}))
        if data:
            reply = random.choice(data)

            if reply["check"] == "text":
                await message.reply_text(reply["text"])
            else:
                await message.reply_sticker(reply["text"])

    else:
        user = message.reply_to_message.from_user

        if user and user.id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
