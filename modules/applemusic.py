# made by @bunnykek

import requests
import bs4
import re
from sanitize_filename import sanitize
from modules.module import Module
from utility import Utility


class AppleMusic(Module):
    NAME = "Apple Music"
    REGEX = re.compile(
        r"https://music.apple.com/(\w{2})/(album|song)/.+?/(\d+)(\?i=(\d+))?")

    def __init__(self, url: str, config: dict, api: bool) -> None:
        self.headers = {
            "authorization": config['applemusic']['auth_bearer'],
            "media-user-token": config['applemusic']['media-user-token'],
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
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        region, kind, albumid, trackFlag, trackid = AppleMusic.REGEX.search(
            url).groups()

        data = {
            'region': region,
            'albumid': albumid,
            'trackFlag': trackFlag,
            'trackid': trackid
        }

        if trackFlag:
            self.jsonResponse = [self.getTrackLyrics(trackid, data, config, api)]

        elif kind == 'song':
            self.jsonResponse = [self.getTrackLyrics(albumid, data, config, api)]

        else:
            self.jsonResponse = self.getAlbumLyrics(albumid, data, config, api)

    def getResponse(self) -> None:
        return self.jsonResponse

    def getAlbumLyrics(self, albumid: str, data: dict, config: dict, api: bool) -> None:
        print("Getting lyrics for the whole album...")
        metadata = self.session.get(
            f"https://api.music.apple.com/v1/catalog/{data["region"]}/albums/{albumid}").json()
        metadata = metadata['data'][0]
        data["albumArtist"] = metadata['attributes']['artistName']

        lyricsJson = list()
        for track in metadata['relationships']['tracks']['data']:
            trackJson = self.getTrackLyrics(track['id'], data, config, api)
            lyricsJson.append(trackJson)

        return lyricsJson

    def getTrackLyrics(self, trackid: str, data: dict, config: dict, api: bool) -> None:
        metadata = self.session.get(
            f"https://api.music.apple.com/v1/catalog/{data["region"]}/songs/{trackid}").json()
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
            f'https://amp-api.music.apple.com/v1/catalog/{data["region"]}/songs/{trackid}/lyrics')
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
                if begin.count(':') > 1:
                    timeStamp = ':'.join(begin.split(':')[1:])
                else:
                    timeStamp = self.__convertTimeSec(
                        begin) if 's' in begin else self.__convertTimeFormat(begin)
                text = paragraph.text
                plain_lyric += text+'\n'
                synced_lyric += f'[{timeStamp}]{text}\n'

        if not api:
            Utility.saveLyrics(synced_lyric, plain_lyric, title, data.get(
                "albumArtist", artist), album, trackNo, year[0:4] if year else 'NaN')

        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }

    def __convertTimeSec(self, original_time):
        # Extract the seconds from the original time
        seconds = float(original_time.split('s')[0])

        # Convert seconds to minutes and remaining seconds
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60

        # Format minutes and remaining seconds into two-digit strings
        formatted_minutes = "{:02d}".format(minutes)
        formatted_seconds = "{:02.3f}".format(remaining_seconds)

        # Combine the formatted components into the desired format
        formatted_time = "{}:{}".format(
            formatted_minutes, formatted_seconds[:5])

        return formatted_time

    def __convertTimeFormat(self, original_time):
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
