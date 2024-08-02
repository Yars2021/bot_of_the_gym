import utils

from modules.notifications_module import NotificationsModule
from modules.size_module import SizeModule
from modules.sound_module import SoundModule


MAIN_TOKEN, YANDEX, SERVER_ID, BOT_CHANNEL, ADMIN_IDS = utils.read_config("./.bot_config")

EXTENSIONS = {
    "cogs.admin_cog": False,
    "cogs.size_cog": False,
    "cogs.birthday_cog": False,
    "cogs.notifications_cog": False,
    "cogs.sound_cog": False,
    "cogs.internet_cog": False,
    "cogs.uploader_cog": False
}

SIZE_FUNCTIONS = SizeModule()
NOTIFICATIONS_FUNCTIONS = NotificationsModule()
SOUND_FUNCTIONS = SoundModule()

files_to_upload = "./data/yt_src/.files_to_upload"
uploaded_files = "./data/yt_src/.uploaded_files"
cloud_dir = "yt_sources_bot"
