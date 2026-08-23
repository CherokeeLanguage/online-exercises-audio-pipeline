---
id: TASK-1
title: >-
  Commit code and json, ignore audio, verify sentence download script, commit
  per data dir
status: In Progress
assignee:
  - '@agent'
created_date: '2026-08-23 19:55'
updated_date: '2026-08-23 19:55'
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
- [ ] #1 Audio files git ignored
- [ ] #2 Code and json committed
- [ ] #3 Download sentence audio script checked
- [ ] #4 One commit per data directory
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect git status and existing files.\n2. Check for script to download sentences and answer user inquiry.\n3. Configure .gitignore for audio files.\n4. Commit code and json files, and create separate commits per data directory.
<!-- SECTION:PLAN:END -->
