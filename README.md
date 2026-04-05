# File Sorter

A Python CLI tool that automatically organizes files by moving them to designated folders based on file extension rules.

## Features

- **Automatic sorting** - Watches directories for new files and moves them based on rules
- **Rule-based organization** - Configure file extensions and destination folders in `rules.json`
- **Manual cleanup** - Sort existing files in any folder with the `clean` command
- **Duplicate handling** - Automatically renames files if a duplicate exists in the destination
- **Large file detection** - Files >= 5GB are moved to a `largefiles` subfolder
- **Download safety** - Skips incomplete downloads (`.download`, `.crdownload`, `.part`, `.tmp`)
- **Logging** - All actions are logged with timestamps to console and `app.log`
- **Portable** - Run from any directory, paths are relative to script location

---

## Setup

### 1. Install Dependencies

```bash
pip install typer watchdog
```

### 2. Install as Command (Optional)

Run `filesorter` from anywhere on your system:

```bash
mkdir -p ~/.local/bin

cat > ~/.local/bin/filesorter << 'EOF'
#!/bin/zsh
SCRIPT_DIR="/Users/wii/Projects/python/learning/pathlib"
exec python3 "$SCRIPT_DIR/main.py" "$@"
EOF

chmod +x ~/.local/bin/filesorter
```

### 3. Add to PATH

Add to your shell config:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 4. Verify Installation

```bash
filesorter --help
```

---

## Configuration

Edit `rules.json` to define your sorting rules. Use `~` for home directory paths:

```json
{
    "rules": [
        {"ext": ".txt", "dest": "~/Documents"},
        {"ext": ".docx", "dest": "~/Documents"},
        {"ext": ".jpg", "dest": "~/Pictures"},
        {"ext": ".mp3", "dest": "~/Music"},
        {"ext": ".pdf", "dest": "~/Documents"}
    ]
}
```

### Adding Rules via CLI

Add a new rule:
```bash
filesorter rules add --ext ".png" --dest "~/Pictures"
```

Delete a rule:
```bash
filesorter rules delete --ext ".png"
```

---

## Usage

### Start Watcher

Watch current directory:
```bash
filesorter start
```

Watch a specific directory:
```bash
filesorter start --path ~/Downloads
```

### Stop Watcher

```bash
filesorter stop
```

### Manual Cleanup

Sort files in current directory:
```bash
filesorter clean
```

Sort files in a specific folder:
```bash
filesorter clean --folder ~/Downloads
filesorter clean --folder /path/to/folder
```

Use `.` for current working directory (default).

### View Logs

```bash
cat app.log
```

---

## Project Structure

```
.
├── main.py           # Main CLI application
├── rules_engine.py    # Rules management
├── rules.json        # Configuration file
├── app.log           # Log file (created automatically)
├── observer.pid      # PID file (created when running)
└── [folders]/        # Destination folders
```

## Log Levels

| Level | Description |
|-------|-------------|
| INFO | Normal operations (file moves, starts, stops) |
| WARNING | Skipped files (no rule, already moved) |
| ERROR | Failed operations |
| DEBUG | Files already in correct folder |
