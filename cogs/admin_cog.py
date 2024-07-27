import discord
from discord import slash_command
from discord.ext import commands

import utils

from configs import global_vars


class AdminCommands(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.bot = bot
        self.admin_ids = global_vars.ADMIN_IDS
        self.bot_channel = global_vars.BOT_CHANNEL

    @slash_command(
        name="update",
        description="Обновить бота",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_update(self, ctx: discord.ApplicationContext):
        if str(ctx.user.id) not in self.admin_ids:
            await ctx.respond(embed=utils.error_embed("Недостаточно прав"),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])
        else:
            await ctx.respond(embed=utils.info_embed("Обновление..."),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[0])
            await utils.update_bot(ctx)

    @slash_command(
        name="patch",
        description="Отобразить последние изменения",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_patch(self, ctx: discord.ApplicationContext):
        if str(ctx.user.id) not in self.admin_ids:
            await ctx.respond(embed=utils.error_embed("Недостаточно прав"),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])
        else:
            await ctx.respond(embed=utils.info_embed("Загружаю данные..."),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[0])
            await utils.show_patchonote(self.bot, self.bot_channel)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
