# made by @bunnykek

import argparse
import datetime
import re 
import json
import requests
from sanitize_filename import sanitize
from utility import saveLyrics

NAME = "Spotify"
REGEX = re.compile(r"https:\/\/open\.spotify\.com\/(track|album)\/([\d|\w]+)")

with open("config.json") as f:
    config = json.load(f)
    AUTH_BEARER = config['spotify']['auth_bearer']

HEADERS = {
    'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'DNT': '1',
    'accept-language': 'en-GB',
    'sec-ch-ua-mobile': '?0',
    'app-platform': 'WebPlayer',
    'authorization': AUTH_BEARER,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
    'accept': 'application/json',
    'Referer': 'https://open.spotify.com/',
    'spotify-app-version': '1.2.35.583.g729c23d6',
    'sec-ch-ua-platform': '"Windows"',
}

# def tokencheckupdate():
#     print("Checking the token...")
#     response = requests.get("https://api.spotify.com/v1/albums?ids=4UlGauD7ROb3YbVOFMgW5u&market=from_token", headers=HEADERS)
#     if response.status_code != 200:
#         print("Token expired. Refreshing...")
#         cookies = {
#         'sp_dc': SP_DC,
#         }

#         params = {
#             'reason': 'transport',
#             'productType': 'web-player',
#         }

#         response = requests.get('https://open.spotify.com/get_access_token', params=params, cookies=cookies)
#         print(response.text)
#         accessToken = response.json()["accessToken"]
#         with open("config.json", 'r+') as f:
#             config = json.load(f)
#             config['spotify']['auth_bearer'] = f"Bearer {accessToken}"
#             HEADERS['authorization'] = config['spotify']['auth_bearer']
#             f.seek(0)
#             # print(json.dumps(config, indent=3))
#             json.dump(config, f, indent=4)
#     else:
#         print("Token is alive.")


def convert_milliseconds(milliseconds):
    # Create a timedelta object with the provided milliseconds
    delta = datetime.timedelta(milliseconds=milliseconds)

    # Extract the hours, minutes, seconds, and milliseconds from the timedelta
    hours = delta.seconds // 3600
    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    # Format the hours, minutes, seconds, and milliseconds into the desired format
    formatted_time = "{:02d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)

    return formatted_time

class Lyrics:
    def __init__(self, url, api = False):
        self.session = requests.session()
        self.session.headers.update(HEADERS)
        kind, id_ = REGEX.search(url).groups()
        
        # tokencheckupdate()

        if kind == 'track':
            self.jsonResponse = [self.getTrackLyrics(id_, api)]
        
        else:
            self.jsonResponse = self.getAlbumLyrics(id_, api)

    def getAlbumLyrics(self, albumid, api):
        response = self.session.get(
            f'https://api.spotify.com/v1/albums?ids={albumid}&market=from_token')
        
        # print(response.text)
        metadata = response.json()['albums'][0]
        
        lyricsJson = list()
        for track in metadata['tracks']['items']:
            trackid = track['id']
            trackJson = self.getTrackLyrics(trackid, api)
            lyricsJson.append(trackJson)
        
        return lyricsJson

    def getTrackLyrics(self, trackid, api):
        response = self.session.get(f'https://api.spotify.com/v1/tracks?ids={trackid}&market=from_token')
        metadata = response.json()['tracks'][0]

        title = sanitize(metadata['name'])
        trackNo = metadata['track_number']
        artworkcode = metadata['album']['images'][0]['url'].split("/")[-1]

        artist = sanitize(metadata['album']['artists'][0]['name'])
        album = sanitize(metadata['album']['name'])
        year = metadata['album']['release_date'][0:4]

        params = {
            'format': 'json',
            'vocalRemoval': 'false',
            'market': 'from_token',
        }

        response = self.session.get(
            f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{trackid}/image/https%3A%2F%2Fi.scdn.co%2Fimage%2F{artworkcode}',
            params=params,
        )

        plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n\n"
        synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"
        
        lines = response.json()['lyrics']['lines']
        for line in lines:
            startms = int(line['startTimeMs'])
            words = line['words']
            timeStamp = convert_milliseconds(startms)
            plain_lyric += words+'\n'
            synced_lyric += f'[{timeStamp}]{words}\n'

        if not api:
            saveLyrics(synced_lyric, plain_lyric, title, artist, album, trackNo, year)
        
        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }