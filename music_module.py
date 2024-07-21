import discord
import os
import yt_dlp


MUSIC_ROOT = os.path.dirname(__file__)

MUSIC_DIR = "yt"

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

        return -1, []


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


def pop_and_continue(voice_client):
    global IS_LOOPED
    global IS_PLAYING
    global SKIP_FLAG
    global SONG_QUEUE

    IS_PLAYING = False

    last_song = SONG_QUEUE.pop(0)

    if IS_LOOPED and not SKIP_FLAG:
        SONG_QUEUE.append(last_song)
    else:
        remove_file(last_song["filename"])

    SKIP_FLAG = False

    if len(SONG_QUEUE) <= 0:
        clean_files()

    play_first(voice_client)


def play_first(voice_client):
    global FFMPEG_OPTIONS
    global IS_PLAYING
    global SONG_QUEUE

    if len(SONG_QUEUE) > 0 and not IS_PLAYING:
        IS_PLAYING = True

        if voice_client is not None and voice_client.is_connected():
            voice_client.play(discord.FFmpegPCMAudio(source=SONG_QUEUE[0]["filename"], **FFMPEG_OPTIONS),
                              after=lambda e: pop_and_continue(voice_client))


async def join_channel(interaction):
    global voice_client
    global voice_channel

    voice_client = interaction.guild.voice_client
    voice_channel = interaction.user.voice.channel

    if voice_client is None or not voice_client.is_connected():
        voice_client = await voice_channel.connect()
    else:
        await voice_client.move_to(interaction.user.voice.channel)


async def leave_channel():
    pass


async def find(interaction, request: str):
    original_response = await interaction.original_response()

    header_code, titles = fetch_header_yt(request)

    if header_code != 0:
        await original_response.edit(content="", embed=discord.Embed(
            title="По запросу ничего не найдено",
            colour=0xf50000))
    else:
        if len(titles) == 1:
            queued = titles[0]
        else:
            queued = ""

            for index in range(len(titles)):
                queued += str(index + 1) + ". " + titles[index] + "\n"

        await original_response.edit(content="", embed=discord.Embed(
            title="Добавляю в очередь",
            description=queued,
            colour=0x00b0f4))

    return header_code


async def load(interaction, request: str):
    global SONG_QUEUE
    global player

    for entry in fetch_files_yt(request):
        SONG_QUEUE.append(entry)

    if len(SONG_QUEUE) <= 0:
        await interaction.channel.send(embed=discord.Embed(
            title="Ошибка скачивания",
            colour=0xf50000))
    else:
        player = await interaction.channel.send(view=PlayerPanel(), embed=discord.Embed(
                title="Сейчас играет",
                description=SONG_QUEUE[0]["title"],
                colour=0x7a00f5))


async def play():
    # play_first(interaction.guild.voice_client)
    pass


async def show_queue(interaction):
    global SONG_QUEUE

    if len(SONG_QUEUE) <= 0:
        info_embed = discord.Embed(title="Очередь пуста", colour=0xf50000)
    else:
        message = ""

        for index in range(len(SONG_QUEUE)):
            message += (str(index + 1) + ". " + SONG_QUEUE[index]["title"] + "\n")

        info_embed = discord.Embed(title="Очередь музыки", description=message, colour=0x7a00f5)

    await interaction.response.send_message(embed=info_embed, ephemeral=True)


async def show_song_info(interaction):
    global SONG_QUEUE

    if len(SONG_QUEUE) <= 0:
        info_embed = discord.Embed(title="Очередь пуста", colour=0xf50000)
    else:
        info_embed = discord.Embed(title=SONG_QUEUE[0]["title"], colour=0x7a00f5)
        info_embed.set_image(url=SONG_QUEUE[0]["thumbnail"])

    await interaction.response.send_message(embed=info_embed, ephemeral=True)


async def terminate():
    global voice_client
    global voice_channel

    clean_files()

    if voice_client is not None:
        await voice_client.disconnect()

    voice_channel = None
    voice_client = None

    if player is not None:
        await player.delete()


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
        await interaction.response.edit_message(content="")
        await terminate()

    @discord.ui.button(
        custom_id="skip_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏩"
    )
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        global SONG_QUEUE
        global player
        global voice_client
        global voice_channel

        await interaction.response.edit_message(content="")

        # ToDo
