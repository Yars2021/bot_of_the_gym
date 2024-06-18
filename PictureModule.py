from AbstractModule import AbstractModule

import aiohttp
import requests
from random import randint


class PictureModule(AbstractModule):
    PICTURE_TOPICS = [
        "cat",
        "gym",
        "space"
    ]

    PICTURE_RESOLUTIONS = [
        "500x500",
        "750x750"
    ]

    BASE_URL = "https://source.unsplash.com/"

    def __init__(self):
        super().__init__("picture_mod")

    def activate(self):
        super(PictureModule, self).activate()

    def deactivate(self):
        super(PictureModule, self).deactivate()

    def get_topics(self):
        return self.PICTURE_TOPICS

    def get_resolutions(self):
        return self.PICTURE_RESOLUTIONS

    def get_base_url(self):
        return self.BASE_URL

    def set_base_url(self, base_url):
        self.BASE_URL = base_url

    async def get_random_pic(self, interaction, resolution, request):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL + resolution + "/?" + request) as image:
                await interaction.response.send_message(image.url)

    async def get_profile_pic(self, resolution, request):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL + resolution + "/?" + request) as image:
                return requests.get(image.url).content

    async def random_profile_pic(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL +
                                   self.PICTURE_RESOLUTIONS[randint(0, len(self.PICTURE_RESOLUTIONS) - 1)] + "/?" +
                                   self.PICTURE_TOPICS[randint(0, len(self.PICTURE_TOPICS) - 1)]) as image:
                return requests.get(image.url).content
