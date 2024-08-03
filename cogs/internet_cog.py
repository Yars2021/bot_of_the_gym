import discord
from discord import slash_command
from discord.ext import commands, tasks

import ast
import json
import os
import utils
import validators
import yt_dlp

from configs import global_vars


class InternetCommands(commands.Cog, name="internet"):
    def __init__(self, bot):
        self.bot = bot
        self.ytdl_search = yt_dlp.YoutubeDL({
            "restrictfilenames": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",
            "force-ipv4": True,
            "cachedir": False
        })
        self.ytdl_info = yt_dlp.YoutubeDL({
            "extract_flat": True,
            "skip_download": True,
        })

    @slash_command(
        name="youtube_src",
        description="Скачать звук/видео по ссылке (YouTube)"
    )
    async def command_youtube_src(self, ctx: discord.ApplicationContext, request: str,
                                  sound_only: discord.Option(bool, required=False, default=False),
                                  include_description: discord.Option(bool, required=False, default=True)):
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

        if not validators.url(request):
            search_result = self.ytdl_search.extract_info(request, download=False)

            if "entries" not in search_result:
                request = search_result["webpage_url"]
            else:
                request = search_result["entries"][0]["webpage_url"]

        info = self.ytdl_info.extract_info(request, download=False)

        if not utils.is_playlist_link(request):
            files.append({
                "requester": str(ctx.user.id),
                "name": str(ctx.user.global_name),
                "request": info["webpage_url"],
                "format_flag": str(sound_only),
                "include_description": str(include_description)
            })
        else:
            if "entries" in info:
                for entry in info["entries"]:
                    if entry is not None:
                        files.append({
                            "requester": str(ctx.user.id),
                            "name": str(ctx.user.global_name),
                            "request": entry["url"],
                            "format_flag": str(sound_only),
                            "include_description": str(include_description)
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
                    video_embeds = utils.video_embed_chain(
                        video_title,
                        result_link,
                        video_uploader,
                        utils.separate_date(video_upload_date),
                        video_description
                    )

                    for video_embed in video_embeds:
                        await (await self.bot.fetch_user(user_id)).send(embed=video_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_uploads_loop.is_running():
            self.check_uploads_loop.start()


def setup(bot):
    bot.add_cog(InternetCommands(bot))
