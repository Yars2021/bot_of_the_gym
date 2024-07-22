import ast
import datetime
import discord
import json
import os

from random import randint


FILE = "./.birthday_table"

BIRTHDAYS = {}


def extract_data():
    global FILE
    global BIRTHDAYS

    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            BIRTHDAYS = ast.literal_eval(f.read())

        f.close()


def add_birthday(user_id, day, month, preferences):
    global FILE
    global BIRTHDAYS

    extract_data()

    BIRTHDAYS[str(user_id)] = [str(day), str(month), preferences]

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(BIRTHDAYS, f)

    f.close()


async def iterate(channel, guild):
    global BIRTHDAYS

    current_day = str(datetime.date.today().day)
    current_month = str(datetime.date.today().month)

    members = guild.fetch_members(limit=None)

    async for member in members:
        for user in BIRTHDAYS:
            if user == str(member.id):
                [day, month] = BIRTHDAYS[user]

                if day == current_day and month == current_month:
                    color = randint(0, 16777215)

                    gpt_message = ""  # ToDo integrate ChatGPT

                    birthday_embed = discord.Embed(
                        title="С днем рождения!",
                        description="**Цифровой Борец помнит о тебе**\nНадеюсь, не только он..." + gpt_message,
                        colour=color)

                    personal_embed = discord.Embed(
                        title="Держи открытку",
                        colour=color)

                    personal_embed.set_image(url="")

                    await channel.send(member.mention, embed=birthday_embed)
                    await member.send(embed=personal_embed)
