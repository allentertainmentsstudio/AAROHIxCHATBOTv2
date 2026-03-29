import random
from Abg.chat_status import adminsOnly

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message

from config import MONGO_URL
from AarohiX import AarohiX
from AarohiX.modules.helpers import CHATBOT_ON, is_admins


@AarohiX.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_(_, m: Message):
    await m.reply_text(
        f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )
    return


def is_command(text):
    if not text:
        return False
    return text.startswith(("!", "/", "?", "@", "#"))


def get_random_reply(chatai, word_key):
    if not word_key:
        return None, "none"
    is_chat = chatai.find({"word": word_key})
    K = [x["text"] for x in is_chat]
    if not K:
        return None, "none"
    hey = random.choice(K)
    is_text = chatai.find_one({"text": hey})
    if not is_text:
        return hey, "none"
    return hey, is_text.get("check", "none")


async def reply_based_on_type(message, hey, check_type):
    if not hey:
        return
    if check_type == "sticker":
        await message.reply_sticker(hey)
    else:
        await message.reply_text(hey)


@AarohiX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_text(client: Client, message: Message):
    try:
        if is_command(getattr(message, "text", None)):
            return
    except Exception:
        pass

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    dildb = MongoClient(MONGO_URL)
    dil = dildb["DilDb"]["Dil"]
    is_dil = dil.find_one({"chat_id": message.chat.id})

    if not message.reply_to_message:
        if not is_dil:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            word_key = getattr(message, "text", None)
            hey, check_type = get_random_reply(chatai, word_key)
            await reply_based_on_type(message, hey, check_type)
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        replied_id = message.reply_to_message.from_user.id
        word_key = getattr(message.reply_to_message, "text", None)
        if replied_id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            word_key = getattr(message, "text", None)
            hey, check_type = get_random_reply(chatai, word_key)
            await reply_based_on_type(message, hey, check_type)
        else:
            if getattr(message, "sticker", None):
                is_chat = chatai.find_one(
                    {"word": word_key, "id": message.sticker.file_unique_id}
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": word_key,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id,
                        }
                    )
            if getattr(message, "text", None):
                is_chat = chatai.find_one({"word": word_key, "text": message.text})
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": word_key,
                            "text": message.text,
                            "check": "none",
                        }
                    )


@AarohiX.on_message(
    (filters.sticker | filters.group | filters.text) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker(client: Client, message: Message):
    try:
        if is_command(getattr(message, "text", None)):
            return
    except Exception:
        pass

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    dildb = MongoClient(MONGO_URL)
    dil = dildb["DilDb"]["Dil"]
    is_dil = dil.find_one({"chat_id": message.chat.id})

    if not message.reply_to_message:
        if not is_dil:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            word_key = getattr(message.sticker, "file_unique_id", None)
            hey, check_type = get_random_reply(chatai, word_key)
            await reply_based_on_type(message, hey, check_type)
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        replied_id = message.reply_to_message.from_user.id
        word_key = getattr(message.reply_to_message, "sticker", None)
        if replied_id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            word_key = getattr(message, "text", None) or getattr(message, "sticker", None)
            hey, check_type = get_random_reply(chatai, word_key)
            await reply_based_on_type(message, hey, check_type)
        else:
            if getattr(message, "text", None):
                is_chat = chatai.find_one(
                    {"word": getattr(message.reply_to_message.sticker, "file_unique_id", None), "text": message.text}
                )
                if not is_chat:
                    chatai.insert_one(
                        {"word": getattr(message.reply_to_message.sticker, "file_unique_id", None),
                         "text": message.text, "check": "text"}
                    )
            if getattr(message, "sticker", None):
                is_chat = chatai.find_one(
                    {"word": getattr(message.reply_to_message.sticker, "file_unique_id", None), "text": message.sticker.file_id}
                )
                if not is_chat:
                    chatai.insert_one(
                        {"word": getattr(message.reply_to_message.sticker, "file_unique_id", None),
                         "text": message.sticker.file_id, "check": "none"}
                    )


@AarohiX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_pvt(client: Client, message: Message):
    try:
        if is_command(getattr(message, "text", None)):
            return
    except Exception:
        pass

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    word_key = getattr(message, "text", None) or getattr(message, "sticker", None)
    hey, check_type = get_random_reply(chatai, word_key)
    await reply_based_on_type(message, hey, check_type)
