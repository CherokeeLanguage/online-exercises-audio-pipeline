from dataclasses import asdict
from json import load, dump
import os
from sys import argv
import shutil

from tts import AMZ_VOICES, get_mp3_en, tts_en

from ..common.structs import OnlineExercisesCard


def get_app_filename(filename: str):
    # change cache/en/foo.wav --> source/en/foo.wav
    return filename.replace("cache/", "source/", 1)


def get_cache_filename_from_app_filename(app_filename: str):
    # change source/en/foo.wav --> cache/en/foo.wav
    return app_filename.replace("source/", "cache/", 1)


def generate_audio_for_voice(voice: str, text: str) -> str:
    """
    Create English audio mp3 and return path.
    """
    tts_en(voice, text)
    cache_file = get_mp3_en(voice, text)
    return get_app_filename(cache_file)


def generate_english_audio(card: OnlineExercisesCard) -> OnlineExercisesCard:
    return OnlineExercisesCard(
        cherokee=card.cherokee,
        cherokee_audio=card.cherokee_audio,
        syllabary=card.syllabary,
        alternate_pronunciations=card.alternate_pronunciations,
        alternate_syllabary=card.alternate_syllabary,
        english=card.english,
        english_audio=[
            generate_audio_for_voice(voice, card.english) for voice in AMZ_VOICES
        ],
    )


def main():
    deck_src = argv[2]
    deck_out = argv[3]
    audio_out = argv[4]

    with open(deck_src) as f:
        json_deck = load(f)
        deck = [OnlineExercisesCard(**card) for card in json_deck]

    deck_with_audio = [generate_english_audio(card) for card in deck]
    with open(deck_out, "w") as f:
        dump(
            [asdict(card) for card in deck_with_audio],
            f,
            ensure_ascii=False,
            sort_keys=True,
        )

    for card in deck_with_audio:
        for appfile in card.english_audio:
            shutil.copy(
                get_cache_filename_from_app_filename(appfile),
                os.path.join(audio_out, appfile),
            )
