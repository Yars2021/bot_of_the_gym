import discord

from configs import global_vars


class Player(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.sound_module = global_vars.SOUND_FUNCTIONS

    @discord.ui.button(
        custom_id="stop_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏹️"
    )
    async def stop(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        if self.sound_module.voice_client is not None:
            await self.sound_module.voice_client.disconnect()

        await interaction.edit(content="")

    @discord.ui.button(
        custom_id="skip_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏩"
    )
    async def skip(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        if self.sound_module.voice_client is not None:
            self.sound_module.voice_client.stop()

        if len(self.sound_module.song_queue) > 1:
            await self.sound_module.reset_player(interaction)
            self.sound_module.play()
        else:
            if self.sound_module.voice_client is not None:
                await self.sound_module.voice_client.disconnect()

        await interaction.edit(content="")

    @discord.ui.button(
        custom_id="loop_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji="🔁"
    )
    async def loop(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        self.sound_module.is_looped = not self.sound_module.is_looped

        if self.sound_module.is_looped:
            button.style = discord.ButtonStyle.primary
        else:
            button.style = discord.ButtonStyle.secondary

        await interaction.edit(content="", view=self)
