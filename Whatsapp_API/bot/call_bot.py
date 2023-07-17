import asyncio

from bot_poo import Bot
import os
import dotenv
AMBIENT = "dev"

# load env
load_env = dotenv.load_dotenv(dotenv_path=f"../config_files/.env.{AMBIENT}")

if __name__ == "__main__":
    botcito = Bot('123', 'Nahuel', )
    while botcito.action_stage != 'end':
        x = input('Val: ')
        asyncio.run(botcito.action(x))
