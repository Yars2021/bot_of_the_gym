import discord
from discord import app_commands
from discord.ext import tasks
import validators

import birthday_module
import music_module
import notifications_module
import size_module
import utils

########################################################################################################################
#  константы
########################################################################################################################


TOKEN, SERVER_ID, BOT_CHANNEL, ADMIN_IDS = utils.read_config("./.bot_config")

intents = discord.Intents.default()
intents.dm_messages = True
intents.members = True
client = discord.Client(intents=intents)
command_tree = app_commands.CommandTree(client)


########################################################################################################################
#  администрирование
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


@command_tree.command(
    name="patch",
    description="Отобразить последние изменения",
    guild=discord.Object(id=SERVER_ID)
)
async def command_update(interaction: discord.Interaction) -> None:
    global ADMIN_IDS
    global BOT_CHANNEL
    global client

    if str(interaction.user.id) in ADMIN_IDS:
        await interaction.response.send_message("Изменения:", delete_after=utils.MESSAGE_TIMER[0])
        await utils.show_patchonote(client, BOT_CHANNEL)
    else:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])


########################################################################################################################
#  size_mod
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
    stats_embed = discord.Embed(title=title, description=table, colour=0xb85300)

    await interaction.response.send_message(embed=stats_embed, delete_after=utils.MESSAGE_TIMER[2])


########################################################################################################################
#  music_mod
########################################################################################################################


@command_tree.command(
    name="play",
    description="music_mod, Играть по ссылке или названию (YouTube)",
    guild=discord.Object(id=SERVER_ID)
)
async def command_play(interaction: discord.Interaction, request: str) -> None:
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message(embed=discord.Embed(
            description="Для использования нужно находиться в голосовом канале",
            colour=0xf50000), ephemeral=True)
    else:
        await interaction.response.send_message("Ищу... Это может занять некоторе время")
        await music_module.find_and_play(interaction, request)


@command_tree.command(
    name="right_play",
    description="music_mod, ♂Играть♂ по названию (YouTube)",
    guild=discord.Object(id=SERVER_ID)
)
async def command_right_play(interaction: discord.Interaction, request: str) -> None:
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message(embed=discord.Embed(
            description="Для использования нужно находиться в голосовом канале",
            colour=0xf50000), ephemeral=True)
    else:
        if not validators.url(request):
            await interaction.response.send_message("Ищу... Это может занять некоторе время")
            await music_module.find_and_play(interaction, request + " right version")
        else:
            await interaction.response.send_message(embed=discord.Embed(
                description="Эта команда не может искать по ссылке",
                colour=0xf50000), ephemeral=True)


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

    if member == client.user:
        if after.channel is None:
            await music_module.terminate()
        elif before.channel is not None and after.channel != before.channel:
            await music_module.update_channel(after.channel)


########################################################################################################################
#  notifications_mod
########################################################################################################################


@command_tree.command(
    name="notify",
    description="notifications_mod, Добавить напоминание",
    guild=discord.Object(id=SERVER_ID)
)
async def command_notify(interaction: discord.Interaction, timezone: int, day: int, month: int, year: int,
                         hours: int, minutes: int, text: str) -> None:
    if timezone > 12 or timezone < -12:
        await interaction.response.send_message(embed=discord.Embed(
            description="Параметр timezone показывает часовой пояс относительно времени UTC.\n"
                        "**-12 <= timezone <= 12**",
            colour=0xf50000), ephemeral=True)
    else:
        code, first, second = notifications_module.form_date_and_time(timezone, day, month, year, hours, minutes)

        if code == "error":
            await interaction.response.send_message(embed=discord.Embed(
                description=first + second,
                colour=0xf50000), ephemeral=True)
        else:
            notifications_module.create_notification(interaction.user.id, first, second, text)

            await interaction.response.send_message(embed=discord.Embed(
                description="Уведомление успешно создано",
                colour=0x00b0f4), ephemeral=True)


@tasks.loop(seconds=30)
async def notifications_loop():
    global client

    await notifications_module.check_notifications(client)


@tasks.loop(hours=24)
async def notifications_cleanup_loop():
    notifications_module.clean_files()


########################################################################################################################
#  birthday_mod
########################################################################################################################


@tasks.loop(hours=24)
async def birthday_loop():
    global SERVER_ID
    global BOT_CHANNEL
    global client

    birthday_module.extract_data()
    await birthday_module.iterate(client.get_channel(int(BOT_CHANNEL)), client.get_guild(int(SERVER_ID)))


########################################################################################################################
#  инициализация
########################################################################################################################


@client.event
async def on_ready():
    global BOT_CHANNEL
    global client
    global command_tree

    size_module.init()
    notifications_loop.start()
    notifications_cleanup_loop.start()
    birthday_loop.start()

    await command_tree.sync(guild=discord.Object(id=SERVER_ID))
    await utils.show_update_info(client, BOT_CHANNEL)

    print("Bot is up!")


client.run(TOKEN)
