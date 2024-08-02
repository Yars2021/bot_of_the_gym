import utils

from modules.notifications_module import NotificationsModule
from modules.size_module import SizeModule
from modules.sound_module import SoundModule


TOKEN, YANDEX, SERVER_ID, BOT_CHANNEL, ADMIN_IDS = utils.read_config("./.bot_config")

EXTENSIONS = {
    "cogs.admin_cog": False,
    "cogs.size_cog": False,
    "cogs.birthday_cog": False,
    "cogs.notifications_cog": False,
    "cogs.sound_cog": False,
    "cogs.internet_cog": False
}

SIZE_FUNCTIONS = SizeModule()
NOTIFICATIONS_FUNCTIONS = NotificationsModule()
SOUND_FUNCTIONS = SoundModule()
