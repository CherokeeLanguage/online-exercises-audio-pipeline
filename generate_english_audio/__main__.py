from sys import argv

from .generate_english_audio_for_deck import main as generate_english_main

PROGRAMS = {"generate-english-audio": generate_english_main}

if __name__ == "__main__":
    prog = argv[1]
    PROGRAMS[prog]()
