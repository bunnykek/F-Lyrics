import argparse
import os
import importlib

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

MODULES = []
for module in os.listdir('modules'):
    modulepath = os.path.join('modules', module)
    if os.path.isfile(modulepath):
        mname = module[:-3]
        globals()[mname] = importlib.import_module(f'modules.{mname}')
        MODULES.append(globals()[mname])

class Flyrics:
    """
    from flyrics import Flyrics\n
    lyric = Flyrics()\n
    lyricsList = lyric.fetch("https://open.spotify.com/album/xxxxxxxxxx")
    """
    def fetch(self, url):
        for module in MODULES:
            result = module.REGEX.search(url)
            if result:
                instance =  module.Lyrics(url, api=True)
                return instance.jsonResponse

if __name__ == "__main__":
    print(banner)
    parser = argparse.ArgumentParser(description="Modular lyrics fetcher")
    parser.add_argument('URL', help="Album or track URL")
    args = parser.parse_args()
    url = args.URL

    for module in MODULES:
        result = module.REGEX.search(url)
        if result:
            print(f"{module.NAME} URL detected.")
            print("Fetching the lyrics...")
            module.Lyrics(url, api=False)
            print("Done.")
            break
