# Online exercises audio pipeline

This repository contains python modules to process WAV audio from first language speakers into individual terms for use on the [CherokeeLanguage/online-exercises](https://github.com/CherokeeLanguage/online-exercises) site.

## High level approach

1. Create a new folder in [data/](data/) for each dataset
1. Annotate WAV files from first-language speakers with [ELAN](https://archive.mpi.nl/tla/elan/download)
   - Use shorthand phonetics with no tone
1. Export annotations as TSV
1. Provide a CSV file with rich (tonal) phonetics, syllabary, and English (terms CSV)
   - Should have columns: `NEEDS_FIXING, VOCAB_SET, ENGLISH, CHEROKEE, SYLLABARY, AUDIO`
   - `NEEDS_FIXING` and `AUDIO` can be blank to start
1. Write a `dataset.json` file that says where to find each of the above (see [common/structs.py](/common/structs.py) and [data/jw-living-phrases/dataset.json](data/jw-living-phrases/dataset.json))
1. Run the following to interactively match an annotated segment to each row in the terms CSV.
   ```
   python -m match_audio data/<your-data-set>
   ```
1. Generate English audio with TTS if needed
1. Copy audio and JSON files into online-exercises repository

## Setup

If you also have a copy of CherokeeLanguage/audio-lessons-generator-python they can share a symlinked cache folder.

## TODOS

### English audio generation (`generate_english_audio` module) needs testing and a brush up for new code structure

Currently, English audio generation expects files to be in slightly different places as it was mostly just picked up from where it lived unmerged on [CherokeeLanguage/audio-lessons-generator-python](https://github.com/CherokeeLanguage/audio-lessons-generator-python).

### `create_cards` is a bit fragile

The current implementation expects a file with English followed by Cherokee for every term. We could relax this to just Cherokee annotations, pull the English from the CSV, and then generate the English text with the other module.
