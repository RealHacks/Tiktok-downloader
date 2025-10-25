#!/usr/bin/env python3
"""
TikTok Account Downloader (Auto Setup, Clean Output)
----------------------------------------------------
✅ Downloads all TikTok videos from any public account.
✅ Works in Termux, Pydroid3, or Desktop.
✅ Automatically installs missing dependencies.
✅ Saves videos to /storage/emulated/0/TecHelp/
✅ Clean progress bar (no warnings)
"""

import os, sys, subprocess, importlib
from typing import List, Optional

# --- Auto-install dependencies ---
REQUIRED = ["yt_dlp", "tqdm"]
for pkg in REQUIRED:
    try:
        importlib.import_module(pkg)
    except ImportError:
        print(f"📦 Installing missing dependency: {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", pkg])

from yt_dlp import YoutubeDL, DownloadError
from tqdm import tqdm

# ---------- Defaults ----------
DEFAULT_OUT_DIR = "/storage/emulated/0/TecHelp"
os.makedirs(DEFAULT_OUT_DIR, exist_ok=True)


# ---------- Helper to get video URLs ----------
def get_tiktok_videos(username: str) -> List[str]:
    username = username.lstrip("@")
    playlist_url = f"https://www.tiktok.com/@{username}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
    except Exception as e:
        print(f"⚠️ Failed to fetch video list for @{username}: {e}")
        return []

    entries = info.get("entries") if isinstance(info, dict) else None
    if not entries:
        vid = info.get("id") if isinstance(info, dict) else None
        if vid:
            return [f"https://www.tiktok.com/@{username}/video/{vid}"]
        return []

    urls: List[str] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        vid_id = e.get("id") or e.get("url") or e.get("webpage_url")
        if not vid_id:
            continue
        if vid_id.startswith("http"):
            urls.append(vid_id)
        else:
            urls.append(f"https://www.tiktok.com/@{username}/video/{vid_id}")

    return urls


# ---------- Download Function ----------
def download_user_videos(username: str, count: Optional[int] = None,
                         out_base: str = DEFAULT_OUT_DIR,
                         ydl_extra_opts: Optional[dict] = None):
    username = username.lstrip("@")
    out_dir = os.path.join(out_base, username)
    os.makedirs(out_dir, exist_ok=True)

    urls = get_tiktok_videos(username)
    if not urls:
        print("⚠️ No videos found (or failed to fetch).")
        return

    total_videos = len(urls)
    print(f"\n✅ Found {total_videos} videos for @{username}.")

    if count is None:
        while True:
            try:
                raw = input(f"How many videos to download (1–{total_videos}) [default {total_videos}]: ").strip()
                if raw == "":
                    n = total_videos
                else:
                    n = int(raw)
                n = max(1, min(n, total_videos))
                break
            except ValueError:
                print("Please enter a valid number.")
    else:
        n = max(1, min(count, total_videos))

    to_download = urls[:n]
    print(f"\n▶ Starting download of {n} video(s) into:\n   {out_dir}\n")

    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(upload_date)s_%(id)s.%(ext)s"),
        "format": "best",
        "quiet": True,
        "ignoreerrors": True,
        "no_warnings": True,
        "progress": True,
        "noprogress": False,
        "progress_with_newline": True,
        "progress_template": "Downloading %(info.id)s: %(progress._percent_str)s |%(progress.bar)s| %(progress._eta_str)s",
        "concurrent_fragment_downloads": 4,
        "writeinfojson": False,
        "writesubtitles": False,
        "merge_output_format": "mp4",
    }

    if ydl_extra_opts:
        ydl_opts.update(ydl_extra_opts)

    with YoutubeDL(ydl_opts) as ydl:
        for url in tqdm(to_download, desc=f"Downloading @{username}", unit="video"):
            try:
                ydl.download([url])
            except DownloadError:
                continue
            except Exception:
                continue

    print(f"\n✅ Done! Videos saved in: {out_dir}")

    # Try to open folder automatically (Android)
    if os.path.exists("/data/data/com.termux/files/usr/bin/am"):
        os.system(f'am start -a android.intent.action.VIEW -d "file://{out_dir}"')


# ---------- Menu ----------
def main_menu():
    usernames: List[str] = []

    while True:
        print("\n========== TikTok Downloader ==========\n")
        print(f"Output folder : {DEFAULT_OUT_DIR}")
        print(f"Usernames     : {', '.join(usernames) if usernames else '(none)'}")
        print("\nMenu:")
        print("  1) Add username")
        print("  2) Remove username")
        print("  3) Start download")
        print("  4) Clear usernames")
        print("  0) Exit\n")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            u = input("Enter TikTok username (no @): ").strip().lstrip("@")
            if u:
                usernames.append(u)
                print(f"✅ Added: {u}")
        elif choice == "2":
            if not usernames:
                print("No usernames to remove.")
                continue
            for i, u in enumerate(usernames, start=1):
                print(f"  {i}) {u}")
            idx = input("Enter number to remove: ").strip()
            if idx.isdigit():
                i = int(idx) - 1
                if 0 <= i < len(usernames):
                    removed = usernames.pop(i)
                    print(f"🗑 Removed: {removed}")
                else:
                    print("Invalid number.")
            else:
                print("Cancelled.")
        elif choice == "3":
            if not usernames:
                print("⚠️ Add at least one username first.")
                continue
            for user in list(usernames):
                download_user_videos(user)
        elif choice == "4":
            usernames.clear()
            print("🧹 Cleared usernames.")
        elif choice == "0":
            print("👋 Exiting.")
            break
        else:
            print("Invalid option. Enter 0–4.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)
