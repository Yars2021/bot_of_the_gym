import discord
from discord import app_commands
from discord.ext import tasks
import validators

import birthday_module
import music_module
import notifications_module
import size_module
import sound_module
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
        await interaction.response.send_message(embed=utils.error_embed("Недостаточно прав"),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])
    else:
        await interaction.response.send_message(embed=utils.info_embed("Обновление..."),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[0])
        await utils.update_bot(interaction)


@command_tree.command(
    name="patch",
    description="Отобразить последние изменения",
    guild=discord.Object(id=SERVER_ID)
)
async def command_patch(interaction: discord.Interaction) -> None:
    global ADMIN_IDS
    global BOT_CHANNEL
    global client

    if str(interaction.user.id) not in ADMIN_IDS:
        await interaction.response.send_message(embed=utils.error_embed("Недостаточно прав"),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])
    else:
        await interaction.response.send_message(embed=utils.info_embed("Загружаю данные..."),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[0])
        await utils.show_patchonote(client, BOT_CHANNEL)


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
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[2])


@command_tree.command(
    name="sum",
    description="size_mod, Считает сумму сегодняшних длин",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_sum(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(size_module.get_sum(
        interaction.created_at), delete_after=utils.MESSAGE_TIMER[3])


@command_tree.command(
    name="stats",
    description="size_mod, Показывает сегодняшнюю статистику",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_stats(interaction: discord.Interaction) -> None:
    global SERVER_ID
    global client

    title, table = await size_module.get_stats(client.get_guild(int(SERVER_ID)), interaction.created_at)

    await interaction.response.send_message(embed=utils.message_embed(title, table, 0xb85300),
                                            delete_after=utils.MESSAGE_TIMER[3])


########################################################################################################################
#  music_mod
########################################################################################################################


@command_tree.command(
    name="play",
    description="music_mod, Играть по ссылке или названию",
    guild=discord.Object(id=SERVER_ID)
)
async def command_play(interaction: discord.Interaction, request: str) -> None:
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message(
            embed=utils.error_embed("Для использования нужно находиться в голосовом канале"),
            ephemeral=True)
    else:
        if sound_module.ACTIVE:
            await sound_module.leave()

        await interaction.response.send_message("Ищу... Это может занять некоторе время")

        if validators.url(request) and request.find("https://open.spotify.com") != -1:
            code, conversion_result = music_module.process_spotify_link(request)

            if code == "ok":
                request = conversion_result
            else:
                request = ""

                await interaction.response.edit_message(
                    embed=utils.error_embed(f"Ошибка поиска по ссылке Spotify: {conversion_result}"),
                    ephemeral=True)

        if len(request) > 0:
            await music_module.find_and_play(interaction, request)


@command_tree.command(
    name="right_play",
    description="music_mod, ♂Играть♂ по названию (YouTube)",
    guild=discord.Object(id=SERVER_ID)
)
async def command_right_play(interaction: discord.Interaction, request: str) -> None:
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message(
            embed=utils.error_embed("Для использования нужно находиться в голосовом канале"),
            ephemeral=True)
    else:
        if validators.url(request):
            await interaction.response.send_message(
                embed=utils.error_embed("Эта команда не может искать по ссылке"),
                ephemeral=True)
        else:
            if sound_module.ACTIVE:
                await sound_module.leave()

            await interaction.response.send_message("Ищу... Это может занять некоторе время")
            await music_module.find_and_play(interaction, request + " right version")


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
        await interaction.response.send_message(
            embed=utils.error_embed("Параметр timezone показывает часовой пояс относительно времени UTC.\n"
                                    "**-12 <= timezone <= 12**"),
            ephemeral=True)
    else:
        code, first, second = notifications_module.form_date_and_time(timezone, day, month, year, hours, minutes)

        if code == "error":
            await interaction.response.send_message(
                embed=utils.error_embed(first + second),
                ephemeral=True)
        else:
            notifications_module.create_notification(interaction.user.id, first, second, text)

            await interaction.response.send_message(
                embed=utils.info_embed("Напоминание успешно создано"),
                ephemeral=True)


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


@command_tree.command(
    name="birthday",
    description="birthday_mod, Добавить данные о дне рождения",
    guild=discord.Object(id=SERVER_ID)
)
async def command_birthday(interaction: discord.Interaction, user_id: str, day: int, month: int, pref: str) -> None:
    global ADMIN_IDS

    if str(interaction.user.id) not in ADMIN_IDS:
        await interaction.response.send_message(embed=utils.error_embed("Недостаточно прав"),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])
    else:
        if not utils.check_date(day, month):
            await interaction.response.send_message(embed=utils.error_embed("Ошибка в дате"),
                                                    ephemeral=True,
                                                    delete_after=utils.MESSAGE_TIMER[1])
        else:
            birthday_module.add_birthday(user_id, day, month, pref)
            birthday_module.extract_data()

            await interaction.response.send_message(embed=utils.info_embed("День рождения успешно добавлен"),
                                                    ephemeral=True)


@command_tree.command(
    name="birthday_table",
    description="birthday_mod, Просмотреть список зарегистрированных дней рождения",
    guild=discord.Object(id=SERVER_ID)
)
async def command_birthday_table(interaction: discord.Interaction) -> None:
    global ADMIN_IDS

    if str(interaction.user.id) not in ADMIN_IDS:
        await interaction.response.send_message(embed=utils.error_embed("Недостаточно прав"),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])
    else:
        await interaction.response.send_message(embed=utils.message_embed(
            "Таблица дней рождения",
            await birthday_module.show_table(client.get_guild(int(SERVER_ID))),
            0x00b0f4), ephemeral=True)


@tasks.loop(hours=24)
async def birthday_loop():
    global SERVER_ID
    global BOT_CHANNEL
    global client

    birthday_module.extract_data()
    await birthday_module.iterate(client.get_channel(int(BOT_CHANNEL)), client.get_guild(int(SERVER_ID)))


########################################################################################################################
#  sound_mod
########################################################################################################################


@command_tree.command(
    name="controls",
    description="sound_mod, Вывести интерфейс управления",
    guild=discord.Object(id=SERVER_ID)
)
async def command_birthday_table(interaction: discord.Interaction) -> None:
    global ADMIN_IDS

    if str(interaction.user.id) in ADMIN_IDS:
        await interaction.response.send_message(view=sound_module.ButtonPanel())
        await interaction.followup.send(view=sound_module.ControlPanel())
    else:
        await interaction.response.send_message(embed=utils.error_embed("Недостаточно прав"),
                                                ephemeral=True,
                                                delete_after=utils.MESSAGE_TIMER[1])


########################################################################################################################
#  инициализация
########################################################################################################################


@client.event
async def on_voice_state_update(member, before, after):
    global client

    if member == client.user:
        if after.channel is None:
            if sound_module.ACTIVE:
                await sound_module.leave()
            else:
                await music_module.terminate()
        elif before.channel is not None and after.channel != before.channel:
            await music_module.update_channel(after.channel)


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
