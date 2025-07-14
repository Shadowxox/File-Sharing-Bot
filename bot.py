# (©) Codexbotz

import sys
import logging
from datetime import datetime
from aiohttp import web

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import (
    API_HASH,
    APP_ID,
    LOGGER,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL,
    CHANNEL_ID,
    PORT
)

from plugins import web_server  # Make sure this exists and returns aiohttp Application

ascii_art = """
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="CodexBotz",
            api_id=APP_ID,
            api_hash=API_HASH,
            bot_token=TG_BOT_TOKEN,
            workers=TG_BOT_WORKERS,
            plugins={"root": "plugins"}
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.username = usr_bot_me.username
        self.uptime = datetime.now()

        # ── FORCE SUBSCRIPTION HANDLER ──
        if FORCE_SUB_CHANNEL:
            try:
                chat = await self.get_chat(FORCE_SUB_CHANNEL)
                if not chat.invite_link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                self.invitelink = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.LOGGER.info(f"Force Sub Invite Link: {self.invitelink}")
            except Exception as e:
                self.LOGGER.warning(f"❌ Failed to get/export invite link for force sub channel: {e}")
                self.LOGGER.info("➡️ Make sure bot is admin in the channel with 'Add Users' permission.")
                sys.exit()

        # ── CHANNEL_ID (DB) TEST ──
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="✅ DB channel connected.")
            await test.delete()
        except Exception as e:
            self.LOGGER.warning(f"❌ Failed accessing CHANNEL_ID ({CHANNEL_ID}): {e}")
            self.LOGGER.info("➡️ Make sure bot is admin in DB channel.")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)

        # ── STARTUP MESSAGE ──
        self.LOGGER.info("🚀 Bot is now running!")
        print(ascii_art)
        print("✅ Welcome to CodeXBotz File Sharing Bot")
        print(f"🔗 t.me/{self.username}")

        # ── START WEB SERVER ──
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", int(PORT)).start()
            self.LOGGER.info(f"🌐 Web server started at port {PORT}")
        except Exception as e:
            self.LOGGER.warning(f"❌ Web server failed to start: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER.info("🛑 Bot stopped.")
