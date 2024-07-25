import asyncio
import discord
import os
import requests
import utils
import yt_dlp

from bs4 import BeautifulSoup


MUSIC_ROOT = os.path.dirname(__file__)

MUSIC_DIR = "yt_sources"

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
    "source_address": "0.0.0.0",
    "force-ipv4": True,
    "preferredcodec": "mp3",
    "cachedir": False
}

YTDL = yt_dlp.YoutubeDL(YTDL_OPTIONS)

IS_LOOPED = False

IS_PLAYING = False

SKIP_FLAG = False

SONG_QUEUE = []

player = None
voice_client = None
voice_channel = None


def clean_files():
    global MUSIC_DIR

    if os.path.exists(MUSIC_DIR):
        os.system("rm -rf ./" + MUSIC_DIR)


def remove_file(path):
    global MUSIC_DIR

    if os.path.exists(os.path.exists("./" + MUSIC_DIR + "/" + path)):
        os.system("rm -f " + "./" + MUSIC_DIR + "/" + path)


def fetch_header_yt(url):
    global YTDL

    titles = []

    try:
        info = YTDL.extract_info(url, download=False)

        if "entries" not in info:
            titles.append(info["title"])
        else:
            for entry in info["entries"]:
                titles.append(entry["title"])

        return 0, titles

    except Exception as e:
        print(f"Ошибка поиска (анализ имен): {e}")

        return -1, [e]


def fetch_files_yt(url):
    global YTDL

    tracks = []

    try:
        info = YTDL.extract_info(url, download=True)

        if "entries" not in info:
            tracks = [{
                "title": info["title"],
                "thumbnail": info["thumbnail"],
                "filename": YTDL.prepare_filename(info)
            }]
        else:
            for entry in info["entries"]:
                tracks.append({
                    "title": entry["title"],
                    "thumbnail": entry["thumbnail"],
                    "filename": YTDL.prepare_filename(entry)
                })

    except Exception as e:
        print(f"Ошибка поиска (скачивание источников): {e}")

    return tracks


def pop_and_continue():
    global IS_LOOPED
    global IS_PLAYING
    global SKIP_FLAG
    global SONG_QUEUE

    IS_PLAYING = False

    if len(SONG_QUEUE) > 0:
        last_song = SONG_QUEUE.pop(0)

        if IS_LOOPED and not SKIP_FLAG:
            SONG_QUEUE.append(last_song)
        else:
            remove_file(last_song["filename"])

        SKIP_FLAG = False

        if len(SONG_QUEUE) > 0:
            play()


def play():
    global FFMPEG_OPTIONS
    global IS_PLAYING
    global SONG_QUEUE
    global voice_client

    if len(SONG_QUEUE) > 0 and not IS_PLAYING:
        IS_PLAYING = True

        if voice_client is not None and voice_client.is_connected():
            voice_client.play(discord.FFmpegPCMAudio(source=SONG_QUEUE[0]["filename"], **FFMPEG_OPTIONS),
                              after=lambda e: pop_and_continue())


async def join_channel(interaction):
    global voice_client
    global voice_channel

    voice_client = interaction.guild.voice_client
    voice_channel = interaction.user.voice.channel

    if voice_client is None:
        voice_client = await voice_channel.connect(reconnect=True)
    else:
        await voice_client.move_to(voice_channel)


async def leave_channel():
    global voice_client

    while voice_client is not None and voice_client.is_playing():
        await asyncio.sleep(1)

    await asyncio.sleep(5)

    if voice_client is not None:
        await voice_client.disconnect()


def process_spotify_link(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "lxml")

        song = soup.find("meta", {"property": "og:title"})["content"]
        artist_soup = soup.find("meta", {"name": "music:musician"})

        if artist_soup is None:
            artist_link = ""
        else:
            artist_link = artist_soup["content"]

        artist_page = BeautifulSoup(requests.get(artist_link).text, "lxml")
        artist = artist_page.find("meta", {"property": "og:title"})["content"]

        return "ok", str(song + " " + artist).replace("&", "and")

    except Exception as e:
        return "error", e


async def find(interaction, request: str):
    original_response = await interaction.original_response()

    header_code, search_result = fetch_header_yt(request)

    if header_code != 0:
        await original_response.edit(content="", embed=utils.error_embed("Ошибка поиска: " + str(search_result[0])))
    else:
        if len(search_result) == 1:
            queued = search_result[0]
        else:
            queued = ""

            for index in range(len(search_result)):
                queued += str(index + 1) + ". " + search_result[index] + "\n"

        await original_response.edit(content="", embed=utils.full_info_embed(
            "Добавляю в очередь",
            queued
        ))

    return header_code


async def reset_player(interaction):
    global SONG_QUEUE
    global player

    if player is not None:
        await player.delete()

    if len(SONG_QUEUE) > 0:
        player = await interaction.channel.send(view=PlayerPanel(), embed=utils.full_music_cover_embed(
            "Сейчас играет",
            SONG_QUEUE[0]["title"]
        ))


async def load(interaction, request: str):
    global SONG_QUEUE

    for entry in fetch_files_yt(request):
        SONG_QUEUE.append(entry)

    if len(SONG_QUEUE) > 0:
        await reset_player(interaction)
    else:
        await interaction.channel.send(embed=utils.error_embed("Ошибка скачивания"))


async def show_queue(interaction):
    global SONG_QUEUE

    if len(SONG_QUEUE) <= 0:
        cover_embed = utils.header_error_embed("Очередь пуста")
    else:
        message = ""

        for index in range(len(SONG_QUEUE)):
            message += (str(index + 1) + ". " + SONG_QUEUE[index]["title"] + "\n")

        cover_embed = utils.message_embed("Очередь музыки", message, 0x7a00f5)

    await interaction.response.send_message(embed=cover_embed, ephemeral=True)


async def show_song_info(interaction):
    global SONG_QUEUE

    if len(SONG_QUEUE) <= 0:
        cover_embed = utils.header_error_embed("Очередь пуста")
    else:
        cover_embed = utils.music_cover_embed(SONG_QUEUE[0]["title"])
        cover_embed.set_image(url=SONG_QUEUE[0]["thumbnail"])

    await interaction.response.send_message(embed=cover_embed, ephemeral=True)


async def terminate():
    global IS_LOOPED
    global IS_PLAYING
    global SKIP_FLAG
    global SONG_QUEUE
    global player
    global voice_client
    global voice_channel

    clean_files()

    voice_client = None
    voice_channel = None
    IS_LOOPED = False
    IS_PLAYING = False
    SKIP_FLAG = False
    SONG_QUEUE = []

    if player is not None:
        await player.delete()

    player = None


async def update_channel(channel):
    global voice_client
    global voice_channel

    if voice_client is not None and channel is not None:
        voice_channel = channel
        await voice_client.move_to(channel)


async def find_and_play(interaction, request):
    global IS_PLAYING

    header_code = await find(interaction, request)

    if header_code == 0:
        await load(interaction, request)

        if not IS_PLAYING:
            await join_channel(interaction)
            play()
            await leave_channel()


class PlayerPanel(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="stop_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏹️"
    )
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        global voice_client

        await interaction.response.edit_message(content="")

        if voice_client is not None:
            await voice_client.disconnect()

    @discord.ui.button(
        custom_id="skip_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏩"
    )
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        global SKIP_FLAG
        global SONG_QUEUE
        global voice_client

        await interaction.response.edit_message(content="")

        SKIP_FLAG = True

        if voice_client is not None:
            voice_client.stop()

        if len(SONG_QUEUE) > 1:
            await reset_player(interaction)
            play()
        else:
            if voice_client is not None:
                await voice_client.disconnect()

    @discord.ui.button(
        custom_id="loop_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji="🔁"
    )
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        global IS_LOOPED

        IS_LOOPED = not IS_LOOPED

        if IS_LOOPED:
            button.style = discord.ButtonStyle.primary
        else:
            button.style = discord.ButtonStyle.secondary

        await interaction.response.edit_message(content="", view=self)
