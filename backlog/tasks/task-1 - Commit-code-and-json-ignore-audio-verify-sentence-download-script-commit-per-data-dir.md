---
id: TASK-1
title: >-
  Commit code and json, ignore audio, verify sentence download script, commit
  per data dir
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 19:55'
updated_date: '2026-08-23 19:56'
labels: []
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Get code and json committed and audio git ignored. Check for script to download all sentences around. Make one commit per data directory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Audio files git ignored
- [x] #2 Code and json committed
- [x] #3 Download sentence audio script checked
- [x] #4 One commit per data directory
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect git status and existing files.\n2. Check for script to download sentences and answer user inquiry.\n3. Configure .gitignore for audio files.\n4. Commit code and json files, and create separate commits per data directory.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured .gitignore for all audio formats (.wav, .mp3, .flac, .m4a, card_audio, split_audio, wav_output, etc.). Confirmed presence of sentence audio downloader script in cnd/__main__.py / cnd/file_downloader.py. Committed code and JSON files followed by individual commits for each data directory (data/cnd, data/john-1, data/jw-animals, data/stories-told-by-cherokees, data/wj-giants).
<!-- SECTION:FINAL_SUMMARY:END -->
