# made by @bunnykek

import re 
import json
import requests
from sanitize_filename import sanitize
from utility import saveLyrics

NAME = "Jiosaavn"
REGEX = re.compile(r"https://www\.jiosaavn\.com/(album|song)/.+?/(.+)")
CLEANR = re.compile('<.*?>') 


class Lyrics:
    def __init__(self, url, api = False):
        self.session = requests.session()
        kind, id_ = REGEX.search(url).groups()
        
        if kind == 'song':
            self.jsonResponse = [self.getTrackLyrics(id_, api)]
        
        else:
            self.jsonResponse = self.getAlbumLyrics(id_, api)
    
    def cleanhtml(self, raw_html):
        cleantext = re.sub(CLEANR, '', raw_html)
        return cleantext
    
    def getAlbumLyrics(self, albumid, api):

        response = self.session.get(f'https://www.jiosaavn.com/api.php?__call=webapi.get&token={albumid}&type=album&_format=json')
        metadata = response.json()
        album_artist = metadata['primary_artists']
        lyricsJson = list()
        for i, track in enumerate(metadata['songs']):
            trackid = REGEX.search(track['perma_url']).group(2)
            trackJson = self.getTrackLyrics(trackid, api, i+1, album_artist, track)
            lyricsJson.append(trackJson)
        
        return lyricsJson

    def getTrackLyrics(self, trackid, api, trackNo=1, artist=None, trackjson=None):
        if not trackjson:
            trackjson = self.session.get(f"https://www.jiosaavn.com/api.php?__call=webapi.get&token={trackid}&type=song&_format=json").json()
            trackjson = trackjson[f"{list(trackjson.keys())[0]}"]
            artist = sanitize(trackjson['primary_artists'])
        
        year = trackjson['year']
        title = sanitize(trackjson['song'])
        album = sanitize(trackjson['album'])
            

        lyric_response = self.session.get("https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id=" + trackjson['id']).json()
        # print(lyric_response)
        try:
            lyrics =  lyric_response.get("lyrics")
            if lyrics is not None:
                lyrics = lyrics.replace('<br>', '\n')
                lyrics = self.cleanhtml(lyrics)
            # print(lyric_response)

            plain_lyric = f"Title: {title}\nAlbum: {album}\nArtist: {artist}\n\n"
            synced_lyric = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"
            
            plain_lyric+=lyrics
        except: pass

        if not api:
            saveLyrics(synced_lyric, plain_lyric, title, artist, album, trackNo, year)
        
        return {
            'synced': synced_lyric,
            'plain': plain_lyric
        }