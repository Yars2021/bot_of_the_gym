import discord
from discord import slash_command
from discord.ext import commands

import utils
import validators

from configs import global_vars
from panels.ControlPanel import ControlPanel
from panels.SoundboardPanel import SoundboardPanel


class SoundModuleCommands(commands.Cog, name="sound_cog"):
    def __init__(self, bot):
        self.bot = bot
        self.sound_module = global_vars.SOUND_FUNCTIONS

    @slash_command(
        name="play",
        description="Играть по ссылке или названию",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_play(self, ctx: discord.ApplicationContext, request: str) -> None:
        if ctx.user.voice is None or ctx.user.voice.channel is None:
            await ctx.respond(
                embed=utils.error_embed("Для использования нужно находиться в голосовом канале"),
                ephemeral=True)
        else:
            if self.sound_module.sounds_active:
                await self.sound_module.terminate_sounds()

            await ctx.respond("Ищу... Это может занять некоторе время")

            if validators.url(request) and request.find("https://open.spotify.com") != -1:
                code, conversion_result = self.sound_module.process_spotify_link(request)

                if code == "ok":
                    request = conversion_result
                else:
                    request = ""

                    await ctx.edit(content="",
                                   embed=utils.error_embed(f"Ошибка поиска по ссылке Spotify: {conversion_result}"))

            if len(request) > 0:
                await self.sound_module.find_and_play(ctx, request)

    @slash_command(
        name="right_play",
        description="♂Играть♂ по названию (YouTube)",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_right_play(self, ctx: discord.ApplicationContext, request: str) -> None:
        if ctx.user.voice is None or ctx.user.voice.channel is None:
            await ctx.respond(
                embed=utils.error_embed("Для использования нужно находиться в голосовом канале"),
                ephemeral=True)
        else:
            if validators.url(request):
                await ctx.respond(
                    embed=utils.error_embed("Эта команда не может искать по ссылке"),
                    ephemeral=True)
            else:
                if self.sound_module.sounds_active:
                    await self.sound_module.terminate_sounds()

                await ctx.respond("Ищу... Это может занять некоторе время")
                await self.sound_module.find_and_play(ctx, request + " right version")

    @slash_command(
        name="controls",
        description="Вывести интерфейс управления",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_controls(self, ctx: discord.ApplicationContext) -> None:
        if str(ctx.user.id) in global_vars.ADMIN_IDS:
            await ctx.respond(view=SoundboardPanel())
            await ctx.followup.send(view=ControlPanel())
        else:
            await ctx.respond(embed=utils.error_embed("Недостаточно прав"),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])


def setup(bot):
    bot.add_cog(SoundModuleCommands(bot))
