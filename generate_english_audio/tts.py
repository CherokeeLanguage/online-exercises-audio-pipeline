"""
Copied from cherokee-language/audio-lessons-generator-python/tts.py
"""
from __future__ import annotations

import dataclasses
import shutil
import boto3
import hashlib
import os
import re
import textwrap
import unicodedata
from boto3_type_annotations.polly import Client as Polly
from pydub import AudioSegment
from pydub import effects

CACHE_EN = os.path.join("cache", "en")

AMZ_HZ: str = "24000"

IMS_VOICES_MALE: list[str] = ["en-345-m", "en-360-m"]
# IMS_VOICES_FEMALE: list[str] = ["en-294-f", "en-330-f", "en-333-f", "en-361-f"]
IMS_VOICES_FEMALE: list[str] = ["en-333-f", "en-361-f"]
IMS_VOICES: list[str] = list()
IMS_VOICES.extend(IMS_VOICES_FEMALE)
IMS_VOICES.extend(IMS_VOICES_MALE)
IMS_VOICES.sort()

AMZ_VOICES_MALE: list[str] = ["Joey"]
# AMZ_VOICES_FEMALE: list[str] = ["Joanna", "Kendra", "Kimberly", "Salli"]
AMZ_VOICES_FEMALE: list[str] = ["Kendra"]
AMZ_VOICES: list[str] = list()
AMZ_VOICES.extend(AMZ_VOICES_FEMALE)
AMZ_VOICES.extend(AMZ_VOICES_MALE)


@dataclasses.dataclass
class TTSBatchEntry:
    voice: str | None = None
    text: str = ""


def tts_en(voice: str, text_en: str):
    mp3_en = get_mp3_en(voice, text_en)
    if os.path.exists(mp3_en):
        return
    polly_client: Polly = boto3.Session().client("polly")
    response = polly_client.synthesize_speech(
        OutputFormat="mp3",  #
        Text=text_en,  #
        VoiceId=voice,  #
        SampleRate=AMZ_HZ,  #
        LanguageCode="en-US",  #
        Engine="neural",
    )
    with open(mp3_en + ".tmp", "wb") as w:
        w.write(response["AudioStream"].read())
    shutil.move(mp3_en + ".tmp", mp3_en)


def get_mp3_en(voice: str, text_en: str) -> str:
    text_en = re.sub("\\s+", " ", text_en).strip()
    mp3_name_en: str = get_filename(voice, text_en)
    mp3_en: str = os.path.join(CACHE_EN, mp3_name_en)
    return mp3_en


def en_audio(voice: str, text_en: str) -> AudioSegment:
    tts_en(voice, text_en)
    mp3_file = get_mp3_en(voice, text_en)
    return effects.normalize(AudioSegment.from_file(mp3_file))


def get_filename(voice: str, text: str, alpha: float | None = None):
    text = re.sub("\\s+", " ", textwrap.dedent(text)).strip()
    text = text.lower()
    if not voice:
        voice = "-"
    if alpha and alpha != 1.0:
        if voice == "-":
            voice = f"a{alpha:.2f}"
        else:
            voice = f"{voice}_a{alpha:.2f}"
    sha1: str
    sha1 = hashlib.sha1(text.encode("UTF-8")).hexdigest()
    _ = unicodedata.normalize("NFD", text).replace(" ", "_")
    _ = unicodedata.normalize("NFC", re.sub("[^a-z_]", "", _))
    if len(_) > 32:
        _ = _[:32]
    filename: str = f"{_}_{voice}_{sha1}.mp3"
    return filename
