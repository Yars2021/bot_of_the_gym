import discord
from discord import slash_command
from discord.ext import commands, tasks

import datetime
import os

from yadisk.objects import SyncResourceLinkObject

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
        self.files_to_upload = []

    @slash_command(
        name="youtube_src",
        description="Скачать звук/видео по ссылке (YouTube)",
        guild_ids=[global_vars.SERVER_ID]
    )
    async def command_youtube_src(self, ctx: discord.ApplicationContext, request: str,
                                  sound_only: discord.Option(bool, required=False, default=False),
                                  force_disk: discord.Option(bool, required=False, default=False)):
        if not validators.url(request):
            await ctx.respond(
                embed=utils.error_embed("Эта команда может искать только по ссылке"),
                ephemeral=True)
        else:
            await ctx.respond(embed=utils.info_embed("Загружаю данные..."),
                              ephemeral=True,
                              delete_after=utils.MESSAGE_TIMER[1])

            now = datetime.datetime.utcnow()

            if sound_only:
                download_format = "bestaudio/best"
                preferred_codec = "mp3"
            else:
                download_format = "bestvideo+bestaudio/best"
                preferred_codec = "mp4"

            ytdl_video = yt_dlp.YoutubeDL({
                "format": download_format,
                "outtmpl": os.path.join(
                    self.sources_root,
                    self.sources_dir,
                    f"{ctx.user.global_name}_{str(now.year)}{str(now.month)}{str(now.day)}{str(now.hour)}{str(now.minute)}{str(now.second)}.%(ext)s"
                ),
                "preferredcodec": preferred_codec,
            })

            info = ytdl_video.extract_info(request, download=True)
            file_path = ytdl_video.prepare_filename(info)

            ytdl_video.close()

            filesize = os.path.getsize(file_path)

            if filesize <= 16 * 1024 * 1024 and not force_disk:
                print("Sending via DMs")
                await ctx.user.send(content="Видео по запросу", file=discord.File(fp=file_path))
                os.remove(file_path)
            else:
                print("Queueing to upload")
                local_path = os.path.join(self.sources_root, self.sources_dir, file_path)
                cloud_path = self.cloud_dir + "/" + file_path.split("/")[-1]

                self.files_to_upload.append([ctx.user, local_path, cloud_path])

    @tasks.loop(seconds=1)
    async def upload_loop(self):
        if len(self.files_to_upload) > 0:
            [requester, local_path, cloud_path] = self.files_to_upload.pop(0)

            disk = yadisk.YaDisk(token=global_vars.YANDEX)

            if not disk.check_token():
                await requester.send(embed=utils.error_embed("Невалидный токен диска"))
            else:
                if not disk.exists(self.cloud_dir):
                    disk.mkdir(self.cloud_dir)

                disk.upload(local_path, cloud_path, timeout=120.0)
                link = disk.publish(cloud_path).get_download_link()

                await requester.send(content=f"[Видео по последнему запросу]({link})")

                disk.close()

            os.remove(local_path)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.upload_loop.is_running():
            self.upload_loop.start()


def setup(bot):
    bot.add_cog(InternetCommands(bot))
