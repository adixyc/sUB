import os
import re
import asyncio
import random
import time
from datetime import datetime
from threading import Thread
from flask import Flask

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

# ---------------- WEB SERVER ---------------- #

app = Flask(__name__)

@app.route('/')
def home():
    return "adubot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web).start()

# ---------------- TELEGRAM CONFIG ---------------- #

api_id = 37282522
api_hash = '689041412e1abb0f86b19975b4c06b86'

session = "1BVtsOIMBu52GYeciAlqB0mdrvECihota_NZjDM5ozkkRNPEObRNvu8Prp5TyxddgdBqGhEIJrB2ginUN5Qq93XveVJb0_-3DK4EJKRdVC6gmZB8W0LAT-IGOFsKUeJQxc-BrvReo-oT8MZYfeiDZTR0h3rQ1RU2OlDnr_JnpN0w9bl-c0IECORMxLHzc_90l7w7Qr6bIkpPKi8M0pJhiDUFrb1l53aKCNfZ9bE_x4vzkJh2TUNI_B-Us0wOtnbOgv3mWnyKnJMwjJNik83fqplU6wqPfiaf3S4YUfvjVZL46mr3ebjq7-JZv8_xzaxr1Ohml11bg97WQdPlxzaFZOqV1IVkWTxU="

client = TelegramClient(StringSession(session), api_id, api_hash)

TARGET_GROUP_ID = -1003623091628
GROUP_LINK = "@SWAPPINGe_WIFE"

replied_users = set()
start_time = time.time()

quotes = [
    "HeIIo",
    "Hey Boys",
    "Adds Me",
    "HeIIo Boys",
    "I'm OnIine",
    "F17 from DeIhi",
    "Try not to c*m chaIIenge"
]

# ---------------- BIO CHECK ---------------- #

ALLOWED_USERNAMES = [
    "@SWAPPINGe_WIFE",
    "@STAR_Shana",
    "@niximia"
]

async def has_link_in_bio(user_id):
    try:
        full = await client(GetFullUserRequest(user_id))
        bio = full.full_user.about or ""

        # remove allowed usernames
        for allowed in ALLOWED_USERNAMES:
            bio = bio.replace(allowed, "")

        patterns = [
            r"@\w+",
            r"t\.me/\w+",
            r"http[s]?://",
            r"www\."
        ]

        for pattern in patterns:
            if re.search(pattern, bio, re.IGNORECASE):
                return True

        return False

    except Exception as e:
        print("Bio check error:", e)
        return False

# ---------------- BACKGROUND TASKS ---------------- #

async def fake_typing():
    while True:
        try:
            async with client.action(TARGET_GROUP_ID, 'typing'):
                await asyncio.sleep(random.randint(6, 12))
        except Exception as e:
            print("Typing Error:", e)
            await asyncio.sleep(15)

async def send_quotes():
    while True:
        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            if dialog.is_group:
                try:
                    await client.send_message(
                        dialog.id,
                        random.choice(quotes)
                    )

                    await asyncio.sleep(40)

                except Exception:
                    pass

        await asyncio.sleep(330)

# ---------------- PRIVATE AUTO REPLY ---------------- #

@client.on(events.NewMessage(incoming=True))
async def private_auto_reply(event):

    if event.is_private and not event.out:

        user_id = event.sender_id

        if user_id not in replied_users:

            replied_users.add(user_id)

            await asyncio.sleep(2)

            await event.respond(
                f"Hi dear ❤️\n"
                f"Thank you for messaging me.\n\n"
                f"Please join our group:\n"
                f"{GROUP_LINK}\n\n"
                f"After joining, message me again 💋\n\n"
                f"Don't leave the group. Couple show will begin soon 🥰"
            )

# ---------------- KEYWORD REPLY ---------------- #

@client.on(events.NewMessage(incoming=True, pattern=r'(?i)^demo$'))
async def demo_reply(event):

    if event.is_private:
        await event.reply("demo paid hai babe.. 100rs only")

# ---------------- GROUP WELCOME ---------------- #

@client.on(events.ChatAction(chats=TARGET_GROUP_ID))
async def welcome_new_user(event):

    if event.user_joined or event.user_added:

        users = await event.get_users()

        for user in users:

            name = user.first_name or "User"

            message = f"Hello {name}, DM ME FOR FUN BABY 💋"

            entity = MessageEntityMentionName(
                offset=6,
                length=len(name),
                user_id=user.id
            )

            await client.send_message(
                TARGET_GROUP_ID,
                message,
                formatting_entities=[entity]
            )

# ---------------- DELETE USERS WITH LINKS IN BIO ---------------- #

@client.on(events.NewMessage(chats=TARGET_GROUP_ID))
async def delete_users_with_links(event):

    try:
        sender = await event.get_sender()

        # ignore bots and yourself
        if sender.bot or sender.is_self:
            return

        bad_bio = await has_link_in_bio(sender.id)

        if bad_bio:

            await event.delete()

            print(f"Deleted message from {sender.id}")

    except Exception as e:
        print("Delete Error:", e)

# ---------------- COMMANDS ---------------- #

@client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping(event):

    start = time.time()

    msg = await event.edit("Pinging...")

    end = time.time()

    await msg.edit(f"PONG! {round((end-start)*1000)} ms")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def get_id(event):

    await event.edit(f"CHAT ID: `{event.chat_id}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.time"))
async def time_cmd(event):

    now = datetime.now().strftime("%H:%M:%S")

    await event.edit(f"CURRENT TIME: {now}")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.alive"))
async def alive(event):

    uptime = int(time.time() - start_time)

    await event.edit(f"⚡ Alive\nUptime: {uptime} sec")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.block"))
async def block_user(event):

    if event.is_private:

        await client(BlockRequest(event.chat_id))

        await event.edit("Blocked.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.unblock"))
async def unblock_user(event):

    if event.is_private:

        await client(UnblockRequest(event.chat_id))

        await event.edit("Unblocked.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.spam"))
async def spam(event):

    args = event.raw_text.split(maxsplit=2)

    if len(args) < 3:
        return await event.edit("Usage: .spam count text")

    count = int(args[1])
    text = args[2]

    await event.delete()

    for _ in range(count):
        await client.send_message(event.chat_id, text)

@client.on(events.NewMessage(outgoing=True, pattern=r"\.dm"))
async def price_list(event):

    text = """
🌸 VC SERVICE - @STAR_NAVYA
🌸 TG/WA ID - @niximia
"""

    await event.edit(text)

# ---------------- AUTO DELETE ALL GROUP MSGS ---------------- #

@client.on(events.NewMessage(chats=TARGET_GROUP_ID))
async def auto_delete_group_messages(event):

    try:
        await asyncio.sleep(60)

        await event.delete()

    except Exception as e:
        print("Auto-delete error:", e)

# ---------------- MAIN ---------------- #

async def main():

    await client.start()

    print("Userbot running...")

    asyncio.create_task(fake_typing())
    asyncio.create_task(send_quotes())

    await client.run_until_disconnected()

keep_alive()
asyncio.run(main())
