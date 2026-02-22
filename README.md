# bear-tools

CLI tool for [Bear.app](https://bear.app/) notes on macOS. Direct SQLite reads + x-callback-url writes.

## Requirements

- macOS with Bear.app installed
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv tool install -e .
```

## Usage

```bash
bear stats                        # note counts, tags, orphans, duplicates
bear search "python"              # search by title or content
bear search "python" -o json      # JSON output for scripts/LLMs
bear summary                      # notes modified today
bear summary -p week              # notes modified this week
bear orphaned                     # notes with no tags
bear duplicates                   # duplicate titles
bear dedup                        # interactive duplicate cleanup
bear dedup -y                     # auto-remove all content duplicates
bear journal                      # create/open daily journal note
bear create "Title" --text "body" # create a new note
```

## How it works

- Reads: queries Bear's SQLite database directly (read-only)
- Writes: uses Bear's x-callback-url scheme via open command (preserves iCloud sync)