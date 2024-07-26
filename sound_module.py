import asyncio
import discord
import music_module
import soundboard
import speech_recognition

from threading import Thread

DIRECTORY_PATH = "./soundboard/"

FFMPEG_OPTIONS = {
    "options": "-vn"
}

ACTIVE = False

LISTENING = False

SOUND_QUEUE = []

voice_client = None
voice_channel = None
listening_thread = None
recognizer = speech_recognition.Recognizer()


def get_next():
    global ACTIVE
    global SOUND_QUEUE

    if len(SOUND_QUEUE) > 0:
        SOUND_QUEUE.pop(0)

        if len(SOUND_QUEUE) > 0:
            play_first()


def play_first():
    global DIRECTORY_PATH
    global ACTIVE
    global SOUND_QUEUE
    global voice_client

    if len(SOUND_QUEUE) > 0 and ACTIVE:
        if voice_client is not None and voice_client.is_connected():
            voice_client.play(discord.FFmpegPCMAudio(source=DIRECTORY_PATH + SOUND_QUEUE[0], **FFMPEG_OPTIONS),
                              after=lambda e: get_next())


async def join(interaction):
    global ACTIVE
    global voice_client
    global voice_channel

    voice_client = interaction.guild.voice_client

    if interaction.user.voice is not None:
        voice_channel = interaction.user.voice.channel

        if voice_client is None:
            voice_client = await voice_channel.connect(reconnect=True)
        else:
            await voice_client.move_to(voice_channel)

        ACTIVE = True


async def leave():
    global ACTIVE
    global LISTENING
    global SOUND_QUEUE
    global voice_client
    global voice_channel
    global listening_thread

    SOUND_QUEUE = []

    if voice_client is not None:
        await voice_client.disconnect()

    voice_channel = None
    listening_thread = None

    ACTIVE = False
    LISTENING = False


def queue_sound(path):
    global ACTIVE
    global SOUND_QUEUE
    global voice_client

    if ACTIVE:
        SOUND_QUEUE.append(path)

        if voice_client is not None and not voice_client.is_playing():
            play_first()


def is_locked():
    return music_module.IS_PLAYING or len(music_module.SONG_QUEUE) > 0


async def start_listening():
    global listening_thread

    if listening_thread is None:
        listening_thread = Thread(target=listen_commands, args=())
        listening_thread.start()


def listen_commands():
    global LISTENING
    global voice_client
    global voice_channel
    global recognizer

    while LISTENING:

        print("Listening...")

    print("Stopped listening")


class ControlPanel(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="join_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="▶️"
    )
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not is_locked():
            await join(interaction)

            for child in self.children:
                if type(child) == discord.ui.Button and child.custom_id == "listen_btn":
                    child.disabled = False

        await interaction.response.edit_message(content="", view=self)

    @discord.ui.button(
        custom_id="leave_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏹️"
    )
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not is_locked():
            await leave()

            for child in self.children:
                if type(child) == discord.ui.Button and child.custom_id == "listen_btn":
                    child.style = discord.ButtonStyle.secondary
                    child.disabled = True

        await interaction.response.edit_message(content="", view=self)

    @discord.ui.button(
        custom_id="listen_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji="⏺️",
        disabled=True
    )
    async def listen(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        global ACTIVE
        global LISTENING
        global listening_thread

        if ACTIVE:
            LISTENING = not LISTENING

            if LISTENING:
                button.style = discord.ButtonStyle.primary
                await start_listening()
            else:
                button.style = discord.ButtonStyle.secondary
                listening_thread = None

        await interaction.response.edit_message(content="", view=self)


class ButtonPanel(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="0",
        label=soundboard.BUTTONS[0]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[0]["emoji"]
    )
    async def sound0(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[0]["path"])

    @discord.ui.button(
        custom_id="1",
        label=soundboard.BUTTONS[1]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[1]["emoji"]
    )
    async def sound1(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[1]["path"])

    @discord.ui.button(
        custom_id="2",
        label=soundboard.BUTTONS[2]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[2]["emoji"]
    )
    async def sound2(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[2]["path"])

    @discord.ui.button(
        custom_id="3",
        label=soundboard.BUTTONS[3]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[3]["emoji"]
    )
    async def sound3(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[3]["path"])

    @discord.ui.button(
        custom_id="4",
        label=soundboard.BUTTONS[4]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[4]["emoji"]
    )
    async def sound4(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[4]["path"])

    @discord.ui.button(
        custom_id="5",
        label=soundboard.BUTTONS[5]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[5]["emoji"]
    )
    async def sound5(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[5]["path"])

    @discord.ui.button(
        custom_id="6",
        label=soundboard.BUTTONS[6]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[6]["emoji"]
    )
    async def sound6(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[6]["path"])

    @discord.ui.button(
        custom_id="7",
        label=soundboard.BUTTONS[7]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[7]["emoji"]
    )
    async def sound7(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[7]["path"])

    @discord.ui.button(
        custom_id="8",
        label=soundboard.BUTTONS[8]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[8]["emoji"]
    )
    async def sound8(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[8]["path"])

    @discord.ui.button(
        custom_id="9",
        label=soundboard.BUTTONS[9]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[9]["emoji"]
    )
    async def sound9(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[9]["path"])

    @discord.ui.button(
        custom_id="10",
        label=soundboard.BUTTONS[10]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[10]["emoji"]
    )
    async def sound10(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[10]["path"])

    @discord.ui.button(
        custom_id="11",
        label=soundboard.BUTTONS[11]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[11]["emoji"]
    )
    async def sound11(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[11]["path"])

    @discord.ui.button(
        custom_id="12",
        label=soundboard.BUTTONS[12]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[12]["emoji"]
    )
    async def sound12(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[12]["path"])

    @discord.ui.button(
        custom_id="13",
        label=soundboard.BUTTONS[13]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[13]["emoji"]
    )
    async def sound13(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[13]["path"])

    @discord.ui.button(
        custom_id="14",
        label=soundboard.BUTTONS[14]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[14]["emoji"]
    )
    async def sound14(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[14]["path"])

    @discord.ui.button(
        custom_id="15",
        label=soundboard.BUTTONS[15]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[15]["emoji"]
    )
    async def sound15(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[15]["path"])

    @discord.ui.button(
        custom_id="16",
        label=soundboard.BUTTONS[16]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[16]["emoji"]
    )
    async def sound16(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[16]["path"])

    @discord.ui.button(
        custom_id="17",
        label=soundboard.BUTTONS[17]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[17]["emoji"]
    )
    async def sound17(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[17]["path"])

    @discord.ui.button(
        custom_id="18",
        label=soundboard.BUTTONS[18]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[18]["emoji"]
    )
    async def sound18(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[18]["path"])

    @discord.ui.button(
        custom_id="19",
        label=soundboard.BUTTONS[19]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[19]["emoji"]
    )
    async def sound19(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[19]["path"])

    @discord.ui.button(
        custom_id="20",
        label=soundboard.BUTTONS[20]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[20]["emoji"]
    )
    async def sound20(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[20]["path"])

    @discord.ui.button(
        custom_id="21",
        label=soundboard.BUTTONS[21]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[21]["emoji"]
    )
    async def sound21(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[21]["path"])

    @discord.ui.button(
        custom_id="22",
        label=soundboard.BUTTONS[22]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[22]["emoji"]
    )
    async def sound22(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[22]["path"])

    @discord.ui.button(
        custom_id="23",
        label=soundboard.BUTTONS[23]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[23]["emoji"]
    )
    async def sound23(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[23]["path"])

    @discord.ui.button(
        custom_id="24",
        label=soundboard.BUTTONS[24]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[24]["emoji"]
    )
    async def sound24(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="")

        queue_sound(soundboard.BUTTONS[24]["path"])
