import discord

from configs import global_vars


class ControlPanel(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.sound_module = global_vars.SOUND_FUNCTIONS

    @discord.ui.button(
        custom_id="join_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="▶️"
    )
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        if not self.sound_module.is_locked():
            await self.sound_module.join(interaction)

            for child in self.children:
                if type(child) == discord.ui.Button and child.custom_id == "listen_btn":
                    child.disabled = False

        await interaction.edit(content="", view=self)

    @discord.ui.button(
        custom_id="leave_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji="⏹️"
    )
    async def leave(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        if not self.sound_module.is_locked():
            if self.sound_module.voice_client is not None:
                await self.sound_module.voice_client.disconnect()

            await self.sound_module.terminate_sounds()

            for child in self.children:
                if type(child) == discord.ui.Button and child.custom_id == "listen_btn":
                    child.style = discord.ButtonStyle.secondary
                    child.disabled = True

        await interaction.edit(content="", view=self)

    @discord.ui.button(
        custom_id="listen_btn",
        label="",
        row=0,
        style=discord.ButtonStyle.secondary,
        emoji="⏺️",
        disabled=True
    )
    async def listen(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        if self.sound_module.sounds_active:
            self.sound_module.listening = not self.sound_module.listening

            if self.sound_module.listening:
                button.style = discord.ButtonStyle.primary
                await self.sound_module.start_listening()
            else:
                button.style = discord.ButtonStyle.secondary
                self.sound_module.listening_thread = None

        await interaction.edit(content="", view=self)
