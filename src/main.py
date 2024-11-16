import os
import sys
import a2s
import asyncio

from typing import Dict, Any

from disnake.ext import commands
from disnake import Activity, ActivityType
from src.utils import log


class DiscordBot(commands.InteractionBot):

    def __init__(self, server_dict: Dict[str, Any]):
        super().__init__(heartbeat_timeout=300)
        self.server_dict = server_dict

    def __restart_bot(self) -> None:
        """Restart Bot"""
        python = sys.executable
        os.execl(python, python, '-B', *sys.argv)

    def __get_time_emoji(self, keywords: str) -> str:
        """Return emoji by time"""
        try:
            time_str = keywords.split(",")[-1].strip()
            return "🌕" if "05:00" <= time_str < "20:00" else "🌑"
        except (IndexError, ValueError):
            return "🕑"

    async def __get_server_info(self) -> a2s.SourceInfo:
        """Return server info"""
        try:
            return await a2s.ainfo(
                address=(self.server_dict["ip"], self.server_dict["port"])
            )
        except Exception:
            return False

    async def on_ready(self) -> None:
        log.info(f"[BOT] {self.server_dict['name']} started")
        await self.update_status(self)

    async def update_status(self, bot: commands.Bot) -> None:
        while True:
            try:
                server_info = await self.__get_server_info()

                if server_info:
                    status = self.server_dict["status_online"].format(
                        player = server_info.player_count,
                        slot = server_info.max_players,
                        time = server_info.keywords.split(",")[-1],
                        emoji = self.__get_time_emoji(server_info.keywords)
                    )
                    log.info(f"[BOT] {self.server_dict['name']} - {status}")
                else:
                    status = self.server_dict["status_offline"]
                    log.info(f"[BOT] {self.server_dict['name']} - {status}")

                await bot.change_presence(activity=Activity(type=ActivityType.custom, name="-", state=status))
                await asyncio.sleep(60)

            except Exception as e:
                log.error(f"[BOT] An error occurred during status updates {self.server_dict['name']}\n╰─> Error: {e}")
                await asyncio.sleep(30)
                self.__restart_bot()
