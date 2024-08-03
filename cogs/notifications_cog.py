import discord
from discord import slash_command
from discord.ext import commands, tasks

import ast
import datetime
import json
import os
import utils

from configs import global_vars


class NotificationsModuleCommands(commands.Cog, name="notifications_cog"):
    def __init__(self, bot):
        self.bot = bot
        self.notifications_module = global_vars.NOTIFICATIONS_FUNCTIONS
        self.path = "./data/notifications/"
        self.history = self.path + "history"

    @slash_command(
        name="notify",
        description="Добавить напоминание"
    )
    async def command_notify(self, ctx: discord.ApplicationContext, timezone: int, day: int, month: int, year: int,
                             hours: int, minutes: int, text: str) -> None:
        if timezone > 12 or timezone < -12:
            await ctx.respond(
                embed=utils.error_embed("Параметр timezone показывает часовой пояс относительно времени UTC.\n"
                                        "**-12 <= timezone <= 12**"),
                ephemeral=True)
        else:
            code, date, time = self.notifications_module.form_date_and_time(timezone, day, month, year, hours, minutes)

            if code == "error":
                await ctx.respond(embed=utils.error_embed(date + time), ephemeral=True)
            else:
                if not os.path.exists(self.path + str(date)):
                    with open(self.path + str(date), "w", encoding="utf-8") as f:
                        f.write("[]")

                    f.close()

                with open(self.path + str(date), "r", encoding="utf-8") as f:
                    notifications = list(ast.literal_eval(f.read()))

                f.close()

                notifications.append({
                    "user": str(ctx.user.id),
                    "date": str(date),
                    "time": str(time),
                    "text": text
                })

                with open(self.path + str(date), "w", encoding="utf-8") as f:
                    json.dump(notifications, f)

                f.close()

                await ctx.respond(embed=utils.info_embed("Напоминание успешно создано"), ephemeral=True)

    @tasks.loop(seconds=30)
    async def notifications_loop(self):
        utcnow = datetime.datetime.utcnow()

        date = str(utcnow.date())
        time = str(utcnow.time())

        if os.path.exists(self.path + date):
            with open(self.path + date, "r", encoding="utf-8") as f:
                notifications = list(ast.literal_eval(f.read()))

            f.close()

            new_notifications = []

            for notification in notifications:
                if notification["time"] > time:
                    new_notifications.append(notification)
                else:
                    await (await self.bot.fetch_user(int(notification["user"]))).send(embed=utils.full_info_embed(
                        "Напоминание",
                        "**" + notification["text"] + "**"
                    ))

                    with open(self.history, "a", encoding="utf-8") as f:
                        f.write(str(notification) + "\n")

                    f.close()

            with open(self.path + date, "w", encoding="utf-8") as f:
                json.dump(new_notifications, f)

            f.close()

    @tasks.loop(hours=24)
    async def notifications_cleanup_loop(self):
        date = str(datetime.datetime.utcnow().date())

        for f in os.listdir(self.path):
            if os.path.isfile(os.path.join(self.path, f) and self.path + f != self.history):
                if self.path + f < date:
                    os.remove(self.path + f)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.notifications_loop.is_running():
            self.notifications_loop.start()

        if not self.notifications_cleanup_loop.is_running():
            self.notifications_cleanup_loop.start()


def setup(bot):
    bot.add_cog(NotificationsModuleCommands(bot))
