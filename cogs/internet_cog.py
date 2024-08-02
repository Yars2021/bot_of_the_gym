import discord
from discord import slash_command
from discord.ext import commands

import ast
import json
import os
import utils
import validators

from configs import global_vars


class InternetCommands(commands.Cog, name="internet"):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="youtube_src",
        description="Скачать звук/видео по ссылке (YouTube)",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_youtube_src(self, ctx: discord.ApplicationContext, request: str,
                                  sound_only: discord.Option(bool, required=False, default=False)):
        if not validators.url(request):
            await ctx.respond(
                embed=utils.error_embed("Эта команда может искать только по ссылке"),
                ephemeral=True)
        else:
            await ctx.respond(embed=utils.info_embed("Запрос отправлен"),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])

            if not os.path.exists(global_vars.files_to_upload):
                with open(global_vars.files_to_upload, "w", encoding="utf-8") as f:
                    f.write("[]")

                f.close()

            with open(global_vars.files_to_upload, "r", encoding="utf-8") as f:
                files = list(ast.literal_eval(f.read()))

            f.close()

            files.append({
                "requester": str(ctx.user.id),
                "name": str(ctx.user.global_name),
                "request": request,
                "format_flag": str(sound_only)
            })

            with open(global_vars.files_to_upload, "w", encoding="utf-8") as f:
                json.dump(files, f)

            f.close()


def setup(bot):
    bot.add_cog(InternetCommands(bot))
