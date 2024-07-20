import ast
import asyncio
import subprocess
import sys

from discord import Embed

MESSAGE_TIMER = [0.0, 15.0, 60.0, 120.0]


def read_config(path):
    with open(path, "r", encoding="utf-8") as config_file:
        config = ast.literal_eval(config_file.read())

    config_file.close()

    return config["token"], config["server"], config["admins"]


async def update_bot(interaction):
    try:
        subprocess.run(["git", "pull"])
        subprocess.run([sys.executable, "main.py"])

        with open("./PATCHNOTE.md", "r", encoding="utf-8") as patch_note:
            lines = patch_note.readlines()

        description = ""

        for i in range(1, len(lines)):
            description += lines[i] + "\n"

        await interaction.followup.send(embed=Embed(title=lines[0], description=description, colour=0x00b0f4))

        sys.exit()

    except Exception as e:
        await interaction.followup.send(f"При обновлении произошла ошибка: {e}", ephemeral=True)
