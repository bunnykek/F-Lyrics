# made by @bunnykek

import argparse
import requests
import bs4
import json
import re
from sanitize_filename import sanitize
from utility import saveLyrics

NAME = "Apple Music"
REGEX = re.compile(
    "https://music.apple.com/(\w{2})/album/.+?/(\d+)(\?i=(\d+))?")

with open("config.json") as f:
    config = json.load(f)

    AUTH_BEARER = config['applemusic']['auth_bearer']
    TOKEN = config['applemusic']['media-user-token']

HEADERS = {
    "authorization": AUTH_BEARER,
    "media-user-token": TOKEN,
    "Origin": "https://music.apple.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://music.apple.com/",
    "content-type": "application/json",
    "x-apple-renewal": "true",
    "DNT": "1",
    "Connection": "keep-alive",
    'l': 'en-US'
}


def convert_time_sec(original_time):
    # Extract the seconds from the original time
    seconds = float(original_time.split('s')[0])

    # Convert seconds to minutes and remaining seconds
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    # Format minutes and remaining seconds into two-digit strings
    formatted_minutes = "{:02d}".format(minutes)
    formatted_seconds = "{:02.3f}".format(remaining_seconds)

    # Combine the formatted components into the desired format
    formatted_time = "{}:{}".format(formatted_minutes, formatted_seconds[:5])

    return formatted_time


def convert_time_format(original_time):
    # Check if the time is in the format "X:XX.XXX"
    if ":" in original_time:
        # Split the original time into minutes, seconds, and milliseconds
        minutes, seconds = map(float, original_time.split(':'))
        minutes = minutes + (seconds // 60)  # Add minutes from seconds
        seconds = seconds % 60

        # Convert the time to milliseconds
        milliseconds = (minutes * 60 * 1000) + (seconds * 1000)

    else:
        # Extract the milliseconds from the time
        milliseconds = int(float(original_time) * 1000)

    # Convert the milliseconds back to hours, minutes, seconds, and milliseconds
    hours = milliseconds // (60 * 60 * 1000)
    minutes = (milliseconds // (60 * 1000)) % 60
    seconds = (milliseconds // 1000) % 60
    milliseconds = milliseconds % 1000

    # Format the hours, minutes, seconds, and milliseconds into the desired format
    formatted_time = "{:02d}:{:02d}.{:03d}".format(
        int(minutes), int(seconds), int(milliseconds))

    return formatted_time


class Lyrics:
    def __init__(self, url, api=False) -> None:
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        region, albumid, trackFlag, trackid = REGEX.search(url).groups()

        if trackFlag:
            self.jsonResponse = [self.getTrackLyric(trackid, region, api)]

        else:
            self.jsonResponse = self.getAlbumLyric(albumid, region, api)

    def getAlbumLyric(self, albumid: str, region: str, api: bool):
        print("Getting lyrics for the whole album...")
        metadata = self.session.get(
            f"https://api.music.apple.com/v1/catalog/{region}/albums/{albumid}").json()
        metadata = metadata['data'][0]
        albumArtist = metadata['attributes']['artistName']

        lyricsJson = list()
        for track in metadata['relationships']['tracks']['data']:
            trackJson = self.getTrackLyric(
                track['id'], region, api, albumArtist)
            lyricsJson.append(trackJson)

        return lyricsJson

    def getTrackLyric(self, trackID: str, region: str, api: bool, albumArtist: str = None):
        metadata = self.session.get(
            f"https://api.music.apple.com/v1/catalog/{region}/songs/{trackID}").json()
        metadata = metadata['data'][0]

        title = sanitize(metadata['attributes']['name'])
        trackNo = metadata['attributes']['trackNumber']

        artist = sanitize(metadata['attributes']['artistName'])
        album = sanitize(metadata['attributes']['albumName'])
        year = metadata['attributes'].get('releaseDate')

        print(f"{trackNo}. {title}...")
        # print(json.dumps(metadata, indent=2))
        if not metadata['attributes']['hasLyrics']:
            print("Lyrics not available.")
            return

        response = self.session.get(
            f'https://amp-api.music.apple.com/v1/catalog/{region}/songs/{trackID}/lyrics')
        result = response.json()
        soup = bs4.BeautifulSoup(
            result['data'][0]['attributes']['ttml'], 'lxml')

        plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n\n"
        synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"
        paragraphs = soup.find_all("p")

        if 'itunes:timing="None"' in result['data'][0]['attributes']['ttml']:
            synced_lyric = None
            for line in paragraphs:
                plain_lyric += line.text+'\n'

        else:
            for paragraph in paragraphs:
                begin = paragraph.get('begin')
                if begin.count(':')>1:
                    timeStamp = ':'.join(begin.split(':')[1:])
                else:
                    timeStamp = convert_time_sec(begin) if 's' in begin else convert_time_format(begin)
                text = paragraph.text
                plain_lyric += text+'\n'
                synced_lyric += f'[{timeStamp}]{text}\n'

        if not api:
            saveLyrics(synced_lyric, plain_lyric, title,
                       albumArtist if albumArtist else artist, album, trackNo, year[0:4] if year else 'NaN')

        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }
