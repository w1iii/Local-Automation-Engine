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
    dest = cwd / f"{rules.find_destination(file)}/"
    # pathfile = rules.find_destination(file)
    dest.mkdir(parents=True, exist_ok=True)

    target_file = dest / filename
    path = f"./{rules.find_destination(file)}"
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


# Start observing file cli


@app.command(name="start")
def start_obs():
    print("start")
    # Save current PID to file
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
