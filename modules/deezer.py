# made by @bunnykek

import re
import requests
from sanitize_filename import sanitize
from utility import Utility
from modules.module import Module


class Deezer(Module):
    NAME = "Deezer"
    REGEX = re.compile(r"https:\/\/www\.deezer\.com\/(track|album)\/(\d+)")

    def __init__(self, url, config: dict, api=False):
        self.session = requests.session()
        self.cookies = {
            'arl': config['deezer']['arl']
        }
        self.session.cookies.update(self.cookies)
        self.__updatebearer()
        kind, id_ = Deezer.REGEX.search(url).groups()

        if kind == 'track':
            self.jsonResponse = [self.getTrackLyrics(id_, dict(), config, api)]

        else:
            self.jsonResponse = self.getAlbumLyrics(id_, dict(), config, api)

    def __updatebearer(self):
        params = {
            'jo': 'p',
            'rto': 'c',
            'i': 'c',
        }
        response = self.session.post(
            'https://auth.deezer.com/login/arl', params=params).json()
        self.session.headers.update(
            {'authorization': 'Bearer '+response['jwt']})

    def getResponse(self):
        return self.jsonResponse

    def getAlbumLyrics(self, albumid, data: dict, config: dict, api):
        response = self.session.get(f'https://api.deezer.com/album/{albumid}')
        metadata = response.json()
        year = metadata['release_date'][0:4]
        lyricsJson = list()
        for i, track in enumerate(metadata['tracks']['data']):
            trackid = track['id']
            data = {
                "trackNo": i+1,
                "year": year,
                "trackjson": track
            }
            trackJson = self.getTrackLyrics(trackid, data, config, api)
            lyricsJson.append(trackJson)

        return lyricsJson

    def getTrackLyrics(self, trackid, data: dict, config: dict, api):
        if not "trackjson" in data:
            data["trackjson"] = self.session.get(
                f"https://api.deezer.com/track/{trackid}").json()
            year = data["trackjson"]['release_date'][0:4]

        title = sanitize(data["trackjson"]['title'])
        artist = sanitize(data["trackjson"]['name'])
        album = sanitize(data["trackjson"]['title'])

        json_data = {
            'operationName': 'SynchronizedTrackLyrics',
            'variables': {
                'trackId': str(trackid),
            },
            'query': 'query SynchronizedTrackLyrics($trackId: String!) {\n  track(trackId: $trackId) {\n    ...SynchronizedTrackLyrics\n    __typename\n  }\n}\n\nfragment SynchronizedTrackLyrics on Track {\n  id\n  lyrics {\n    ...Lyrics\n    __typename\n  }\n  album {\n    cover {\n      small: urls(pictureRequest: {width: 100, height: 100})\n      medium: urls(pictureRequest: {width: 264, height: 264})\n      large: urls(pictureRequest: {width: 800, height: 800})\n  explicitStatus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Lyrics on Lyrics {\n  id\n  copyright\n  text\n  writers\n  synchronizedLines {\n    ...LyricsSynchronizedLines\n    __typename\n  }\n  __typename\n}\n\nfragment LyricsSynchronizedLines on LyricsSynchronizedLine {\n  lrcTimestamp\n  line\n  lineTranslated\n  milliseconds\n  duration\n  __typename\n}',
        }

        lyric_response = self.session.post(
            'https://pipe.deezer.com/api', json=json_data).json()
        # print(lyric_response)

        plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n"
        synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"

        try:
            plain_lyric += lyric_response.get('data').get(
                'track').get('lyrics').get('text')+"\n"

            for line in lyric_response.get('data').get('track').get('lyrics').get('synchronizedLines'):
                synced_lyric += f"{line['lrcTimestamp']} {line['line']}\n"

            plain_lyric += "\nWriters: " + lyric_response.get('data').get('track').get('lyrics').get(
                'writers') + "\n" + "Copyright: " + lyric_response.get('data').get('track').get('lyrics').get('copyright')
            synced_lyric += "\nWriters: " + lyric_response.get('data').get('track').get('lyrics').get(
                'writers') + "\n" + "Copyright: " + lyric_response.get('data').get('track').get('lyrics').get('copyright')
        except:
            pass

        if not api:
            Utility.saveLyrics(synced_lyric, plain_lyric, title,
                               artist, album, data.get("trackNo", 1), year)

        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }
