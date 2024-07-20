import discord
from discord import app_commands
from discord.ext import tasks

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
    description="size_mod, считает сегодняшнюю длину",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_size(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(size_module.get_size(
        str(interaction.user.id),
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[3])


@command_tree.command(
    name="sum",
    description="size_mod, считает сумму сегодняшних длин",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_sum(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(size_module.get_sum(
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[2])


@command_tree.command(
    name="stats",
    description="size_mod, показывает сегодняшнюю статистику",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_stats(interaction: discord.Interaction) -> None:
    global SERVER_ID
    global client

    await interaction.response.send_message(await size_module.get_stats(
        client.get_guild(int(SERVER_ID)),
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[2])



########################################################################################################################
#  Команды music_mod
########################################################################################################################





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
