# made by @bunnykek

import re 
import json
import requests
from sanitize_filename import sanitize
from utility import saveLyrics

NAME = "Tidal"
REGEX = re.compile(r"https:\/\/tidal\.com\/browse\/(track|album)\/(\d+)")

with open("config.json") as f:
    config = json.load(f)
    AUTH_BEARER = config['tidal']['auth_bearer']

HEADERS = {
    'authorization': AUTH_BEARER,
}

class Lyrics:
    def __init__(self, url, api = False):
        self.session = requests.session()
        self.session.headers.update(HEADERS)
        kind, id_ = REGEX.search(url).groups()
        
        if kind == 'track':
            self.jsonResponse = [self.getTrackLyrics(id_, api)]
        
        else:
            self.jsonResponse = self.getAlbumLyrics(id_, api)

    def getAlbumLyrics(self, albumid, api):
        params = {
            'albumId': albumid,
            'countryCode': 'US',
            'locale': 'en_US',
            'deviceType': 'BROWSER',
        }

        response = self.session.get('https://listen.tidal.com/v1/pages/album', params=params)
        
        # print(response.text)
        metadata = response.json()
        
        lyricsJson = list()
        for track in metadata['rows'][1]['modules'][0]['pagedList']['items']:
            trackid = track['item']['id']
            trackJson = self.getTrackLyrics(trackid, api)
            lyricsJson.append(trackJson)
        
        return lyricsJson

    def getTrackLyrics(self, trackid, api):
        params = {
            'countryCode': 'US',
            'locale': 'en_US',
            'deviceType': 'BROWSER',
        }

        response = self.session.get(f'https://listen.tidal.com/v1/tracks/{trackid}', params=params)
        metadata = response.json()

        print(metadata)
        title = sanitize(metadata['title'])
        trackNo = metadata['trackNumber']
        artist = sanitize(metadata['artist']['name'])
        album = sanitize(metadata['album']['title'])
        year = metadata['streamStartDate'][0:4]

        lyric_response = self.session.get(
            f'https://listen.tidal.com/v1/tracks/{trackid}/lyrics',
            params=params,
        ).json()


        plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n\n"
        synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"
        
        plain_lyric+=lyric_response.get('lyrics')
        synced_lyric+=lyric_response.get('subtitles')

        if not api:
            saveLyrics(synced_lyric, plain_lyric, title, artist, album, trackNo, year)
        
        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }