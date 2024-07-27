import discord

import asyncio
import os
import requests
import speech_recognition
import utils
import yt_dlp

from bs4 import BeautifulSoup
from panels.PlayerPanel import Player
from threading import Thread


class SoundModule:
    def __init__(self):
        self.sounds_active = False
        self.listening = False
        self.sound_queue = []

        self.is_looped = False
        self.is_playing = False
        self.skip_flag = False
        self.song_queue = []

        self.voice_client = None
        self.voice_channel = None
        self.listening_thread = None
        self.player = None

        self.soundboard_directory_path = "./data/soundboard/"
        self.music_root = os.path.join(os.path.dirname(__file__), "../data")
        self.music_dir = "yt_sources"

        self.ffmpeg_options = {
            "options": "-vn"
        }
        self.ytdl_options = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.music_root, self.music_dir, "%(extractor)s-%(id)s-%(title)s.%(ext)s"),
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

        self.recognizer = speech_recognition.Recognizer()
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_options)

    @staticmethod
    def process_spotify_link(link):
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "lxml")

            song = soup.find("meta", {"property": "og:title"})["content"]
            artist_link = soup.find("meta", {"name": "music:musician"})["content"]
            artist_page = BeautifulSoup(requests.get(artist_link).text, "lxml")
            artist = artist_page.find("meta", {"property": "og:title"})["content"]

            return "ok", str(song + " " + artist).replace("&", "and")

        except Exception as e:
            return "error", e

    def get_next(self):
        if len(self.sound_queue) > 0:
            self.sound_queue.pop(0)

            if len(self.sound_queue) > 0:
                self.play_first()

    def play_first(self):
        if len(self.sound_queue) > 0 and self.sounds_active:
            if self.voice_client is not None and self.voice_client.is_connected():
                self.voice_client.play(discord.FFmpegPCMAudio(
                    source=self.soundboard_directory_path + self.sound_queue[0], **self.ffmpeg_options),
                                  after=lambda e: self.get_next())

    async def join(self, interaction):
        self.voice_client = interaction.guild.voice_client

        if interaction.user.voice is not None:
            self.voice_channel = interaction.user.voice.channel

            if self.voice_client is None:
                self.voice_client = await self.voice_channel.connect(reconnect=True)
            else:
                await self.voice_client.move_to(self.voice_channel)

            self.sounds_active = True

    async def terminate_sounds(self):
        self.sound_queue = []

        if self.voice_client is not None:
            self.voice_client.stop()

        self.voice_client = None
        self.voice_channel = None
        self.listening_thread = None

        self.sounds_active = False
        self.listening = False

    def queue_sound(self, path):
        if self.sounds_active:
            self.sound_queue.append(path)

            if self.voice_client is not None and not self.voice_client.is_playing():
                self.play_first()

    def is_locked(self):
        return self.is_playing or len(self.song_queue) > 0

    def clean_files(self):
        if os.path.exists(os.path.join(self.music_root, self.music_dir)):
            os.system("rm -rf " + os.path.join(self.music_root, self.music_dir))

    def remove_file(self, path):
        if os.path.exists(os.path.exists(os.path.join(self.music_root, self.music_dir) + "/" + path)):
            os.system("rm -f " + os.path.join(self.music_root, self.music_dir) + "/" + path)

    def fetch_header_yt(self, url):
        titles = []

        try:
            info = self.ytdl.extract_info(url, download=False)

            if "entries" not in info:
                titles.append(info["title"])
            else:
                for entry in info["entries"]:
                    titles.append(entry["title"])

            return 0, titles

        except Exception as e:
            print(f"Ошибка поиска (анализ имен): {e}")

            return -1, [e]

    def fetch_files_yt(self, url):
        tracks = []

        try:
            info = self.ytdl.extract_info(url, download=True)

            if "entries" not in info:
                tracks = [{
                    "title": info["title"],
                    "thumbnail": info["thumbnail"],
                    "filename": self.ytdl.prepare_filename(info)
                }]
            else:
                for entry in info["entries"]:
                    tracks.append({
                        "title": entry["title"],
                        "thumbnail": entry["thumbnail"],
                        "filename": self.ytdl.prepare_filename(entry)
                    })

            return 0, tracks

        except Exception as e:
            return -1, [f"Ошибка поиска (скачивание источников): {e}"]

    def pop_and_continue(self):
        self.is_playing = False

        if len(self.sound_queue) > 0:
            last_song = self.song_queue.pop(0)

            if self.is_looped and not self.skip_flag:
                self.song_queue.append(last_song)
            else:
                self.remove_file(last_song["filename"])

            self.skip_flag = False

            if len(self.sound_queue) > 0:
                self.play()

    def play(self):
        if len(self.song_queue) > 0 and not self.is_playing:
            self.is_playing = True

            if self.voice_client is not None and self.voice_client.is_connected():
                self.voice_client.play(discord.FFmpegPCMAudio(
                    source=self.song_queue[0]["filename"], **self.ffmpeg_options),
                    after=lambda e: self.pop_and_continue())

    async def join_channel(self, ctx):
        self.voice_client = ctx.guild.voice_client
        self.voice_channel = ctx.user.voice.channel

        if self.voice_client is not None:
            await self.voice_client.move_to(self.voice_channel)
        else:
            self.voice_client = await self.voice_channel.connect(reconnect=True)

    async def leave_channel(self):
        while self.voice_client is not None and self.voice_client.is_playing():
            await asyncio.sleep(1)

        await asyncio.sleep(5)

        if self.voice_client is not None and not self.is_playing and not self.sounds_active:
            await self.voice_client.disconnect()

    async def find(self, ctx, request: str):
        header_code, search_result = self.fetch_header_yt(request)

        if header_code != 0:
            await ctx.edit(content="", embed=utils.error_embed("Ошибка поиска: " + str(search_result[0])))
        else:
            if len(search_result) == 1:
                queued = search_result[0]
            else:
                queued = ""

                for index in range(len(search_result)):
                    queued += str(index + 1) + ". " + search_result[index] + "\n"

            await ctx.edit(content="", embed=utils.full_info_embed(
                "Добавляю в очередь",
                queued
            ))

        return header_code

    async def reset_player(self, ctx):
        if self.player is not None:
            await self.player.delete()

        if len(self.song_queue) > 0:
            self.player = await ctx.channel.send(view=Player(), embed=utils.full_music_cover_embed(
                "Сейчас играет",
                self.song_queue[0]["title"]
            ))

    async def load(self, ctx, request: str):
        code, result = self.fetch_files_yt(request)

        if code == -1:
            await ctx.channel.send(embed=utils.error_embed(result[0]))
        else:
            for entry in result:
                self.song_queue.append(entry)

            if len(self.song_queue) > 0:
                await self.reset_player(ctx)
            else:
                await ctx.channel.send(embed=utils.error_embed("Ошибка скачивания"))

    async def terminate(self):
        self.clean_files()

        if self.voice_client is not None:
            self.voice_client.stop()

        self.voice_client = None
        self.voice_channel = None
        self.is_looped = False
        self.is_playing = False
        self.skip_flag = False
        self.song_queue = []

        if self.player is not None:
            await self.player.delete()

        self.player = None

    async def update_channel(self, channel):
        if self.voice_client is not None and channel is not None:
            self.voice_channel = channel
            await self.voice_client.move_to(channel)

    async def find_and_play(self, ctx, request):
        header_code = await self.find(ctx, request)

        if header_code == 0:
            await self.load(ctx, request)

            if not self.is_playing:
                await self.join_channel(ctx)
                self.play()
                await self.leave_channel()

    async def start_listening(self):
        if self.listening_thread is None:
            self.listening_thread = Thread(target=self.listen_commands, args=())
            self.listening_thread.start()

    def listen_commands(self):
        while self.listening:
            print("Listening...")

        print("Stopped listening")
