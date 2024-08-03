import discord
from discord import Embed

import ast
import datetime
import os.path
import subprocess
import time
import sys


UPDATE_FLAG_PATH = "./.updated"

MESSAGE_TIMER = [0.0, 15.0, 60.0, 120.0]


def message_embed(title, text, color):
    if len(title) <= 0:
        return Embed(
            description=text,
            colour=color
        )
    elif len(text) <= 0:
        return Embed(
            title=title,
            colour=color
        )
    else:
        return Embed(
            title=title,
            description=text,
            colour=color
        )


def embed_chain(title, text, color, sep=" "):
    if len(text) <= 4096:
        return [message_embed(title, text, color)]
    else:
        embeds = []
        tokens = text.split(sep=sep)
        description = ""
        title_flag = True

        for token in tokens:
            if len(token) + len(description) <= 4096:
                description += token + sep
            else:
                if not title_flag:
                    embeds.append(message_embed("", description, color))
                else:
                    embeds.append(message_embed(title, description, color))
                    title_flag = False

                description = token

        if len(description) > 0:
            embeds.append(message_embed("", description, color))

        return embeds


def error_embed(text):
    return message_embed("", text, 0xf50000)


def header_error_embed(title):
    return message_embed(title, "", 0xf50000)


def info_embed(text):
    return message_embed("", text, 0x00b0f4)


def full_info_embed(title, text):
    return message_embed(title, text, 0x00b0f4)


def music_cover_embed(title):
    return message_embed(title, "", 0xff622e)


def full_music_cover_embed(title, text):
    return message_embed(title, text, 0xff622e)


def separate_date(date: str):
    return date[-2:] + "." + date[-4:-2] + "." + date[:-4]


def read_config(path):
    with open(path, "r", encoding="utf-8") as config_file:
        config = ast.literal_eval(config_file.read())

    config_file.close()

    return config["discord-main-token"], config["yandex-token"], config["server"], config["channel"], config["admins"]


async def show_patchonote(client, channel):
    with open("./PATCHNOTE.md", "r", encoding="utf-8") as patch_note:
        lines = patch_note.readlines()

    patch_note.close()

    if len(lines) > 0:
        description = ""

        for i in range(1, len(lines)):
            description += lines[i] + "\n"

        await (await client.fetch_channel(int(channel))).send(embed=Embed(title=lines[0], description=description))


async def show_update_info(client, channel):
    global UPDATE_FLAG_PATH

    if os.path.exists(UPDATE_FLAG_PATH):
        await show_patchonote(client, channel)
        os.remove(UPDATE_FLAG_PATH)


def restart_bot():
    os.system(f"echo \"python3 ./main.py\" | at -t {datetime.datetime.fromtimestamp(time.time()) + datetime.timedelta(seconds=10)}")
    sys.exit()


async def update_bot(ctx: discord.ApplicationContext):
    try:
        subprocess.run(["git", "pull"])

        with open("./.updated", "w", encoding="utf-8") as flag_file:
            flag_file.close()

        restart_bot()
    except Exception as e:
        await ctx.followup.send(f"При обновлении произошла ошибка: {e}", ephemeral=True)


def check_date(day, month):
    try:
        datetime.datetime(datetime.datetime.utcnow().date().year, month, day)
        return True
    except Exception as e:
        print(e)
        return False
