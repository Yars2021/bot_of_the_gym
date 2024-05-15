import os
import subprocess
import sys

import AbstractModule
import AudioModule


async def check_permissions(interaction, permissions):
    if str(interaction.user) not in permissions:
        await interaction.response.send_message("Недостаточно прав", ephemeral=True)
        return False

    return True


async def check_module(interaction, module, modules):
    if module not in modules:
        await interaction.response.send_message("Модуль не найден", ephemeral=True)
        return False

    if not modules[module].STATUS:
        await interaction.response.send_message("Модуль неактивен", ephemeral=True)
        return False

    return True


async def check_voice(interaction):
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message("Для использования нужно находиться в голосовом канале",
                                                ephemeral=True)
        return False

    return True


async def lsmod(interaction, modules):
    output = "Список модулей:\n"

    for module in modules:
        status = "OFF"

        if modules[module].STATUS:
            status = "ON"

        output += ("\t" + modules[module].MODULE + ":\t" + status + "\n")

    await interaction.response.send_message(output, ephemeral=True)


async def set_mod_state(interaction, message, module: AbstractModule, status, modules):
    if module not in modules:
        await interaction.response.send_message("Модуль не найден: " + modules[module].MODULE, ephemeral=True)
        return

    modules[module].set_status(status)
    await interaction.response.send_message(message, ephemeral=True)


async def pull_and_restart(interaction):
    try:
        subprocess.run(["git", "pull"])

        await interaction.response.send_message("Code updated successfully. Restarting the bot...")

        subprocess.run([sys.executable, "bot.py"])
        quit()

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)


async def check_music_part(interaction, audio_mod: AudioModule):
    if not audio_mod.get_music_status():
        await interaction.response.send_message("Музыкальный сервис выключен")
        return False

    return True


async def check_sound_part(interaction, audio_mod: AudioModule):
    if not audio_mod.get_sound_status():
        await interaction.response.send_message("Звуковая панель выключена")
        return False

    return True
