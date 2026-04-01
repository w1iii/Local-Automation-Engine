import logging
import shutil
import time
from pathlib import Path

from rules_engine import Rules
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

cwd = Path(".")
downloads = cwd / "downloads/"

rules = Rules()
rules.load_rules()


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


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
observer = Observer()
observer.schedule(Handler(), cwd, recursive=False)
observer.schedule(Handler(), downloads, recursive=True)
observer.start()

try:
    while observer.is_alive():
        time.sleep(1)
        observer.join(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
