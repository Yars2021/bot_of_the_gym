import discord

from configs import soundboard, global_vars


class SoundboardPanel(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.sound_module = global_vars.SOUND_FUNCTIONS

    @discord.ui.button(
        custom_id="0",
        label=soundboard.BUTTONS[0]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[0]["emoji"]
    )
    async def sound0(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[0]["path"])

    @discord.ui.button(
        custom_id="1",
        label=soundboard.BUTTONS[1]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[1]["emoji"]
    )
    async def sound1(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[1]["path"])

    @discord.ui.button(
        custom_id="2",
        label=soundboard.BUTTONS[2]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[2]["emoji"]
    )
    async def sound2(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[2]["path"])

    @discord.ui.button(
        custom_id="3",
        label=soundboard.BUTTONS[3]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[3]["emoji"]
    )
    async def sound3(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[3]["path"])

    @discord.ui.button(
        custom_id="4",
        label=soundboard.BUTTONS[4]["label"],
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[4]["emoji"]
    )
    async def sound4(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[4]["path"])

    @discord.ui.button(
        custom_id="5",
        label=soundboard.BUTTONS[5]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[5]["emoji"]
    )
    async def sound5(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[5]["path"])

    @discord.ui.button(
        custom_id="6",
        label=soundboard.BUTTONS[6]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[6]["emoji"]
    )
    async def sound6(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[6]["path"])

    @discord.ui.button(
        custom_id="7",
        label=soundboard.BUTTONS[7]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[7]["emoji"]
    )
    async def sound7(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[7]["path"])

    @discord.ui.button(
        custom_id="8",
        label=soundboard.BUTTONS[8]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[8]["emoji"]
    )
    async def sound8(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[8]["path"])

    @discord.ui.button(
        custom_id="9",
        label=soundboard.BUTTONS[9]["label"],
        row=1,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[9]["emoji"]
    )
    async def sound9(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[9]["path"])

    @discord.ui.button(
        custom_id="10",
        label=soundboard.BUTTONS[10]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[10]["emoji"]
    )
    async def sound10(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[10]["path"])

    @discord.ui.button(
        custom_id="11",
        label=soundboard.BUTTONS[11]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[11]["emoji"]
    )
    async def sound11(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[11]["path"])

    @discord.ui.button(
        custom_id="12",
        label=soundboard.BUTTONS[12]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[12]["emoji"]
    )
    async def sound12(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[12]["path"])

    @discord.ui.button(
        custom_id="13",
        label=soundboard.BUTTONS[13]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[13]["emoji"]
    )
    async def sound13(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[13]["path"])

    @discord.ui.button(
        custom_id="14",
        label=soundboard.BUTTONS[14]["label"],
        row=2,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[14]["emoji"]
    )
    async def sound14(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[14]["path"])

    @discord.ui.button(
        custom_id="15",
        label=soundboard.BUTTONS[15]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[15]["emoji"]
    )
    async def sound15(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[15]["path"])

    @discord.ui.button(
        custom_id="16",
        label=soundboard.BUTTONS[16]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[16]["emoji"]
    )
    async def sound16(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[16]["path"])

    @discord.ui.button(
        custom_id="17",
        label=soundboard.BUTTONS[17]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[17]["emoji"]
    )
    async def sound17(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[17]["path"])

    @discord.ui.button(
        custom_id="18",
        label=soundboard.BUTTONS[18]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[18]["emoji"]
    )
    async def sound18(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[18]["path"])

    @discord.ui.button(
        custom_id="19",
        label=soundboard.BUTTONS[19]["label"],
        row=3,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[19]["emoji"]
    )
    async def sound19(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[19]["path"])

    @discord.ui.button(
        custom_id="20",
        label=soundboard.BUTTONS[20]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[20]["emoji"]
    )
    async def sound20(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[20]["path"])

    @discord.ui.button(
        custom_id="21",
        label=soundboard.BUTTONS[21]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[21]["emoji"]
    )
    async def sound21(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[21]["path"])

    @discord.ui.button(
        custom_id="22",
        label=soundboard.BUTTONS[22]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[22]["emoji"]
    )
    async def sound22(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[22]["path"])

    @discord.ui.button(
        custom_id="23",
        label=soundboard.BUTTONS[23]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[23]["emoji"]
    )
    async def sound23(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[23]["path"])

    @discord.ui.button(
        custom_id="24",
        label=soundboard.BUTTONS[24]["label"],
        row=4,
        style=discord.ButtonStyle.secondary,
        emoji=soundboard.BUTTONS[24]["emoji"]
    )
    async def sound24(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="")

        self.sound_module.queue_sound(soundboard.BUTTONS[24]["path"])
