from AbstractModule import AbstractModule

import asyncio
import discord
import os
import yt_dlp

import SoundboardButtons


class AudioModule(AbstractModule):
    MUSIC_ROOT = os.path.dirname(__file__)

    MUSIC_DIR = "yt"

    SOUND_ROOT = os.path.dirname(__file__) + "/soundboard/"

    FFMPEG_OPTIONS = {
        "options": "-vn"
    }

    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(MUSIC_ROOT, MUSIC_DIR, "%(extractor)s-%(id)s-%(title)s.%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0"
    }

    SONG_QUEUE = []

    MUSIC_FLAGS = {
        "IS_LOOPED": False,
        "IS_PLAYING": False,
        "SKIP_FLAG": False
    }

    BUTTONS = SoundboardButtons.BUTTONS

    SOUND_QUEUE = []

    SOUND_FLAGS = {
        "IS_PLAYING": False
    }

    voice_client = None
    voice_channel = None

    def __init__(self):
        super().__init__("audio_mod")
        self.MUSIC_STATUS = True
        self.SOUND_STATUS = True

    def activate(self):
        super(SizeModule, self).activate()

    def deactivate(self):
        super(SizeModule, self).deactivate()

    def get_music_status(self):
        return self.MUSIC_STATUS

    def get_sound_status(self):
        return self.SOUND_STATUS

    def set_music_status(self, music_status):
        self.MUSIC_STATUS = music_status

    def set_sound_status(self, sound_status):
        self.SOUND_STATUS = sound_status

    def clean_files(self):
        if os.path.exists(self.MUSIC_DIR):
            os.system("rm -rf ./" + self.MUSIC_DIR)

    def remove_file(self, path):
        if os.path.exists(os.path.exists("./" + self.MUSIC_DIR + "/" + path)):
            os.system("rm -f " + "./" + self.MUSIC_DIR + "/" + path)

    def edit_sound_button(self, index, new_label, new_emoji, new_path):
        self.BUTTONS[index] = {"label": new_label, "emoji": new_emoji, "path": new_path}

    def drop_song_queue(self):
        self.MUSIC_FLAGS["IS_PLAYING"] = False
        self.MUSIC_FLAGS["IS_LOOPED"] = False
        self.MUSIC_FLAGS["SKIP_FLAG"] = False
        self.SONG_QUEUE = []

    def drop_sound_queue(self):
        self.SOUND_FLAGS["IS_PLAYING"] = False
        self.SOUND_QUEUE = []

    def reset_player(self):
        self.voice_client = None
        self.voice_channel = None

    # Получить названия по ссылке
    def search_yt(self, url):
        titles = []

        try:
            info = yt_dlp.YoutubeDL(self.YTDL_OPTIONS).extract_info(url, download=False)

            if "entries" not in info:
                titles.append(info["title"])
            else:
                for entry in info["entries"]:
                    titles.append(entry["title"])

            return {
                "code": 0,
                "titles": titles
            }
        except Exception:
            print("Ошибка поиска (анализ имен)")

            return {
                "code": -1,
                "titles": []
            }

    # Найти и скачать звук по ссылке
    def search_download_yt(self, url):
        tracks = []

        with yt_dlp.YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=True)

                if "entries" not in info:
                    tracks = [{
                        "title": info["title"],
                        "thumbnail": info["thumbnail"],
                        "filename": ydl.prepare_filename(info)
                    }]
                else:
                    for entry in info["entries"]:
                        tracks.append({
                            "title": entry["title"],
                            "thumbnail": entry["thumbnail"],
                            "filename": ydl.prepare_filename(entry)
                        })

            except Exception:
                print("Ошибка поиска (скачивание)")

        return tracks

    # Перейти к следующему элементу очереди. Добавить в конец только что сыгранный элемент, если IS_LOOPED
    def pop_and_continue(self):
        self.MUSIC_FLAGS["IS_PLAYING"] = False

        last_song = self.SONG_QUEUE.pop(0)

        if self.MUSIC_FLAGS["IS_LOOPED"] and not self.MUSIC_FLAGS["SKIP_FLAG"]:
            self.SONG_QUEUE.append(last_song)
        else:
            self.remove_file(last_song["filename"])

        self.MUSIC_FLAGS["SKIP_FLAG"] = False

        if len(self.SONG_QUEUE) <= 0:
            self.clean_files()

        self.play_first()

    def pop_and_continue_sound(self):
        self.SOUND_FLAGS["IS_PLAYING"] = False

        if len(self.SOUND_QUEUE) > 0:
            self.SOUND_QUEUE.pop(0)

        self.play_sound_queue()

    # Найти и сыграть 0-й запрос из очереди
    def play_first(self):
        if len(self.SONG_QUEUE) <= 0 or self.MUSIC_FLAGS["IS_PLAYING"]:
            return

        self.MUSIC_FLAGS["IS_PLAYING"] = True

        if self.voice_client is not None and self.voice_client.is_connected():
            self.voice_client.play(discord.FFmpegPCMAudio(self.SONG_QUEUE[0]["filename"]),
                                   after=lambda e: self.pop_and_continue())

    def play_sound_queue(self):
        if len(self.SOUND_QUEUE) <= 0 or self.SOUND_FLAGS["IS_PLAYING"]:
            return

        self.SOUND_FLAGS["IS_PLAYING"] = True

        if self.voice_client is not None and self.voice_client.is_connected():
            self.voice_client.play(discord.FFmpegPCMAudio(self.SOUND_ROOT + self.SOUND_QUEUE[0]),
                                   after=lambda e: self.pop_and_continue_sound())

    # Проверить правильность запроса и добавить в очередь, если он корреткный
    async def queue_song(self, interaction, request):
        await interaction.response.send_message("Ищу...")

        initial_message = await interaction.original_response()

        search_result = self.search_yt(request)

        if search_result["code"] != 0:
            await initial_message.edit(content="По запросу ничего не найдено")
            return

        if len(search_result["titles"]) == 1:
            await initial_message.edit(content="Добавляю в очередь -- " + search_result["titles"][0])
        else:
            playlist = ""

            for index in range(len(search_result["titles"])):
                playlist += (str(index + 1) + ". " + search_result["titles"][index] + "\n")

            await initial_message.edit(content="Добавляю в очередь -- ПЛЕЙЛИСТ:\n" + playlist)

        for entry in self.search_download_yt(request):
            self.SONG_QUEUE.append(entry)

        self.voice_client = interaction.guild.voice_client
        self.voice_channel = interaction.user.voice.channel

        if self.SOUND_FLAGS["IS_PLAYING"]:
            self.drop_sound_queue()

            if self.voice_client is not None:
                await self.voice_client.disconnect()

        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await self.voice_channel.connect()
        else:
            await self.voice_client.move_to(interaction.user.voice.channel)

        self.play_first()

    async def queue_sound(self, sound_tuple, interaction):
        if not self.SOUND_STATUS or self.MUSIC_FLAGS["IS_PLAYING"] or len(self.SONG_QUEUE) > 0:
            return

        self.voice_client = interaction.guild.voice_client
        self.voice_channel = interaction.user.voice.channel

        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await self.voice_channel.connect()
        else:
            await self.voice_client.move_to(self.voice_channel)

        self.SOUND_QUEUE.append(sound_tuple["path"])

        self.play_sound_queue()

    async def show_queue(self, interaction):
        if len(self.SONG_QUEUE) <= 0:
            message = "Очередь пуста"
        else:
            message = "Очередь музыки:\n"

        for index in range(len(self.SONG_QUEUE)):
            message += (str(index + 1) + ". " + self.SONG_QUEUE[index]["title"] + "\n")

        await interaction.response.send_message(message, ephemeral=True)

    async def get_song_info(self, interaction):
        if len(self.SONG_QUEUE) <= 0:
            await interaction.response.send_message("Очередь пуста", ephemeral=True)
            return

        await interaction.response.send_message("Сейчас играет:\n\n" + self.SONG_QUEUE[0]["title"],
                                                embed=discord.Embed().set_image(url=self.SONG_QUEUE[0]["thumbnail"]),
                                                ephemeral=True)

    async def skip(self, interaction):
        if interaction.guild.voice_client is not None:
            self.MUSIC_FLAGS["SKIP_FLAG"] = True
            interaction.guild.voice_client.stop()

        if len(self.SONG_QUEUE) > 0:
            self.play_first()

    async def listen_activity(self):
        while self.MUSIC_FLAGS["IS_PLAYING"] or self.SOUND_FLAGS["IS_PLAYING"]:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(10)

            while self.MUSIC_FLAGS["IS_PLAYING"] or self.SOUND_FLAGS["IS_PLAYING"]:
                break
            else:
                self.drop_song_queue()
                self.drop_sound_queue()

                self.clean_files()

                if self.voice_client is not None:
                    await self.voice_client.disconnect()


class Soundboard(discord.ui.View):
    def __init__(self, sound_module) -> None:
        super().__init__(timeout=None)
        self.soundModule = sound_module

    @discord.ui.button(
        custom_id="sound_11",
        label=SoundboardButtons.BUTTONS[0]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[0]["emoji"]
    )
    async def play_11(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[0]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[0], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_12",
        label=SoundboardButtons.BUTTONS[1]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[1]["emoji"]
    )
    async def play_12(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[1]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[1], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_13",
        label=SoundboardButtons.BUTTONS[2]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[2]["emoji"]
    )
    async def play_13(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[2]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[2], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_14",
        label=SoundboardButtons.BUTTONS[3]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[3]["emoji"]
    )
    async def play_14(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[3]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[3], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_15",
        label=SoundboardButtons.BUTTONS[4]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[4]["emoji"]
    )
    async def play_15(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[4]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[4], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_21",
        label=SoundboardButtons.BUTTONS[5]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[5]["emoji"]
    )
    async def play_21(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[5]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[5], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_22",
        label=SoundboardButtons.BUTTONS[6]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[6]["emoji"]
    )
    async def play_22(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[6]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[6], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_23",
        label=SoundboardButtons.BUTTONS[7]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[7]["emoji"]
    )
    async def play_23(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[7]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[7], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_24",
        label=SoundboardButtons.BUTTONS[8]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[8]["emoji"]
    )
    async def play_24(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[8]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[8], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_25",
        label=SoundboardButtons.BUTTONS[9]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[9]["emoji"]
    )
    async def play_25(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[9]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[9], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_31",
        label=SoundboardButtons.BUTTONS[10]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[10]["emoji"]
    )
    async def play_31(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[10]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[10], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_32",
        label=SoundboardButtons.BUTTONS[11]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[11]["emoji"]
    )
    async def play_32(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[11]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[11], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_33",
        label=SoundboardButtons.BUTTONS[12]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[12]["emoji"]
    )
    async def play_33(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[12]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[12], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_34",
        label=SoundboardButtons.BUTTONS[13]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[13]["emoji"]
    )
    async def play_34(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[13]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[13], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_35",
        label=SoundboardButtons.BUTTONS[14]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[14]["emoji"]
    )
    async def play_35(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[14]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[14], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_41",
        label=SoundboardButtons.BUTTONS[15]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[15]["emoji"]
    )
    async def play_41(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[15]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[15], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_42",
        label=SoundboardButtons.BUTTONS[16]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[16]["emoji"]
    )
    async def play_42(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[16]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[16], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_43",
        label=SoundboardButtons.BUTTONS[17]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[17]["emoji"]
    )
    async def play_43(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[17]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[17], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_44",
        label=SoundboardButtons.BUTTONS[18]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[18]["emoji"]
    )
    async def play_44(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[18]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[18], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_45",
        label=SoundboardButtons.BUTTONS[19]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[19]["emoji"]
    )
    async def play_45(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[19]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[19], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_51",
        label=SoundboardButtons.BUTTONS[20]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[20]["emoji"]
    )
    async def play_51(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[20]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[20], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_52",
        label=SoundboardButtons.BUTTONS[21]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[21]["emoji"]
    )
    async def play_52(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[21]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[21], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_53",
        label=SoundboardButtons.BUTTONS[22]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[22]["emoji"]
    )
    async def play_53(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[22]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[22], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_54",
        label=SoundboardButtons.BUTTONS[23]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[23]["emoji"]
    )
    async def play_54(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[23]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[23], interaction)
        await self.soundModule.listen_activity()

    @discord.ui.button(
        custom_id="sound_55",
        label=SoundboardButtons.BUTTONS[24]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=SoundboardButtons.BUTTONS[24]["emoji"]
    )
    async def play_55(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Играю " + SoundboardButtons.BUTTONS[24]["label"])
        await self.soundModule.queue_sound(SoundboardButtons.BUTTONS[24], interaction)
        await self.soundModule.listen_activity()
