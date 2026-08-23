from dataclasses import dataclass
from pathlib import Path


def audio_url(filename: str) -> str:
    return f"https://cherokeenationdictionary.net/Audio/{filename}"


@dataclass
class Sentence:
    """
    Sentence info from CND CSV
    """

    english: str
    syllabary: str
    phonetic: str
    audio: str
    id: str

    @property
    def audio_url(self) -> str:
        return audio_url(self.audio)

    @property
    def audio_path(self) -> Path:
        return Path("data/cnd/card_audio") / self.audio
