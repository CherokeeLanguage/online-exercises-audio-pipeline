import os
from pathlib import Path
import shutil
from common.structs import DatasetMetadata

from .tts import AMZ_VOICES, get_mp3_en, tts_en

from common.online_exercises_structs import (
    OnlineExercisesCard,
    read_cards_for_dataset,
    write_cards_json_for_dataset,
)


def get_app_filename(dataset: DatasetMetadata, cache_filename: str) -> str:
    return str(dataset.audio_output_dir / Path(cache_filename).name)


def get_cache_filename_from_app_filename(app_filename: str):
    # change source/en/foo.wav --> cache/en/foo.wav
    return f"cache/en/{Path(app_filename).name}"


def generate_audio_for_voice(voice: str, text: str) -> str:
    """
    Create English audio mp3 and return path to cached mp3.
    """
    tts_en(voice, text)
    return get_mp3_en(voice, text)


def generate_english_audio(
    dataset: DatasetMetadata, card: OnlineExercisesCard
) -> OnlineExercisesCard:
    cached_audio = [
        generate_audio_for_voice(voice, card.english) for voice in AMZ_VOICES
    ]
    return OnlineExercisesCard(
        cherokee=card.cherokee,
        cherokee_audio=card.cherokee_audio,
        syllabary=card.syllabary,
        alternate_pronunciations=card.alternate_pronunciations,
        alternate_syllabary=card.alternate_syllabary,
        english=card.english,
        english_audio=[
            get_app_filename(dataset, cache_filename) for cache_filename in cached_audio
        ],
        phoneticOrthography=card.phoneticOrthography,
    )


def main(dataset: DatasetMetadata):
    cards = read_cards_for_dataset(dataset)
    cards_with_english = [generate_english_audio(dataset, card) for card in cards]
    write_cards_json_for_dataset(dataset, cards_with_english)

    for card in cards_with_english:
        for appfile in card.english_audio:
            shutil.copy(
                get_cache_filename_from_app_filename(appfile),
                appfile,
            )
