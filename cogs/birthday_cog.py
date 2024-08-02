import discord
from discord import slash_command
from discord.ext import commands, tasks

import ast
import datetime
import json
import os
import utils

from configs import global_vars
from random import randint


class BirthdayModuleCommands(commands.Cog, name="birthday_module"):
    def __init__(self, bot):
        self.bot = bot
        self.file = "./data/.birthday_table"
        self.birthdays = {}

    def extract_data(self):
        if os.path.exists(self.file):
            with open(self.file, "r", encoding="utf-8") as f:
                self.birthdays = ast.literal_eval(f.read())

            f.close()

    @slash_command(
        name="birthday",
        description="Добавить данные о дне рождения",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_birthday(self, ctx: discord.ApplicationContext, user_id: str, day: int, month: int, pref: str) -> None:
        if str(ctx.user.id) not in global_vars.ADMIN_IDS:
            await ctx.respond(embed=utils.error_embed("Недостаточно прав"),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])
        else:
            if not utils.check_date(day, month):
                await ctx.respond(embed=utils.error_embed("Ошибка в дате"),
                                  ephemeral=True,
                                  delete_after=utils.MESSAGE_TIMER[1])
            else:
                self.extract_data()
                self.birthdays[str(user_id)] = [str(day), str(month), pref]

                with open(self.file, "w", encoding="utf-8") as f:
                    json.dump(self.birthdays, f)

                f.close()

                await ctx.respond(embed=utils.info_embed("День рождения успешно добавлен"), ephemeral=True)

    @slash_command(
        name="birthday_table",
        description="Просмотреть список зарегистрированных дней рождения",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_birthday_table(self, ctx: discord.ApplicationContext) -> None:
        if str(ctx.user.id) not in global_vars.ADMIN_IDS:
            await ctx.respond(embed=utils.error_embed("Недостаточно прав"),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])
        else:
            self.extract_data()

            members = self.bot.get_guild(int(global_vars.SERVER_ID)).fetch_members(limit=None)

            users = {}

            async for member in members:
                if member.nick is not None:
                    users[str(member.id)] = member.nick
                else:
                    users[str(member.id)] = member.global_name

            table = ""
            index = 1

            for user in users:
                for birthday in self.birthdays:
                    if user == birthday:
                        table += str(index) + ". " + users[user] + ": " + \
                                 self.birthdays[birthday][0] + "." + self.birthdays[birthday][1] + "\n"
                        index += 1

            await ctx.respond(embed=utils.full_info_embed("Таблица дней рождения", table), ephemeral=True)

    @tasks.loop(hours=24)
    async def birthday_loop(self):
        self.extract_data()

        current_day = str(datetime.date.today().day)
        current_month = str(datetime.date.today().month)

        members = self.bot.get_guild(int(global_vars.SERVER_ID)).fetch_members(limit=None)

        async for member in members:
            for user in self.birthdays:
                if user == str(member.id):
                    [day, month, preferences] = self.birthdays[user]

                    if day == current_day and month == current_month:
                        color = randint(0, 16777215)

                        gpt_message = ""  # ToDo integrate ChatGPT

                        birthday_embed = utils.message_embed(
                            "С днем рождения!",
                            "**Цифровой Борец помнит о тебе**\nНадеюсь, не только он..." + gpt_message,
                            color
                        )

                        personal_embed = discord.Embed(
                            title="Держи открытку",
                            colour=color)

                        personal_embed.set_image(url="")

                        await member.send(embed=personal_embed)
                        await (await self.bot.fetch_channel(int(global_vars.BOT_CHANNEL)))\
                            .send(member.mention, embed=birthday_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.birthday_loop.is_running():
            self.birthday_loop.start()


def setup(bot):
    bot.add_cog(BirthdayModuleCommands(bot))
