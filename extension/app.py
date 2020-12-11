from discordex import DexBot
from discordex.utils.node import File

from pymongo import MongoClient

class Discommu(DexBot):
    def __init__(self):
        self.config = File('config.json')
        self.db = MongoClient(f'mongodb+srv://admin:{self.config.db.password}@{self.config.db.url}/discommu?retryWrites=true&w=majority')['discommu']

        self.userCollection = self.db['users']
        self.postCollection = self.db['posts']
        self.categoryCollection = self.db['categories']

        super().__init__(self.config.command_prefix, allow_bots = False)

    def run(self):
        super().run(self.config.token)