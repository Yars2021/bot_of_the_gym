import discord
from discord import slash_command
from discord.ext import commands, tasks

import datetime
import os
import utils
import validators
import yadisk
import yt_dlp

from configs import global_vars


class InternetCommands(commands.Cog, name="internet"):
    def __init__(self, bot):
        self.bot = bot
        self.sources_root = os.path.join(os.path.dirname(__file__), "../data")
        self.sources_dir = "yt_video_sources"
        self.cloud_dir = "yt_sources_bot"
        self.files_to_delete = []
        self.ytdl_source_options = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(self.sources_root, self.sources_dir, "%(title)s.%(ext)s"),
            "preferredcodec": "mp4",
        }
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_source_options)

    @slash_command(
        name="youtube_src",
        description="Скачать видео по ссылке",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_youtube_src(self, ctx: discord.ApplicationContext, request: str):
        if not validators.url(request):
            await ctx.respond(
                embed=utils.error_embed("Эта команда может искать только по ссылке"),
                ephemeral=True)
        else:
            await ctx.respond(embed=utils.info_embed("Загружаю данные..."),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])

            info = self.ytdl.extract_info(request, download=True)
            filename = self.ytdl.prepare_filename(info)

            if os.path.getsize(filename) <= 8 * 1024 * 1024:
                await ctx.user.send(content="Видео по запросу", file=discord.File(filename))
            else:
                disk = yadisk.YaDisk(token=global_vars.YANDEX)

                if not disk.check_token():
                    await ctx.edit(embed=utils.error_embed("Невалидный токен диска"))
                else:
                    if not disk.exists(self.cloud_dir):
                        disk.mkdir(self.cloud_dir)

                    now = datetime.datetime.utcnow()

                    disk_filename = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + "." + filename.split(".")[-1]

                    print(disk_filename)

                    disk.upload(filename, self.cloud_dir + "/" + disk_filename)

                    self.files_to_delete.append(disk_filename)

                    print(disk_filename)

            os.remove(filename)

    @tasks.loop(hours=24)
    async def disk_cleanup_loop(self):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        self.disk_cleanup_loop.start()


def setup(bot):
    bot.add_cog(InternetCommands(bot))
