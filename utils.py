import ast
import os.path
import subprocess
import time

from datetime import datetime, timedelta
from discord import Embed


UPDATE_FLAG_PATH = "./.updated"

MESSAGE_TIMER = [0.0, 15.0, 60.0, 120.0]


def read_config(path):
    with open(path, "r", encoding="utf-8") as config_file:
        config = ast.literal_eval(config_file.read())

    config_file.close()

    return config["token"], config["server"], config["admins"]


async def show_patchonote(client):
    if os.path.exists(UPDATE_FLAG_PATH):
        with open("./PATCHNOTE.md", "r", encoding="utf-8") as patch_note:
            lines = patch_note.readlines()

        patch_note.close()

        description = ""

        for i in range(1, len(lines)):
            description += lines[i] + "\n"

        await client.get_channel(1264218377879162954).send(embed=Embed(title=lines[0], description=description))

        os.remove(UPDATE_FLAG_PATH)


async def update_bot(interaction):
    try:
        subprocess.run(["git", "pull"])

        with open("./.updated", "w", encoding="utf-8") as flag_file:
            flag_file.close()

        os.system(f"echo \"python3 ./main.py\" | at -t {datetime.fromtimestamp(time.time()) + timedelta(seconds=10)}")

        quit(0)
    except Exception as e:
        await interaction.followup.send(f"При обновлении произошла ошибка: {e}", ephemeral=True)
