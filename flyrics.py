import argparse
import os
import importlib

from modules.deezer import Deezer
from modules.spotify import Spotify
from modules.tidal import Tidal
from modules.applemusic import AppleMusic
from modules.jiosaavn import Jiosaavn

from modules.module import Module
from utility import Utility

banner = """
 /$$$$$$$$         /$$                           /$$                    
| $$_____/        | $$                          |__/                    
| $$              | $$       /$$   /$$  /$$$$$$  /$$  /$$$$$$$  /$$$$$$$
| $$$$$    /$$$$$$| $$      | $$  | $$ /$$__  $$| $$ /$$_____/ /$$_____/
| $$__/   |______/| $$      | $$  | $$| $$  \__/| $$| $$      |  $$$$$$ 
| $$              | $$      | $$  | $$| $$      | $$| $$       \____  $$
| $$              | $$$$$$$$|  $$$$$$$| $$      | $$|  $$$$$$$ /$$$$$$$/
|__/              |________/ \____  $$|__/      |__/ \_______/|_______/ 
                             /$$  | $$                                  
                            |  $$$$$$/                                  
                             \______/  

                     A Modular lyrics fetcher
                               --by @bunnykek"""


class Flyrics:

    """
    from flyrics import Flyrics\n
    lyric = Flyrics()\n
    lyricsList = lyric.fetch("https://open.spotify.com/album/xxxxxxxxxx")
    """

    def __init__(self):
        self.modules: list[type[Module]] = [
            Deezer, Spotify, Tidal, AppleMusic, Jiosaavn]

    def fetch(self, url, api=True):
        for module in self.modules:
            result = module.REGEX.search(url)
            if result:
                instance = module(url, Utility.getConfig(), api=api)
                return instance.getResponse()


if __name__ == "__main__":
    print(banner)
    parser = argparse.ArgumentParser(description="Modular lyrics fetcher")
    parser.add_argument('URL', help="Album or track URL")
    args = parser.parse_args()
    url = args.URL

    flyricsInstance = Flyrics()
    flyricsInstance.fetch(url, api=False)
