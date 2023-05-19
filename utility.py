import json
import os

with open("config.json") as f:
    config = json.load(f)

    SYNCED = config['synced_lyrics']
    PLAIN = config['plain_lyrics']
    LYRIC_PATH = config['lyric_file_path']


def saveLyrics(synced_lyric, plain_lyric, title, artist, album, trackNo, year):
    lyric_path = LYRIC_PATH.format(title=title, artist=artist, album=album, trackNo=str(trackNo), year=year)

    if not os.path.exists('/'.join(lyric_path.split('/')[:-1])):
        os.makedirs('/'.join(lyric_path.split('/')[:-1]))

    if SYNCED and synced_lyric:
        with open(lyric_path+'.lrc', "w+",encoding='utf-8') as f:
            f.write(synced_lyric)
    if PLAIN and plain_lyric:
        with open(lyric_path+'.txt', 'w+', encoding='utf-8') as f:
            f.write(plain_lyric)