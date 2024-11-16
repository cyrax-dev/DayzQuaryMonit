import asyncio
from typing import Dict, Any

from disnake import errors
from dynaconf import Dynaconf

from src.main import DiscordBot
from src.utils import log

config = Dynaconf(settings_files=['./settings/config.json'])


async def start_bot(server_dict: Dict[str, Any]) -> None:
    try:
        bot = DiscordBot(server_dict)
        await bot.start(server_dict["token"])

    except errors.LoginFailure:
        log.error(f"[BOT] Неверный токен {server_dict["name"]}")
    except Exception as e:
        log.error(f"[BOT] Произошла ошибка при запуске {server_dict["name"]}\n╰─> Ошибка: {e}")


async def main() -> None:
    tasks = [asyncio.create_task(start_bot(server)) for server in config.servers]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
