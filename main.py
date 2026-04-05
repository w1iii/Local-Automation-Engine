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

cwd = Path(".")
downloads = cwd / "downloads/"

rules = Rules()
app = typer.Typer()
app.add_typer(rules_app, name="rules")
observer = Observer()
rules.load_rules()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        print("Created: ", event.src_path)
        file = event.src_path
        move_file(file)

    def on_deleted(self, event):
        print("Deleted: ", event.src_path)

    def on_moved(self, event):
        print("Moved: ", event.src_path)


def move_file(file):
    filename = Path(file).name
    destination = rules.find_destination(file)
    if not destination:
        print(f"No rule for {filename}, skipping")
        return
    dest = cwd / f"{destination}/"
    dest.mkdir(parents=True, exist_ok=True)

    target_file = dest / filename
    path = f"./{destination}"
    if not rules.filesize(file):
        target_file = dest / "largefiles/" / filename
        Path(f"{path}/largefiles").mkdir(exist_ok=True)
    # print(target_file)
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
        print("file already exists, renaming to", target_file.name)
    shutil.move(file, target_file)
    # rules.filesize(target_file, pathfile)


def check_folder(folder):
    files_to_move = []
    for item in folder.iterdir():
        if item.is_file():
            dest = rules.find_destination(str(item))
            if dest:
                expected_dest = cwd / dest
                if item.parent.resolve() == expected_dest.resolve():
                    pass
                    # print(f"Already in correct folder: {item.name}")
                else:
                    files_to_move.append(item)
                    print(f"Needs moving: {item.name} -> {dest}")
    if len(files_to_move) <= 0:
        print("No files to move")
    return files_to_move


@app.command(name="clean")
def clean_folder(folder: str = typer.Option(..., help="folder")):
    base_dir = Path.cwd()
    target_folder = base_dir / folder

    files_to_move = check_folder(target_folder)
    print(f"Files to move: {len(files_to_move)}")

    if len(files_to_move) < 1:
        return

    for file in files_to_move:
        try:
            move_file(str(file))
            print(f"Moved: {file.name}")
        except FileNotFoundError:
            print(f"Already moved or missing: {file.name}")


@app.command(name="start")
def start_obs():
    print("start")
    with open("observer.pid", "w") as f:
        pid = os.getpid()
        f.write(str(pid))
    print(pid)

    observer.schedule(Handler(), str(cwd), recursive=False)
    observer.schedule(Handler(), str(downloads), recursive=True)
    observer.start()

    try:
        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    finally:
        if os.path.exists("observer.pid"):
            os.remove("observer.pid")


@app.command(name="stop")
def stop_obs():
    try:
        with open("observer.pid", "r") as f:
            pid = int(f.read().strip())
        print(f"Sending SIGINT to observer with PID {pid} ...")
        os.kill(pid, signal.SIGINT)
        os.remove("observer.pid")
        print("Observer process stopped.")
    except FileNotFoundError:
        print("PID file not found. Is the observer running?")
    except ProcessLookupError:
        print("Process not found (already stopped?)")
    except Exception as e:
        print(f"Error stopping observer: {e}")


if __name__ == "__main__":
    app()
