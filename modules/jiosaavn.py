# made by @bunnykek

import re
import requests
from sanitize_filename import sanitize
from utility import Utility
from modules.module import Module


class Jiosaavn(Module):
    NAME = "Jiosaavn"
    REGEX = re.compile(r"https://www\.jiosaavn\.com/(album|song)/.+?/(.+)")
    CLEANR = re.compile('<.*?>')

    def __init__(self, url: str, config: dict, api: bool):
        self.session = requests.session()
        kind, id_ = Jiosaavn.REGEX.search(url).groups()

        if kind == 'song':
            self.jsonResponse = [self.getTrackLyrics(id_, dict(), config, api)]

        else:
            self.jsonResponse = self.getAlbumLyrics(id_, dict(), config, api)

    def __cleanhtml(self, raw_html):
        cleantext = re.sub(Jiosaavn.CLEANR, '', raw_html)
        return cleantext

    def getResponse(self):
        return self.jsonResponse

    def getAlbumLyrics(self, albumid: str, data: dict, config: dict, api: bool):
        response = self.session.get(
            f'https://www.jiosaavn.com/api.php?__call=webapi.get&token={albumid}&type=album&_format=json')
        metadata = response.json()
        album_artist = metadata['primary_artists']
        lyricsJson = list()
        for i, track in enumerate(metadata['songs']):
            trackid = Jiosaavn.REGEX.search(track['perma_url']).group(2)
            data = {
                "trackNo": i+1,
                "albumArtist": album_artist,
                "trackjson": track
            }
            trackJson = self.getTrackLyrics(trackid, data, config, api)
            lyricsJson.append(trackJson)

        return lyricsJson

    def getTrackLyrics(self, trackid: str, data: dict, config: dict, api: bool):
        trackjson = data.get("trackjson", None)
        if not trackjson:
            trackjson = self.session.get(
                f"https://www.jiosaavn.com/api.php?__call=webapi.get&token={trackid}&type=song&_format=json").json()
            trackjson = trackjson[f"{list(trackjson.keys())[0]}"]
            artist = sanitize(trackjson['primary_artists'])
        else:
            artist = sanitize(
                data.get("albumArtist", trackjson['primary_artists']))

        year = trackjson['year']
        title = sanitize(trackjson['song'])
        album = sanitize(trackjson['album'])

        lyric_response = self.session.get(
            "https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id=" + trackjson['id']).json()
        # print(lyric_response)

        plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n\n"
        synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"

        try:
            lyrics = lyric_response.get("lyrics")
            if lyrics is not None:
                lyrics = lyrics.replace('<br>', '\n')
                lyrics = self.__cleanhtml(lyrics)
            # print(lyric_response)

            plain_lyric += lyrics
        except:
            pass

        if not api:
            Utility.saveLyrics(synced_lyric, plain_lyric, title,
                               artist, album, data.get("trackNo", 1), year)

        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }
