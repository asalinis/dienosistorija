#!/usr/bin/env python3
"""Imports today's story from the public Google Drive folder into the repo.

The morning scheduled task writes <YYYY-MM-DD>.json into the Drive folder
(DRIVE_FOLDER_ID). The folder is shared "anyone with the link", so no
credentials are needed. Images are listed by their Wikimedia Commons file
names and downloaded here.

Usage:
  import_story.py            import today's story (Europe/Vilnius) if missing
  import_story.py --list     only list the folder and test downloading (diagnostics)

Writes "imported=<date>" to $GITHUB_OUTPUT when a story was added.
"""
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

FOLDER = os.environ.get("DRIVE_FOLDER_ID", "")
UA = "DienosIstorija/1.0 (edgaras@tamo.lt)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["date", "title", "category", "hook", "emailSummary", "body", "takeaways", "sources", "images"]


def get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as err:  # noqa: BLE001
            last = err
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def list_folder():
    page = get(f"https://drive.google.com/embeddedfolderview?id={FOLDER}#list").decode("utf-8", "replace")
    files = {}
    for m in re.finditer(r'id="entry-([A-Za-z0-9_-]+)".*?class="flip-entry-title">(.*?)</div>', page, re.S):
        files[html.unescape(m.group(2)).strip()] = m.group(1)
    return files


def download(file_id):
    return get(f"https://drive.google.com/uc?export=download&id={file_id}")


def write_output(key, value):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")


def fetch_image(commons_name, dest):
    from PIL import Image
    name = commons_name.removeprefix("File:").replace(" ", "_")
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=960"
    im = Image.open(io.BytesIO(get(url))).convert("RGB")
    if im.width > 960:
        im = im.resize((960, round(im.height * 960 / im.width)), Image.LANCZOS)
    im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    if not FOLDER:
        sys.exit("DRIVE_FOLDER_ID is not set")
    if "--list" in sys.argv:
        files = list_folder()
        if not files:
            sys.exit("Drive folder is empty or not shared publicly ('Anyone with the link').")
        print("Folder contents:", files)
        for name, fid in files.items():
            print(name, "->", download(fid)[:120])
        return
    now = datetime.now(ZoneInfo("Europe/Vilnius"))
    today = now.strftime("%Y-%m-%d")
    target = os.path.join(ROOT, "data", "stories", f"{today}.json")
    if os.path.exists(target):
        print(f"{today}: already published.")
        return
    # Scheduled runs only report a failure once, on the last check of the morning.
    strict = os.environ.get("GITHUB_EVENT_NAME") != "schedule" or (now.hour, now.minute) >= (8, 45)
    try:
        files = list_folder()
    except RuntimeError as err:
        msg = f"Cannot read the Drive folder (is it shared 'Anyone with the link'?): {err}"
        if strict:
            sys.exit(msg)
        print("Warning:", msg)
        return
    if f"{today}.json" not in files:
        msg = f"{today}: story not in Drive. Folder has: {sorted(files)}"
        if strict:
            sys.exit(msg)
        print(msg)
        return
    story = json.loads(download(files[f"{today}.json"]).decode("utf-8"))
    missing = [k for k in REQUIRED if k not in story]
    if missing:
        sys.exit(f"Story is missing fields: {missing}")
    if story["date"] != today:
        sys.exit(f"Story date {story['date']} does not match {today}")
    images = story.pop("images")
    for n, img in enumerate(images, 1):
        commons = img["file"] if isinstance(img, dict) else img
        dest = os.path.join(ROOT, "img", f"{today}-{n}.jpg")
        fetch_image(commons, dest)
        print("image", n, commons)
    story["imageSources"] = images
    refs = re.findall(r'src="(/img/[^"]+)"', story["body"])
    absent = [r for r in refs if not os.path.exists(ROOT + r)]
    if absent:
        sys.exit(f"Body references missing images: {absent}")
    story.setdefault("readMin", max(1, round(len(re.sub("<[^>]+>", " ", story["body"]).split()) / 170)))
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(story, fh, ensure_ascii=False, indent=1)
    print(f"Imported {today}: {story['title']}")
    write_output("imported", today)


if __name__ == "__main__":
    main()
