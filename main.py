import discord
from discord import app_commands
from discord.ext import tasks
import os

import music_module
import size_module
import utils

########################################################################################################################
#  Константы
########################################################################################################################


TOKEN, SERVER_ID, ADMIN_IDS = utils.read_config("./.bot_config")

intents = discord.Intents.default()
intents.dm_messages = True
intents.members = True
client = discord.Client(intents=intents)
command_tree = app_commands.CommandTree(client)


########################################################################################################################
#  Команды администратора
########################################################################################################################


@command_tree.command(
    name="update",
    description="Обновить бота",
    guild=discord.Object(id=SERVER_ID)
)
async def command_update(interaction: discord.Interaction) -> None:
    global ADMIN_IDS

    if str(interaction.user.id) not in ADMIN_IDS:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])
    else:
        await interaction.response.send_message("Обновление...",
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[0])
        await utils.update_bot(interaction)


########################################################################################################################
#  Команды size_mod
########################################################################################################################


@command_tree.command(
    name="size",
    description="size_mod, Считает сегодняшнюю длину",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_size(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(size_module.get_size(
        str(interaction.user.id),
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[3])


@command_tree.command(
    name="sum",
    description="size_mod, Считает сумму сегодняшних длин",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_sum(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(size_module.get_sum(
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[2])


@command_tree.command(
    name="stats",
    description="size_mod, Показывает сегодняшнюю статистику",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_stats(interaction: discord.Interaction) -> None:
    global SERVER_ID
    global client

    title, table = await size_module.get_stats(client.get_guild(int(SERVER_ID)), interaction.created_at)
    stats_embed = discord.Embed(title=title, description=table, colour=0xf5e000)

    await interaction.response.send_message(embed=stats_embed, delete_after=utils.MESSAGE_TIMER[2])


########################################################################################################################
#  Команды music_mod
########################################################################################################################


@command_tree.command(
    name="play",
    description="music_mod, Играть по ссылке или названию (YouTube)",
    guild=discord.Object(id=SERVER_ID)
)
async def command_play(interaction: discord.Interaction, request: str) -> None:
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message("Для использования нужно находиться в голосовом канале", ephemeral=True)
    else:
        await interaction.response.send_message("Ищу... Это может занять некоторе время")

        header_code = await music_module.find(interaction, request)

        if header_code == 0:
            await music_module.load(interaction, request)
            await music_module.join_channel(interaction)
            #   start_playing


# @command_tree.command(
#     name="rplay",
#     description="music_mod, ♂Играть♂ по названию (YouTube)",
#     guild=discord.Object(id=SERVER_ID)
# )
# async def command_rplay(interaction: discord.Interaction, request: str) -> None:
#     global SERVER_ID
#
#     await interaction.response.send_message("♂Ищу♂...", delete_after=utils.MESSAGE_TIMER[0])
#     await music_module.find_and_queue(interaction, request + " right version")
#
#     await music_module.listen_activity(client.voice_clients, 10)
#     await music_module.check_voice(interaction.guild.voice_client, 5)


@command_tree.command(
    name="queue",
    description="music_mod, Показать очередь",
    guild=discord.Object(id=SERVER_ID)
)
async def command_queue(interaction: discord.Interaction) -> None:
    await music_module.show_queue(interaction)


@command_tree.command(
    name="song",
    description="music_mod, Подробнее о текущей песне",
    guild=discord.Object(id=SERVER_ID)
)
async def command_song(interaction: discord.Interaction) -> None:
    await music_module.show_song_info(interaction)


@client.event
async def on_voice_state_update(member, before, after):
    global client

    if after.channel is None and member == client.user:
        await music_module.terminate()


########################################################################################################################
#  Инициализация
########################################################################################################################


@client.event
async def on_ready():
    global client
    global command_tree

    size_module.init()

    await command_tree.sync(guild=discord.Object(id=SERVER_ID))
    await utils.show_patchonote(client)

    print("Bot is up!")


client.run(TOKEN)
