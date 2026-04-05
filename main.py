import logging
import os
import shutil
import signal
import time
from pathlib import Path

import typer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from rules_engine import Rules
from rules_engine import app as rules_app

SCRIPT_DIR = Path(__file__).parent.resolve()
cwd = SCRIPT_DIR
downloads = Path.home() / "Downloads"

EXCLUDE_PATTERNS = [
    ".download",
    ".crdownload",
    ".part",
    ".partial",
    ".tmp",
    "observer.pid",
]

rules = Rules()
app = typer.Typer()
app.add_typer(rules_app, name="rules")
observer = Observer()
rules.load_rules()

LOG_FILE = SCRIPT_DIR / "app.log"

logger = logging.getLogger("file_sorter")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter(
    "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_format)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        time.sleep(2)
        file = event.src_path

        for pattern in EXCLUDE_PATTERNS:
            if pattern in file:
                return

        logger.info(f"File detected: {event.src_path}")
        move_file(file)

    def on_deleted(self, event):
        logger.info(f"File deleted: {event.src_path}")

    def on_moved(self, event):
        logger.info(f"File moved: {event.src_path}")


def move_file(file):
    filename = Path(file).name
    destination = rules.find_destination(file)
    if not destination:
        logger.warning(f"No rule for {filename}, skipping")
        return
    dest = rules.resolve_destination(destination)
    dest.mkdir(parents=True, exist_ok=True)

    target_file = dest / filename
    if not rules.filesize(file):
        target_file = dest / "largefiles" / filename
        (dest / "largefiles").mkdir(exist_ok=True)
    if target_file.exists():
        count = 0
        newfilename = target_file.stem
        try:
            count = int(target_file.stem[-1])
            newfilename = target_file.stem[:-1]
        except ValueError:
            pass
        while target_file.exists():
            new_name = f"{newfilename}{count}{target_file.suffix}"
            target_file = target_file.parent / new_name
            count += 1
        logger.info(f"File exists, renamed to: {target_file.name}")
    shutil.move(file, target_file)
    logger.info(f"Moved: {filename} -> {destination}/{target_file.name}")


def check_folder(folder):
    files_to_move = []
    for item in folder.iterdir():
        if item.is_file():
            dest = rules.find_destination(str(item))
            if dest:
                expected_dest = rules.resolve_destination(dest)
                if item.parent.resolve() == expected_dest.resolve():
                    logger.debug(f"Already in correct folder: {item.name}")
                else:
                    files_to_move.append(item)
                    logger.info(f"Needs moving: {item.name} -> {dest}")
    if len(files_to_move) <= 0:
        logger.info("No files to move")
    return files_to_move


@app.command(name="clean")
def clean_folder(
    folder: str = typer.Option(".", help="folder (use '.' for current directory)"),
):
    if folder == ".":
        target_folder = Path.cwd()
    else:
        target_folder = Path(folder).expanduser().resolve()
    print(target_folder)

    files_to_move = check_folder(target_folder)
    logger.info(f"Files to move: {len(files_to_move)}")

    if len(files_to_move) < 1:
        return

    for file in files_to_move:
        try:
            move_file(str(file))
        except FileNotFoundError:
            logger.warning(f"Already moved or missing: {file.name}")


@app.command(name="start")
def start_obs(
    path: str = typer.Option(".", help="path to watch (use '.' for current directory)"),
):
    watch_path = Path(path).expanduser().resolve() if path != "." else Path.cwd()
    logger.info(f"Starting file watcher on: {watch_path}")
    with open(SCRIPT_DIR / "observer.pid", "w") as f:
        pid = os.getpid()
        f.write(str(pid))
    logger.info(f"Watcher started with PID: {pid}")

    observer.schedule(Handler(), str(watch_path), recursive=True)
    observer.start()

    try:
        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    finally:
        if (SCRIPT_DIR / "observer.pid").exists():
            (SCRIPT_DIR / "observer.pid").unlink()
        logger.info("Watcher stopped")


@app.command(name="stop")
def stop_obs():
    pid_file = SCRIPT_DIR / "observer.pid"
    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        logger.info(f"Stopping watcher with PID: {pid}...")
        os.kill(pid, signal.SIGINT)
        pid_file.unlink()
        logger.info("Watcher stopped successfully")
    except FileNotFoundError:
        logger.error("PID file not found. Is the watcher running?")
    except ProcessLookupError:
        logger.error("Process not found (already stopped?)")
    except Exception as e:
        logger.error(f"Error stopping watcher: {e}")


if __name__ == "__main__":
    app()
