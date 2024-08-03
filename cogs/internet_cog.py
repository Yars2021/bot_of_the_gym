import discord
from discord import slash_command
from discord.ext import commands, tasks

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

    @tasks.loop(seconds=5)
    async def check_uploads_loop(self):
        if os.path.exists(global_vars.uploaded_files):
            with open(global_vars.uploaded_files, "r", encoding="utf-8") as f:
                uploaded_files = list(ast.literal_eval(f.read()))

            f.close()

            if len(uploaded_files) > 0:
                uploaded_file = uploaded_files.pop(0)

                with open(global_vars.uploaded_files, "w", encoding="utf-8") as f:
                    json.dump(uploaded_files, f)

                f.close()

                user_id = int(uploaded_file["requester"])
                result_link = uploaded_file["result"]
                video_title = uploaded_file["title"]
                video_uploader = uploaded_file["uploader"]
                video_description = uploaded_file["description"]
                video_upload_date = uploaded_file["upload_date"]

                if result_link == "token_fail":
                    await (await self.bot.fetch_user(user_id)).send(embed=utils.error_embed(result_link))
                else:
                    video_embed = discord.Embed(title=video_title,
                                                url=result_link,
                                                description="```" + video_description + "```",
                                                colour=0x9e9e9e)

                    video_embed.set_author(name=video_uploader)
                    video_embed.set_footer(text=utils.separate_date(video_upload_date))

                    await (await self.bot.fetch_user(user_id)).send(embed=video_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_uploads_loop.is_running():
            self.check_uploads_loop.start()


def setup(bot):
    bot.add_cog(InternetCommands(bot))
