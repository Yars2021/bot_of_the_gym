import discord
from discord.ext import commands, tasks

import ast
import datetime
import json
import os
import yadisk
import yt_dlp

import utils
from configs import global_vars


class UploaderCommands(commands.Cog, name="uploader"):
    def __init__(self, bot):
        self.bot = bot

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
                result = uploaded_file["result"]

                if result == "token_fail":
                    await (await self.bot.fetch_user(user_id)).send(embed=utils.error_embed(result))
                else:
                    await (await self.bot.fetch_user(user_id)).send(
                        embed=utils.info_embed(f"[Загрузить файл]({result})")
                    )

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_uploads_loop.is_running():
            self.check_uploads_loop.start()


def setup(bot):
    bot.add_cog(UploaderCommands(bot))
