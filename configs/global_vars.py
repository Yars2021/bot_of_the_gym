import utils

from modules.notifications_module import NotificationsModule
from modules.size_module import SizeModule
from modules.sound_module import SoundModule


TOKEN, SERVER_ID, BOT_CHANNEL, ADMIN_IDS = utils.read_config("./.bot_config")

EXTENSIONS = [
    "cogs.admin_cog",
    "cogs.size_cog",
    "cogs.birthday_cog",
    "cogs.notifications_cog",
    "cogs.sound_cog"
]

SIZE_FUNCTIONS = SizeModule()
NOTIFICATIONS_FUNCTIONS = NotificationsModule()
SOUND_FUNCTIONS = SoundModule()
