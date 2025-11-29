import json
import os
from pathlib import Path

_config = None


def getConfig():
    global _config
    if _config is None:
        with open("config.json") as f:
            _config = json.load(f)
    return _config


class Utility:
    @staticmethod
    def getConfig():
        return getConfig()

    @staticmethod
    def saveLyrics(synced_lyric, plain_lyric, title, artist, album, trackNo, year):
        config = getConfig()
        lyric_path = config['lyric_file_path'].format(
            title=title, artist=artist, album=album, trackNo=str(trackNo), year=year
        )

        # Create directory if it doesn't exist
        Path(lyric_path).parent.mkdir(parents=True, exist_ok=True)

        # Save synced lyrics
        if config['synced_lyrics'] and synced_lyric:
            with open(f"{lyric_path}.lrc", "w", encoding='utf-8') as f:
                f.write(synced_lyric)

        # Save plain lyrics
        if config['plain_lyrics'] and plain_lyric:
            with open(f"{lyric_path}.txt", "w", encoding='utf-8') as f:
                f.write(plain_lyric)
