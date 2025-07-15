from pprint import pprint

from dotenv import load_dotenv
import os
import glob
import json

from telethon import TelegramClient, events
from telethon.tl.types import (
    UpdateBotNewBusinessMessage,
    UpdateBotDeleteBusinessMessage,
    UpdateBotEditBusinessMessage,
    UpdateBotBusinessConnect,
    PeerUser,
    InputDocument,
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeVideo,
    DocumentAttributeAudio, DocumentAttributeSticker, DocumentAttributeAnimated, DocumentAttributeImageSize,
)
from database import save_message, get_message_by_id, save_owner_id, get_owner_id, delete_message_from_database, \
    delete_owner_id, connection_id_exists, rewrite_connection_id, get_old_connection_id_by_owner_id
import datetime
from encryption import encrypt_message, decrypt_message

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
API_TOKEN = os.getenv("API_TOKEN")

bot = TelegramClient("bot_session", API_ID, API_HASH)
bot.start(bot_token=API_TOKEN)


# --- Обработка бизнес-подключения ---
@bot.on(events.Raw())
async def handle_business_connection(event):
    if isinstance(event, UpdateBotBusinessConnect):
        connection = event.connection
        owner_id = connection.user_id
        connection_id = connection.connection_id
        print(connection.disabled)
        print(connection_id_exists(owner_id))
        if connection.disabled:
            print("Bot discconect")
        else:
            if connection_id_exists(owner_id):
                old_connection_id = get_old_connection_id_by_owner_id(owner_id)
                rewrite_connection_id(old_connection_id, connection_id)
                print("Bot online")
            else:
                save_owner_id(owner_id, connection_id)


@bot.on(events.Raw())
async def hadnle_analitc(event):
    data = event
    pprint(data.to_dict())


# --- Обработка бизнес-сообщений ---
@bot.on(events.Raw())
async def handle_business_messages(event):
    # Обработка нового сообщенния
    if isinstance(event, UpdateBotNewBusinessMessage):
        message = event.message
        message_connection_id = event.connection_id
        reply = event.reply_to_message

        if reply and reply.media and hasattr(reply.media, 'ttl_seconds') and reply.media.ttl_seconds:
            owner_id = get_owner_id(message_connection_id)
            photo_path = await bot.download_media(reply.media, file=f"images/{owner_id}.jpg")
            await bot.send_file(owner_id, photo_path)
            os.remove(photo_path)

        if isinstance(message.peer_id, PeerUser):
            user_id = message.peer_id.user_id
            user_info = await bot.get_entity(user_id)
            username = f"@{user_info.username}" if user_info.username else user_info.first_name
            message_text = encrypt_message(message.message, get_owner_id(message_connection_id))
            message_id = message.id
            date = datetime.datetime.now().isoformat()
            print(f"📩 Збережено від {username}: {message_text}")

            if isinstance(message.media, MessageMediaPhoto):
                # это фото
                await bot.download_media(message.media, file=f"images/{message.id}.jpg")
                save_message(message_connection_id, message_id, user_id, username, "photo", message_text, date)

            elif isinstance(message.media, MessageMediaDocument):
                doc = message.media.document
                mime = (doc.mime_type or "").lower()
                for attr in doc.attributes:

                    # ────── АНИМИРОВАННЫЙ СТИКЕР / «GIF» (VIDEO/MP4) ──────
                    if isinstance(attr, (DocumentAttributeSticker, DocumentAttributeVideo)) \
                            and mime == "video/webm":

                        doc = message.media.document
                        info = {
                            "doc_id": doc.id,
                            "access_hash": doc.access_hash,
                            "file_ref": doc.file_reference.hex(),
                            "mime": doc.mime_type
                        }
                        save_message(message_connection_id, message_id, user_id, username,
                                     "gif", json.dumps(info), date)
                        break


                    elif isinstance(attr,
                                    (DocumentAttributeSticker, DocumentAttributeImageSize)) and mime == "image/webp":
                        file_path = f"stickers/{message.id}.webp"
                        await bot.download_media(message.media, file=file_path)
                        print("🟠 Статический стикер")
                        save_message(message_connection_id, message_id, user_id, username, "sticker",
                                     message_text, date)
                        break

                    elif isinstance(attr, DocumentAttributeAudio) and attr.voice:
                        print("🎧 Голосовое сообщение")
                        await bot.download_media(message.media, file=f"voices/{message.id}.ogg")
                        save_message(message_connection_id, message_id, user_id, username, "voice", message_text, date)
                        break

                    elif isinstance(attr, DocumentAttributeVideo) and attr.round_message:
                        print("🔵 Видеокружок")
                        await bot.download_media(message.media, file=f"rounds/{message.id}.mp4")
                        save_message(message_connection_id, message_id, user_id, username, "round", message_text, date)
                        break

                    elif isinstance(attr, DocumentAttributeVideo):
                        print("🎥 Видео")
                        await bot.download_media(message.media, file=f"videos/{message.id}.mp4")
                        save_message(message_connection_id, message_id, user_id, username, "video", message_text, date)
                        break

                    else:
                        print("📎 Документ/файл")
                        await bot.download_media(message.media, file=f"files/{message.id}")
                        save_message(message_connection_id, message_id, user_id, username, "file", message_text, date)

            else:
                save_message(message_connection_id, message_id, user_id, username, "text", message_text, date)

    # Обработка удаленного сообщенния
    elif isinstance(event, UpdateBotDeleteBusinessMessage):
        msg_ids = event.messages
        for msg_id in msg_ids:
            row = get_message_by_id(msg_id)
            delete_message_from_database(msg_id)
            if row:
                connection_id, username, type_message, text = row
                print(connection_id)
                print(type(type_message))
                owner_id = get_owner_id(connection_id)
                type_map = {
                    "photo": ("photos", "удалил фото"),
                    "voice": ("voices", "удалил голосовое"),
                    "round": ("rounds", "удалил кружок"),
                    "video": ("videos", "удалил видео"),
                    "file": ("files", "удалил файл"),
                    "gif": ("gifs", "удалил гифку"),
                    "sticker": ("stickers", "удалил стикер")
                }

                if type_message in type_map:
                    folder, label = type_map[type_message]

                    if type_message == "gif":
                        data = json.loads(text)  # text = JSON-строка из save_message
                        input_doc = InputDocument(
                            id=data["doc_id"],
                            access_hash=data["access_hash"],
                            file_reference=bytes.fromhex(data["file_ref"])
                        )

                        await bot.send_message(owner_id, f"{username} удалил гифку:")
                        await bot.send_file(owner_id, input_doc, force_document=False)


                    files = glob.glob(f"{folder}/{msg_id}.*")
                    if files:
                        await bot.send_message(owner_id, f"{username} {label}:")
                        await bot.send_file(owner_id, files[0], force_document=False)
                        os.remove(files[0])
                else:
                    messages_text = decrypt_message(text, owner_id)
                    await bot.send_message(owner_id, f"{username} удалил сообщение: {messages_text}")
            else:
                print(f"⚠️ Сообщение с ID {msg_id} не найдено в базе\n")

    # Обработка отредактированого сообщенния
    elif isinstance(event, UpdateBotEditBusinessMessage):
        msg = event.message
        row = get_message_by_id(msg.id)
        if msg.from_id:
            print("⚠️ Отредактированно ботом!")
        elif row:
            connection_id, username, text, = row
            owner_id = get_owner_id(connection_id)
            messages_text = decrypt_message(text, owner_id)
            await bot.send_message(owner_id,
                                   f"{username} отредактировал сообщение {messages_text} на {msg.message} ")
        else:
            print(f"⚠️ Сообщение с ID {msg.id} не найдено в базе\n")


# --- Обработка команды /start ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    owner_id = event.sender_id
    print(f"🆔 Новый пользователь: {owner_id}")
    await event.respond("Привет, я бот для отслеживания удалённых и изменённых сообщений.")


def main():
    print("🤖 Бот очікує бізнес-повідомлення...")
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
