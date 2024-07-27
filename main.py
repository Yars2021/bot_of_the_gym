import discord
from discord.ext import commands

from configs import global_vars

client = commands.Bot(intents=discord.Intents.all())


@client.event
async def on_voice_state_update(member, before, after):
    global client

    if member == client.user:
        if after.channel is None:
            if not global_vars.SOUND_FUNCTIONS.sounds_active:
                await global_vars.SOUND_FUNCTIONS.terminate()
            else:
                await global_vars.SOUND_FUNCTIONS.terminate_sounds()
        elif before.channel is not None and after.channel != before.channel:
            await global_vars.SOUND_FUNCTIONS.update_channel(after.channel)


@client.event
async def on_connect():
    global client

    for extension in global_vars.EXTENSIONS:
        client.load_extension(extension)

    await client.sync_commands()

    print("Синхронизация модулей завершена")


@client.event
async def on_ready():
    print("Бот активен!")


client.run(global_vars.TOKEN)
