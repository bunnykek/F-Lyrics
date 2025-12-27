# made by @bunnykek

from modulefinder import Module
import re
import requests
from sanitize_filename import sanitize
from utility import Utility


class Tidal(Module):
    NAME = "Tidal"
    REGEX = re.compile(r"https:\/\/tidal\.com\/(track|album)\/(\d+)")

    def __init__(self, url: str, config: dict, api: bool):
        self.session = requests.session()

        HEADERS = {
            'authorization': config['tidal']['auth_bearer'],
        }
        self.session.headers.update(HEADERS)
        kind, id_ = Tidal.REGEX.search(url).groups()

        if kind == 'track':
            self.jsonResponse = [self.getTrackLyrics(id_, dict(), api)]

        else:
            self.jsonResponse = self.getAlbumLyrics(id_, dict(), api)

    def getResponse(self):
        return self.jsonResponse

    def getAlbumLyrics(self, albumid: str, data: dict, api: bool):
        params = {
            'albumId': albumid,
            'countryCode': 'US',
            'locale': 'en_US',
            'deviceType': 'BROWSER',
        }
        response = self.session.get(
            'https://tidal.com/v1/pages/album', params=params)

        metadata = response.json()

        # print(response.text)

        lyricsJson = list()
        for track in metadata['rows'][1]['modules'][0]['pagedList']['items']:
            trackid = track['item']['id']
            trackJson = self.getTrackLyrics(trackid, data, api)
            lyricsJson.append(trackJson)

        return lyricsJson

    def getTrackLyrics(self, trackid: str, data: dict, api: bool):
        params = {
            'countryCode': 'US',
            'locale': 'en_US',
            'deviceType': 'BROWSER',
        }

        response = self.session.get(
            f'https://listen.tidal.com/v1/tracks/{trackid}', params=params)
        metadata = response.json()

        title = sanitize(metadata['title'])
        trackNo = metadata['trackNumber']
        artist = sanitize(metadata['artist']['name'])
        album = sanitize(metadata['album']['title'])
        year = metadata['streamStartDate'][0:4]

        lyric_response = self.session.get(
            f'https://openapi.tidal.com/v2/tracks/{trackid}?include=lyrics',
            params=params,
        ).json()
        
        print(json.dumps(lyric_response, indent=4))

        plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n\n"
        synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"

        try:
            plain_lyric += lyric_response.get('included')[0]['attributes'].get('text', '')
            synced_lyric += lyric_response.get('included')[0]['attributes'].get('lrcText', '')
        except (IndexError, KeyError, TypeError):
            print(f"No lyrics found for {title} by {artist}")

        if not api:
            Utility.saveLyrics(synced_lyric, plain_lyric, title,
                               artist, album, trackNo, year)

        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }
