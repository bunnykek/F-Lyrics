from abc import ABC, abstractmethod


class Module(ABC):
    @abstractmethod
    def __init__(self, url: str, config: dict, api: bool) -> None:
        pass

    @abstractmethod
    def getAlbumLyrics(self, albumid: str, data: dict, config: dict, api: bool) -> None:
        pass

    @abstractmethod
    def getTrackLyrics(self, trackid: str, data: dict, config: dict, api: bool) -> None:
        pass

    @abstractmethod
    def getResponse(self) -> dict:
        pass
