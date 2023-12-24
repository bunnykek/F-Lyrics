# F-Lyrics
A Modular Lyrics Fetcher

## Supported services
- Apple Music
- Spotify
- Tidal
- Deezer
- Jiosaavn

`Other services module can be added or made if required`

## Installation
- `git clone https://github.com/bunnykek/F-Lyrics`
- `cd F-Lyrics`
- `pip install -r requirements.txt`
- Open the `config.json` file and fill the tokens.

## How to use
### Terminal
`py flyrics.py URL`    
```
py flyrics.py https://open.spotify.com/track/5jbDih9bLGmI8ycUKkN5XA
```

### API usage
```
from flyrics import Flyrics
lyric = Flyrics()
lyricJson = lyric.fetch("https://open.spotify.com/track/5jbDih9bLGmI8ycUKkN5XA")
print(lyricJson)
```
Response Json ex:
```
[
  {
    'synced': " ",
    'plain': " "
  },
  {
    'synced': " ",
    'plain': " "
  }
]
```

![WindowsTerminal_59swFyULxo](https://github.com/bunnykek/F-Lyrics/assets/67633271/b05c4c33-0f3f-4c11-ae58-46323ba92c9e)


- I will not be responsible for how you use F-Lyrics
