import asyncio
import discord
import os
import yt_dlp


MUSIC_ROOT = os.path.dirname(__file__)

MUSIC_DIR = "yt"

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
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

IS_LOOPED = False

IS_PLAYING = False

SKIP_FLAG = False

SONG_QUEUE = []


def clean_files():
    global MUSIC_DIR

    if os.path.exists(MUSIC_DIR):
        os.system("rm -rf ./" + MUSIC_DIR)


def remove_file(path):
    global MUSIC_DIR

    if os.path.exists(os.path.exists("./" + MUSIC_DIR + "/" + path)):
        os.system("rm -f " + "./" + MUSIC_DIR + "/" + path)


def terminate():
    global IS_PLAYING
    global SONG_QUEUE

    IS_PLAYING = False
    SONG_QUEUE = []

    clean_files()


# Получить названия по ссылке
def fetch_header_yt(url):
    global YTDL_OPTIONS

    titles = []

    try:
        info = yt_dlp.YoutubeDL(YTDL_OPTIONS).extract_info(url, download=False)

        if "entries" not in info:
            titles.append(info["title"])
        else:
            for entry in info["entries"]:
                titles.append(entry["title"])

        return {
            "code": 0,
            "titles": titles
        }
    except Exception as e:
        print(f"Ошибка поиска (анализ имен): {e}")

        return {
            "code": -1,
            "titles": []
        }


# Найти и скачать звук по ссылке
def fetch_files_yt(url):
    global YTDL_OPTIONS

    tracks = []

    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
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

        except Exception as e:
            print(f"Ошибка поиска (скачивание): {e}")

    return tracks


# Перейти к следующему элементу очереди. Добавить в конец только что сыгранный элемент, если IS_LOOPED
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


# Найти и сыграть 0-й запрос из очереди
def play_first(voice_client):
    global IS_PLAYING
    global SONG_QUEUE

    if len(SONG_QUEUE) <= 0 or IS_PLAYING:
        return

    IS_PLAYING = True

    if voice_client is not None and voice_client.is_connected():
        voice_client.play(discord.FFmpegPCMAudio(SONG_QUEUE[0]["filename"]),
                          after=lambda e: pop_and_continue(voice_client))


async def find_and_queue(interaction, request: str):
    global IS_PLAYING
    global SONG_QUEUE

    yt_header = fetch_header_yt(request)

    if yt_header["code"] != 0:
        await interaction.channel.send(embed=discord.Embed(title="По запросу ничего не найдено", colour=0xf50000))
        return

    if len(yt_header["titles"]) == 1:
        await interaction.channel.send("Добавляю в очередь -- " + yt_header["titles"][0])
    else:
        playlist = ""

        for index in range(len(yt_header["titles"])):
            playlist += (str(index + 1) + ". " + yt_header["titles"][index] + "\n")

        print("Добавляю в очередь -- ПЛЕЙЛИСТ:\n" + playlist)

    for entry in fetch_files_yt(request):
        SONG_QUEUE.append(entry)

    voice_client = interaction.guild.voice_client

    if not IS_PLAYING:
        voice_channel = interaction.user.voice.channel

        if voice_client is None or not voice_client.is_connected():
            voice_client = await voice_channel.connect()
        else:
            await voice_client.move_to(voice_channel)

    play_first(voice_client)


async def listen_activity(voice_client, timeout):
    global IS_PLAYING

    while IS_PLAYING:
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(timeout)

        while IS_PLAYING:
            break
        else:
            terminate()

            if voice_client is not None:
                await voice_client.disconnect()


async def check_voice(voice_client, timeout):
    global IS_PLAYING

    while voice_client is not None:
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(timeout)

        while voice_client is not None:
            break
        else:
            terminate()


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
