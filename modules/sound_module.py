import discord

import asyncio
import os
import random
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
        self.is_paused = False
        self.is_playing = False
        self.skip_flag = False
        self.songs_to_load = []
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

    async def join_for_sounds(self, interaction):
        self.voice_client = interaction.guild.voice_client

        if interaction.user.voice is not None:
            self.voice_channel = interaction.user.voice.channel

            if self.voice_client is not None:
                await self.voice_client.move_to(self.voice_channel)
            else:
                self.voice_client = await self.voice_channel.connect(reconnect=True)

            self.sounds_active = True

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

        if self.voice_client is not None and not self.is_playing and len(self.song_queue) <= 0:
            await self.voice_client.disconnect()

    def get_next_sound(self):
        if len(self.sound_queue) > 0:
            self.sound_queue.pop(0)

            if len(self.sound_queue) > 0:
                self.play_first_sound()

    def play_first_sound(self):
        if len(self.sound_queue) > 0 and self.sounds_active:
            if self.voice_client is not None and self.voice_client.is_connected():
                self.voice_client.play(discord.FFmpegPCMAudio(
                    source=self.soundboard_directory_path + self.sound_queue[0], **self.ffmpeg_options),
                                  after=lambda e: self.get_next_sound())

    def is_locked(self):
        return self.is_playing or len(self.song_queue) > 0

    def queue_sound(self, path):
        if self.sounds_active:
            self.sound_queue.append(path)

            if self.voice_client is not None and not self.voice_client.is_playing():
                self.play_first_sound()

    async def terminate_sounds(self):
        self.sound_queue = []

        if self.voice_client is not None:
            self.voice_client.stop()

        self.voice_client = None
        self.voice_channel = None
        self.listening_thread = None

        self.sounds_active = False
        self.listening = False

    def clean_files(self):
        if os.path.exists(os.path.join(self.music_root, self.music_dir)):
            os.system("rm -rf " + os.path.join(self.music_root, self.music_dir))

    def remove_file(self, path):
        if os.path.exists(os.path.exists(os.path.join(self.music_root, self.music_dir) + "/" + path)):
            os.system("rm -f " + os.path.join(self.music_root, self.music_dir) + "/" + path)

    async def reset_player(self, ctx):
        if self.player is not None:
            await self.player.delete()

        if len(self.song_queue) > 0:
            self.player = await ctx.channel.send(view=Player(), embed=utils.full_music_cover_embed(
                "Сейчас играет",
                self.song_queue[0]["title"]
            ))

    def fetch_single_file_yt(self, request):
        try:
            info = self.ytdl.extract_info(request, download=True)

            if "entries" in info:
                return -1, "Ошибка формата при скачивании"
            else:
                return 0, self.ytdl.prepare_filename(info)

        except Exception as e:
            return -1, f"Ошибка скеачивания: {e}"

    def fetch_headers_yt(self, url):
        titles = []

        try:
            info = self.ytdl.extract_info(url, download=False)

            if "entries" not in info:
                titles = [{
                    "title": info["title"],
                    "thumbnail": info["thumbnail"],
                    "url": info["webpage_url"]
                }]
            else:
                for entry in info["entries"]:
                    titles.append({
                        "title": entry["title"],
                        "thumbnail": entry["thumbnail"],
                        "url": entry["webpage_url"]
                    })

            return 0, titles

        except Exception as e:
            return -1, [f"Ошибка поиска: {e}"]

    def load_first_song(self):
        if len(self.songs_to_load) > 0:
            code, result = self.fetch_single_file_yt(self.songs_to_load[0]["url"])

            if code == 0:
                for song in self.song_queue:
                    if song["title"] == self.songs_to_load[0]["title"]:
                        song["filename"] = result

            self.songs_to_load.pop(0)

    def load_song_by_name(self, name: str):
        if len(self.songs_to_load) > 0:
            url = ""
            index = 0

            for song in self.songs_to_load:
                if song["title"] == name:
                    url = song["url"]
                    break

                index += 1

            if url != "":
                code, result = self.fetch_single_file_yt(url)

                if code == 0:
                    for song in self.song_queue:
                        if song["title"] == name:
                            song["filename"] = result

                self.songs_to_load.pop(index)

    def shuffle(self):
        if len(self.song_queue) > 1:
            current_song = self.song_queue.pop(0)
            random.shuffle(self.song_queue)
            shuffled_queue = [current_song]
            shuffled_queue.extend(self.song_queue)
            self.song_queue = shuffled_queue

    def pop_and_continue(self):
        self.is_playing = False

        if len(self.song_queue) > 0:
            last_song = self.song_queue.pop(0)

            if not self.is_looped or self.skip_flag:
                self.remove_file(last_song["filename"])
            else:
                self.song_queue.append(last_song)

            self.skip_flag = False

            if len(self.song_queue) > 0:
                self.play()

    def play(self):
        if len(self.song_queue) > 0 and not self.is_playing:
            self.is_playing = True

            if self.voice_client is not None and self.voice_client.is_connected():
                if "filename" not in self.song_queue[0]:
                    self.load_song_by_name(self.song_queue[0]["title"])

                self.voice_client.play(discord.FFmpegPCMAudio(
                    source=self.song_queue[0]["filename"], **self.ffmpeg_options),
                    after=lambda e: self.pop_and_continue())

    async def find(self, ctx, request: str):
        header_code, search_result = self.fetch_headers_yt(request)

        if header_code != 0:
            await ctx.edit(content="", embed=utils.error_embed("Ошибка поиска: " + str(search_result[0])))
        else:
            if len(search_result) == 1:
                queued_title = search_result[0]["title"]
                self.song_queue.append(search_result[0])
                self.songs_to_load.append(search_result[0])
            else:
                queued_title = ""

                for index in range(len(search_result)):
                    queued_title += str(index + 1) + ". " + search_result[index]["title"] + "\n"
                    self.song_queue.append(search_result[index])
                    self.songs_to_load.append(search_result[index])

            await ctx.edit(content="", embed=utils.full_info_embed(
                "Добавляю в очередь",
                queued_title
            ))

        return header_code

    async def find_and_play(self, ctx, request):
        header_code = await self.find(ctx, request)

        if header_code == 0:
            self.load_first_song()
            await self.reset_player(ctx)

            if not self.is_playing:
                await self.join_channel(ctx)
                self.play()
                await self.leave_channel()

    def pause(self):
        if self.voice_client is not None:
            self.voice_client.pause()

    def resume(self):
        if self.voice_client is not None:
            self.voice_client.resume()

    async def update_channel(self, channel):
        if self.voice_client is not None and channel is not None:
            self.voice_channel = channel
            await self.voice_client.move_to(channel)

    async def terminate(self):
        self.clean_files()

        if self.voice_client is not None:
            self.voice_client.stop()

        self.voice_client = None
        self.voice_channel = None
        self.is_looped = False
        self.is_paused = False
        self.is_playing = False
        self.skip_flag = False
        self.songs_to_load = []
        self.song_queue = []

        if self.player is not None:
            await self.player.delete()

        self.player = None

    async def start_listening(self):
        if self.listening_thread is None:
            self.listening_thread = Thread(target=self.listen_commands, args=())
            self.listening_thread.start()

    def listen_commands(self):
        while self.listening:
            print("Listening...")

        print("Stopped listening")
