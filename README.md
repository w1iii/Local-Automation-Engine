# File Sorter

A Python CLI tool that automatically organizes files by moving them to designated folders based on file extension rules.

## Features

- **Automatic sorting** - Watches directories for new files and moves them based on rules
- **Rule-based organization** - Configure file extensions and destination folders in `rules.json`
- **Manual cleanup** - Sort existing files in any folder with the `clean` command
- **Duplicate handling** - Automatically renames files if a duplicate exists in the destination
- **Large file detection** - Files >= 5GB are moved to a `largefiles` subfolder
- **Logging** - All actions are logged with timestamps to console and `app.log`

## Installation

```bash
pip install typer watchdog
```

## Configuration

Edit `rules.json` to define your sorting rules:

```json
{
    "rules": [
        {"ext": ".txt", "dest": "documents"},
        {"ext": ".jpg", "dest": "photos"},
        {"ext": ".mp3", "dest": "music"},
        {"ext": ".pdf", "dest": "pdf"}
    ]
}
```

## Usage

### Manage Rules

Add a new rule:
```bash
python3 main.py rules add --ext ".png" --dest "images"
```

Delete a rule:
```bash
python3 main.py rules delete --ext ".png"
```

### Start/Stop Watcher

Start watching for new files:
```bash
python3 main.py start
```

Stop the watcher:
```bash
python3 main.py stop
```

### Manual Cleanup

Sort files in a specific folder:
```bash
python3 main.py clean --folder downloads
```

### View Logs

All actions are logged to `app.log`:
```bash
cat app.log
```

## Project Structure

```
.
├── main.py           # Main CLI application
├── rules_engine.py   # Rules management
├── rules.json        # Configuration file
├── app.log           # Log file (created automatically)
└── [folders]/        # Destination folders for sorted files
```

## Log Levels

| Level | Description |
|-------|-------------|
| INFO | Normal operations (file moves, starts, stops) |
| WARNING | Skipped files (no rule, already moved) |
| ERROR | Failed operations |
| DEBUG | Files already in correct folder |
