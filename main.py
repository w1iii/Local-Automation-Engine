import logging
import shutil
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

cwd = Path(".")


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
    if file.endswith(".txt"):
        dest = cwd / "documents/"
    elif file.endswith(".jpg"):
        dest = cwd / "photos/"
    elif file.endswith(".mp3"):
        dest = cwd / "music/"
    else:
        return

    if not dest.exists():
        Path.mkdir(dest)

    target_file = dest / filename
    print(target_file)
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


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
observer = Observer()
observer.schedule(Handler(), cwd, recursive=True)
print("Watching over: ", cwd)
observer.start()

try:
    while observer.is_alive():
        time.sleep(1)
        observer.join(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
