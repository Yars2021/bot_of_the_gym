import discord
from discord import slash_command
from discord.ext import commands

import ast
import datetime
import json
import os
import utils

from configs import global_vars
from random import randint


class SizeModCommands(commands.Cog, name="size_cog"):
    def __init__(self, bot):
        self.bot = bot
        self.size_module = global_vars.SIZE_FUNCTIONS
        self.file = "./data/.size_table"
        self.messages = [
            "Волшебная палочка",
            "Козырь в рукаве",
            "Питон в кустах",
            "Мясная сигара",
            "Третья нога",
            "Экскалибур",
            "Авторитет",
            "Морковка",
            "Членохер",
            "Чупачупс",
            "Сюрприз",
            "Хоботок",
            "Прикол",
            "Талант",
            "Ствол",
            "Маяк",
            "Удав"
        ]

        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                f.write("{}")

            f.close()

    @slash_command(
        name="size",
        description="Считает сегодняшнюю длину",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_size(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.user.id)
        call_date = str(datetime.datetime.utcnow().date())

        with open(self.file, "r", encoding="utf-8") as f:
            stats = ast.literal_eval(f.read())

        f.close()

        if user_id == "429951059650150411":
            stats[user_id] = [call_date, 50, "", 0]
        elif user_id == "318056725070741506":
            stats[user_id] = [call_date, 15.5, "", 0]

        if user_id not in stats:
            stats[user_id] = [call_date, randint(1, 40), self.size_module.get_secret(1), 1]
        elif call_date != stats[user_id][0]:
            chance = stats[user_id][3]
            next_chance = 1

            secret = self.size_module.get_secret(chance)

            if secret == "":
                next_chance = min(chance + 1, 20)

            stats[user_id] = [call_date, randint(1, 40), secret, next_chance]

        with(open(self.file, "w", encoding="utf-8")) as f:
            json.dump(stats, f)

        f.close()

        await ctx.respond(self.messages[randint(0, len(self.messages) - 1)] +
                          " у тебя " + stats[user_id][2] +
                          self.size_module.get_length(stats[user_id][1]), delete_after=utils.MESSAGE_TIMER[2])

    @slash_command(
        name="sum",
        description="Считает сумму сегодняшних длин",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_sum(self, ctx: discord.ApplicationContext):
        with open(self.file, "r", encoding="utf-8") as f:
            stats = ast.literal_eval(f.read())

        f.close()

        call_date = str(datetime.datetime.utcnow().date())

        size_sum = 0

        for user in stats:
            if stats[user][0] == call_date:
                size_sum += stats[user][1]

        await ctx.respond("Сумма за сегодня = " + str(size_sum) + " см", delete_after=utils.MESSAGE_TIMER[3])

    @slash_command(
        name="stats",
        description="Показывает сегодняшнюю статистику",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_stats(self, ctx: discord.ApplicationContext):
        date = datetime.datetime.utcnow().date()
        guild = await self.bot.fetch_guild(global_vars.SERVER_ID)

        with open(self.file, "r", encoding="utf-8") as f:
            stats = ast.literal_eval(f.read())

        f.close()

        call_date = str(date)
        call_day = str(date.day)
        call_month = str(date.month)
        call_year = str(date.year)

        members = guild.fetch_members(limit=None)

        daily = ""
        index = 1

        async for member in members:
            for user in stats:
                if stats[user][0] == call_date and user == str(member.id):
                    if member.nick is not None:
                        display = member.nick
                    else:
                        display = member.global_name

                    daily += str(index) + ". " + display + ": " + str(stats[user][1]) + " см " + stats[user][2] + "\n"
                    index += 1

        await ctx.respond(
            embed=utils.message_embed(
                "Статистика за " + call_day + "." + call_month + "." + call_year, daily, 0xb85300),
            delete_after=utils.MESSAGE_TIMER[3])


def setup(bot):
    bot.add_cog(SizeModCommands(bot))
