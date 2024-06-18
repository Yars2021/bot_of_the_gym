import datetime

import discord
from discord import app_commands
from discord.ext import tasks

import utils
from AudioModule import AudioModule
from AudioModule import Soundboard
from NotificationsModule import NotificationsModule
from PictureModule import PictureModule
from SizeModule import SizeModule


########################################################################################################################
#                                                    Константы
########################################################################################################################


with open('./.discord_token', 'r', encoding="utf-8") as f:
    TOKEN = f.read()

SERVER_ID = 770365960854831115
ADMIN_USERNAMES = ["yars_games", "lw01f"]

MESSAGE_TIMER = {
    "absent": 0.0,
    "short": 15.0,
    "normal": 60.0,
    "extended": 120.0
}

MODULES = {
    "size_mod": SizeModule(),
    "picture_mod": PictureModule(),
    "audio_mod": AudioModule(),
    "notifications_mod": NotificationsModule()
}


########################################################################################################################
#                                                    Переменные
########################################################################################################################


intents = discord.Intents.default()
intents.dm_messages = True
client = discord.Client(intents=intents)
command_tree = app_commands.CommandTree(client)


########################################################################################################################
#                                                 Системные команды
########################################################################################################################


@command_tree.command(
    name="lsmod",
    description="Просмотр списка модулей и их состояний",
    guild=discord.Object(id=SERVER_ID)
)
async def command_lsmod(interaction: discord.Interaction) -> None:
    global MODULES

    await utils.lsmod(interaction, MODULES)


@command_tree.command(
    name="enmod",
    description="Активировать модуль",
    guild=discord.Object(id=SERVER_ID)
)
async def command_enmod(interaction: discord.Interaction, module: str) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES):
        await utils.set_mod_state(interaction, "Модуль активирован", module, True, MODULES)


@command_tree.command(
    name="dismod",
    description="Деактивировать модуль",
    guild=discord.Object(id=SERVER_ID)
)
async def command_dismod(interaction: discord.Interaction, module: str) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES):
        await utils.set_mod_state(interaction, "Модуль деактивирован", module, False, MODULES)


@command_tree.command(
    name="update",
    description="Pull changes from Git and restart the bot",
    guild=discord.Object(id=SERVER_ID)
)
async def command_update(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES):
        await utils.pull_and_restart(interaction)


########################################################################################################################
#                                                 Команды size_mod
########################################################################################################################


@command_tree.command(
    name="size",
    description="size_mod, считает сегодняшнюю длину",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_size(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["size_mod"].MODULE, MODULES):
        await interaction.response.send_message(MODULES["size_mod"].get_size(str(interaction.user.id),
                                                                             str(interaction.user),
                                                                             interaction.created_at),
                                                delete_after=MESSAGE_TIMER["extended"])


@command_tree.command(
    name="sum",
    description="size_mod, считает сумму сегодняшних длин",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_sum(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["size_mod"].MODULE, MODULES):
        await interaction.response.send_message(MODULES["size_mod"].get_sum(interaction.created_at),
                                                delete_after=MESSAGE_TIMER["normal"])


@command_tree.command(
    name="stats",
    description="size_mod, показывает статистику за сегодня",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_stats(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["size_mod"].MODULE, MODULES):
        await interaction.response.send_message(MODULES["size_mod"].get_sizes(interaction.created_at),
                                                delete_after=MESSAGE_TIMER["normal"])


@command_tree.command(
    name="chance",
    description="size_mod, статистика шансов выпадения фичи",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_chance(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["size_mod"].MODULE, MODULES):
        await interaction.response.send_message(MODULES["size_mod"].get_chances(interaction.created_at),
                                                ephemeral=True,
                                                delete_after=MESSAGE_TIMER["normal"])


########################################################################################################################
#                                                Команды audio_mod
########################################################################################################################


@command_tree.command(
    name="music_on",
    description="Включить проигрывание музыки",
    guild=discord.Object(id=SERVER_ID)
)
async def command_music_on(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES):
        MODULES["audio_mod"].set_music_status(True)
        await interaction.response.send_message("Включаю музыкальный сервис", delete_after=MESSAGE_TIMER["short"])


@command_tree.command(
    name="music_off",
    description="Выключить проигрывание музыки",
    guild=discord.Object(id=SERVER_ID)
)
async def command_music_off(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES):
        MODULES["audio_mod"].set_music_status(False)
        await interaction.response.send_message("Выключаю музыкальный сервис", delete_after=MESSAGE_TIMER["short"])


@command_tree.command(
    name="sound_on",
    description="Включить звуковую панель",
    guild=discord.Object(id=SERVER_ID)
)
async def command_sound_on(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES):
        MODULES["audio_mod"].set_sound_status(True)
        await interaction.response.send_message("Включаю звуковую панель", delete_after=MESSAGE_TIMER["short"])


@command_tree.command(
    name="sound_off",
    description="Выключить звуковую панель",
    guild=discord.Object(id=SERVER_ID)
)
async def command_sound_off(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES):
        MODULES["audio_mod"].set_sound_status(False)
        await interaction.response.send_message("Выключаю звуковую панель", delete_after=MESSAGE_TIMER["short"])


@command_tree.command(
    name="play",
    description="Играть по ссылке или названию",
    guild=discord.Object(id=SERVER_ID)
)
async def command_play(interaction: discord.Interaction, request: str) -> None:
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await MODULES["audio_mod"].queue_song(interaction, request)
        await MODULES["audio_mod"].listen_activity()


@command_tree.command(
    name="rplay",
    description="♂Играть♂ по названию",
    guild=discord.Object(id=SERVER_ID)
)
async def command_rplay(interaction: discord.Interaction, request: str) -> None:
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await MODULES["audio_mod"].queue_song(interaction, request + " right version")
        await MODULES["audio_mod"].listen_activity()


@command_tree.command(
    name="loop",
    description="Включить зацикливание",
    guild=discord.Object(id=SERVER_ID)
)
async def command_loop(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await interaction.response.send_message("Включаю зацикливание", delete_after=MESSAGE_TIMER["short"])
        MODULES["audio_mod"].MUSIC_FLAGS["IS_LOOPED"] = True


@command_tree.command(
    name="unloop",
    description="Выключить зацикливание",
    guild=discord.Object(id=SERVER_ID)
)
async def command_unloop(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await interaction.response.send_message("Выключаю зацикливание", delete_after=MESSAGE_TIMER["short"])
        MODULES["audio_mod"].MUSIC_FLAGS["IS_LOOPED"] = False


@command_tree.command(
    name="stop",
    description="Отключиться",
    guild=discord.Object(id=SERVER_ID)
)
async def command_stop(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await interaction.response.send_message("Отключаюсь...", delete_after=MESSAGE_TIMER["absent"])

        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect()

        MODULES["audio_mod"].drop_song_queue()
        MODULES["audio_mod"].drop_sound_queue()
        MODULES["audio_mod"].clean_files()
        MODULES["audio_mod"].reset_player()


@command_tree.command(
    name="pause",
    description="Пауза",
    guild=discord.Object(id=SERVER_ID)
)
async def command_pause(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await interaction.response.send_message("Пауза", delete_after=MESSAGE_TIMER["short"])

        if MODULES["audio_mod"].voice_client is not None:
            MODULES["audio_mod"].voice_client.pause()


@command_tree.command(
    name="resume",
    description="Продолжить воспроизведение",
    guild=discord.Object(id=SERVER_ID)
)
async def command_resume(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await interaction.response.send_message("Пауза", delete_after=MESSAGE_TIMER["short"])

        if MODULES["audio_mod"].voice_client is not None:
            MODULES["audio_mod"].voice_client.resume()


@command_tree.command(
    name="queue",
    description="Показать очередь треков",
    guild=discord.Object(id=SERVER_ID)
)
async def command_queue(interaction: discord.Interaction) -> None:
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await MODULES["audio_mod"].show_queue(interaction)


@command_tree.command(
    name="song",
    description="Подробнее о текущей песне",
    guild=discord.Object(id=SERVER_ID)
)
async def command_song(interaction: discord.Interaction) -> None:
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await MODULES["audio_mod"].get_song_info(interaction)


@command_tree.command(
    name="skip",
    description="Пропустить текущую песню, удалив ее из очереди",
    guild=discord.Object(id=SERVER_ID)
)
async def command_skip(interaction: discord.Interaction) -> None:
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_music_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        if len(MODULES["audio_mod"].SONG_QUEUE) <= 0:
            await interaction.response.send_message("Очередь пуста",
                                                    ephemeral=True, delete_after=MESSAGE_TIMER["short"])
            return

        await interaction.response.send_message("Пропускаю...", delete_after=MESSAGE_TIMER["short"])

        await MODULES["audio_mod"].skip(interaction)


@command_tree.command(
    name="init_sounds",
    description="Инициализация звуковой панели",
    guild=discord.Object(id=SERVER_ID)
)
async def command_init_sounds(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MODULES

    if await utils.check_module(interaction, MODULES["audio_mod"].MODULE, MODULES) and \
        await utils.check_sound_part(interaction, MODULES["audio_mod"]) and \
            await utils.check_voice(interaction):
        await interaction.response.send_message(view=Soundboard(MODULES["audio_mod"]))


########################################################################################################################
#                                                Команды picture_mod
########################################################################################################################


@command_tree.command(
    name="random_pic",
    description="Найти случайную картинку по теме в указанном разрешении",
    guild=discord.Object(id=SERVER_ID)
)
async def command_random_pic(interaction: discord.Interaction, resolution: str, request: str) -> None:
    global MODULES

    if await utils.check_module(interaction, MODULES["picture_mod"].MODULE, MODULES):
        await MODULES["picture_mod"].get_random_pic(interaction, resolution, request)


@command_tree.command(
    name="reset_avatar",
    description="Сменить картинку профиля на случайную",
    guild=discord.Object(id=SERVER_ID)
)
async def command_reset_avatar(interaction: discord.Interaction, resolution: str, request: str) -> None:
    global ADMIN_USERNAMES
    global MESSAGE_TIMER
    global MODULES

    global client

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["picture_mod"].MODULE, MODULES):
        await interaction.response.send_message("Меняю картинку профиля", delete_after=MESSAGE_TIMER["short"])

        await client.user.edit(avatar=await MODULES["picture_mod"].get_profile_pic(resolution, request))


@tasks.loop(hours=24)
async def profile_pic_routine():
    global MODULES

    await client.user.edit(avatar=await MODULES["picture_mod"].random_profile_pic())


########################################################################################################################
#                                            Команды notifications_mod
########################################################################################################################


@command_tree.command(
    name="clear_notification_history",
    description="Очистить историю нотификаций",
    guild=discord.Object(id=SERVER_ID)
)
async def command_clear_notification_history(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["notifications_mod"].MODULE, MODULES):
        await interaction.response.send_message("История очищена", ephemeral=True, delete_after=MESSAGE_TIMER["normal"])
        MODULES["notifications_mod"].clear_history()


@command_tree.command(
    name="force_clear_files",
    description="Принудительно удалить все старые файлы нотификаций",
    guild=discord.Object(id=SERVER_ID)
)
async def command_force_clear_files(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["notifications_mod"].MODULE, MODULES):
        await interaction.response.send_message("Старые файлы удалены", ephemeral=True, delete_after=MESSAGE_TIMER["normal"])
        MODULES["notifications_mod"].clear_old()


@command_tree.command(
    name="get_notification_history",
    description="Получить историю нотификаций",
    guild=discord.Object(id=SERVER_ID)
)
async def command_get_notification_history(interaction: discord.Interaction) -> None:
    global ADMIN_USERNAMES
    global MESSAGE_TIMER
    global MODULES

    if await utils.check_permissions(interaction, ADMIN_USERNAMES) and \
            await utils.check_module(interaction, MODULES["notifications_mod"].MODULE, MODULES):
        await interaction.response.send_message(MODULES["notifications_mod"].get_history(),
                                                ephemeral=True,
                                                delete_after=MESSAGE_TIMER["normal"])


@client.event
async def on_message(message):
    global MODULES

    if message.author != client.user and isinstance(message.channel, discord.DMChannel):
        if message.content == "/help":
            await message.channel.send("Команды:\n/help - выводит список доступных команд\n" +
                                       "/notify - создает напоминание на указанную дату и время.\n" +
                                       "\tИспользование: /notify <TZ> <DATE> <TIME> \"<TITLE>\" \"<TEXT>\"\n" +
                                       "\t\t<TZ> - часовой сдвиг относительно времени UTC, число от -24 до 24\n" +
                                       "\t\t<DATE> - дата в формате год-месяц-день (2024-06-18)\n" +
                                       "\t\t<TIME> - время в формате часы:минуты:секунды (19:11:42)\n" +
                                       "\t\t<TITLE> - звголовок напоминания, то, что отобразится в первую очередь\n" +
                                       "\t\t<TEXT> - текст напоминания\n" +
                                       "\t\tВАЖНО! - заголовк и текст указываются в двойных кавычках (\").\n" +
                                       "\t\tЭто позволяет использовать внутри них пробелы\n"
                                       "\tПример:\n" +
                                       "\t\t/notify 3 2024-06-18 19:43:50 \"Тестовый Заголовок\" \"Текст Напоминания\"")
        elif message.content.startswith("/notify"):
            args = message.content.split()

            try:
                timezone = int(args[1])
                if timezone < -24 or timezone > 24:
                    await message.channel.send("Неверный формат часового сдвига. Ожидается число от -24 до 24")

                complex_args = message.content.split("\"")

                MODULES["notifications_mod"].queue_notification(message.author.id,
                                                                timezone,
                                                                args[2],
                                                                args[3],
                                                                complex_args[1],
                                                                complex_args[3])

                MODULES["notifications_mod"].save_notification()

                await message.channel.send("Напоминание создано")
            except Exception:
                await message.channel.send("Неверный формат аргументов.\nИспользуйте /help для отображения справки")

        else:
            await message.channel.send("Неизвестная команда.\nИспользуйте /help для отображения списка команд")


@tasks.loop(seconds=0.5)
async def notifications_send_routine():
    global MODULES

    MODULES["notifications_mod"].save_notification()

    notifications_to_send = MODULES["notifications_mod"].notify_tick()

    for notification in notifications_to_send:
        author = await client.fetch_user(notification["author"])

        await author.send("**" + notification["title"] + "**")
        await author.send(notification["text"])


@tasks.loop(hours=24)
async def notifications_cleanup_routine():
    global MODULES

    MODULES["notifications_mod"].clear_old()


########################################################################################################################
#                                                 Включение бота
########################################################################################################################


@client.event
async def on_ready():
    global command_tree

    await command_tree.sync(guild=discord.Object(id=SERVER_ID))
    profile_pic_routine.start()
    notifications_send_routine.start()
    notifications_cleanup_routine.start()

    print("Bot is up!")


client.run(TOKEN)
