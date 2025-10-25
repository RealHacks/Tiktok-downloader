#!/usr/bin/env python3  
"""  
Universal Video & Audio Downloader (Auto Setup)  
-----------------------------------------------  
✅ Downloads from TikTok, YouTube, Instagram, etc.  
✅ Supports MP4 (video) and MP3 (audio only)  
✅ Works in Termux, Pydroid3, or Desktop.  
✅ Automatically installs dependencies.  
✅ Saves files to /storage/emulated/0/TecHelp/  
✅ Clean output + progress bars  
"""  
  
import os, sys, subprocess, importlib, warnings  
from typing import List, Optional  
from tqdm import tqdm  
warnings.filterwarnings("ignore")  
  
# --- Auto-install dependencies ---  
REQUIRED = ["yt_dlp", "tqdm"]  
for pkg in REQUIRED:  
    try:  
        importlib.import_module(pkg)  
    except ImportError:  
        print(f"📦 Installing {pkg} ...")  
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", pkg])  
  
from yt_dlp import YoutubeDL  
  
# ---------- Defaults ----------  
DEFAULT_OUT_DIR = "/storage/emulated/0/TecHelp"  
os.makedirs(DEFAULT_OUT_DIR, exist_ok=True)  
  
# ---------- Helper: download any video ----------  
def download_custom_link(url: str, out_dir: str = DEFAULT_OUT_DIR):  
    """Download any video (MP4) from a given link"""  
    print(f"\n▶ Downloading video from: {url}")  
    os.makedirs(out_dir, exist_ok=True)  
  
    ydl_opts = {  
        "outtmpl": os.path.join(out_dir, "%(title).100s.%(ext)s"),  
        "format": "best",  
        "quiet": True,  
        "no_warnings": True,  
        "ignoreerrors": True,  
        "merge_output_format": "mp4",  
    }  
  
    try:  
        with YoutubeDL(ydl_opts) as ydl:  
            result = ydl.extract_info(url, download=False)  
            entries = result["entries"] if "entries" in result else [result]  
            for entry in tqdm(entries, desc="Downloading Video", unit="video"):  
                if entry and entry.get("webpage_url"):  
                    ydl.download([entry["webpage_url"]])  
        print(f"✅ Saved to: {out_dir}\n")  
    except Exception as e:  
        print(f"⚠️ Failed: {e}")  
  
# ---------- Helper: download MP3 only ----------  
def download_audio_only(url: str, out_dir: str = DEFAULT_OUT_DIR):  
    """Download MP3 audio from a given link"""  
    print(f"\n🎵 Downloading MP3 from: {url}")  
    os.makedirs(out_dir, exist_ok=True)  
  
    ydl_opts = {  
        "outtmpl": os.path.join(out_dir, "%(title).100s.%(ext)s"),  
        "format": "bestaudio/best",  
        "quiet": True,  
        "no_warnings": True,  
        "ignoreerrors": True,  
        "postprocessors": [{  
            "key": "FFmpegExtractAudio",  
            "preferredcodec": "mp3",  
            "preferredquality": "192",  
        }],  
    }  
  
    try:  
        with YoutubeDL(ydl_opts) as ydl:  
            result = ydl.extract_info(url, download=False)  
            entries = result["entries"] if "entries" in result else [result]  
            for entry in tqdm(entries, desc="Downloading Audio", unit="track"):  
                if entry and entry.get("webpage_url"):  
                    ydl.download([entry["webpage_url"]])  
        print(f"✅ MP3 saved to: {out_dir}\n")  
    except Exception as e:  
        print(f"⚠️ Failed: {e}")  
  
# ---------- TikTok account video fetching ----------  
def get_tiktok_videos(username: str) -> List[str]:  
    username = username.lstrip("@")  
    playlist_url = f"https://www.tiktok.com/@{username}"  
    ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True, "no_warnings": True}  
    try:  
        with YoutubeDL(ydl_opts) as ydl:  
            info = ydl.extract_info(playlist_url, download=False)  
    except Exception as e:  
        print(f"⚠️ Failed to fetch for @{username}: {e}")  
        return []  
    entries = info.get("entries") if isinstance(info, dict) else None  
    if not entries:  
        vid = info.get("id") if isinstance(info, dict) else None  
        if vid:  
            return [f"https://www.tiktok.com/@{username}/video/{vid}"]  
        return []  
    urls = []  
    for e in entries or []:  
        if not isinstance(e, dict): continue  
        vid_id = e.get("id") or e.get("url") or e.get("webpage_url")  
        if not vid_id: continue  
        urls.append(vid_id if vid_id.startswith("http") else f"https://www.tiktok.com/@{username}/video/{vid_id}")  
    return urls  
  
# ---------- Download TikTok account videos ----------  
def download_user_videos(username: str, count: Optional[int] = None,  
                         out_base: str = DEFAULT_OUT_DIR):  
    username = username.lstrip("@")  
    out_dir = os.path.join(out_base, username)  
    os.makedirs(out_dir, exist_ok=True)  
    urls = get_tiktok_videos(username)  
    if not urls:  
        print("⚠️ No videos found.")  
        return  
    total = len(urls)  
    print(f"\n✅ Found {total} videos for @{username}.")  
    if count is None:  
        try:  
            raw = input(f"How many videos to download (1–{total}) [default {total}]: ").strip()  
            n = total if raw == "" else int(raw)  
            n = max(1, min(n, total))  
        except ValueError:  
            n = total  
    else:  
        n = max(1, min(count, total))  
    to_download = urls[:n]  
    print(f"\n▶ Downloading {n} video(s) into {out_dir}\n")  
  
    ydl_opts = {  
        "outtmpl": os.path.join(out_dir, "%(upload_date)s_%(id)s.%(ext)s"),  
        "format": "best",  
        "quiet": True,  
        "no_warnings": True,  
        "ignoreerrors": True,  
        "merge_output_format": "mp4",  
    }  
  
    with YoutubeDL(ydl_opts) as ydl:  
        for url in tqdm(to_download, desc=f"Downloading @{username}", unit="video"):  
            try:  
                ydl.download([url])  
            except Exception:  
                continue  
    print(f"\n✅ Done! Videos saved in: {out_dir}")  
    if os.path.exists("/data/data/com.termux/files/usr/bin/am"):  
        os.system(f'am start -a android.intent.action.VIEW -d "file://{out_dir}" >/dev/null 2>&1')  
  
# ---------- Main menu ----------  
def main_menu():  
    usernames: List[str] = []  
  
    while True:  
        print("\n========== Universal Downloader ==========\n")  
        print(f"Output folder : {DEFAULT_OUT_DIR}")  
        print(f"Usernames     : {', '.join(usernames) if usernames else '(none)'}")  
        print("\nMenu:")  
        print("  1) Add TikTok username")  
        print("  2) Remove username")  
        print("  3) Download TikTok user videos")  
        print("  4) Clear usernames")  
        print("  5) Download from any custom link (MP4)")  
        print("  6) Download MP3 (audio only) from link")  
        print("  7) Explore my projects")  
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
            for i, u in enumerate(usernames, 1):  
                print(f"  {i}) {u}")  
            idx = input("Enter number to remove: ").strip()  
            if idx.isdigit() and 1 <= int(idx) <= len(usernames):  
                print(f"🗑 Removed: {usernames.pop(int(idx)-1)}")  
  
        elif choice == "3":  
            if not usernames:  
                print("⚠️ Add at least one username first.")  
                continue  
            for user in list(usernames):  
                download_user_videos(user)  
  
        elif choice == "4":  
            usernames.clear()  
            print("🧹 Cleared usernames.")  
  
        elif choice == "5":   # Custom link MP4  
            link = input("Paste any video link: ").strip()  
            if link:  
                download_custom_link(link)  
            else:  
                print("⚠️ Invalid link.")  
  
        elif choice == "6":   # Custom link MP3  
            link = input("Paste any link to extract MP3: ").strip()  
            if link:  
                download_audio_only(link)  
            else:  
                print("⚠️ Invalid link.")  
  
        elif choice == "7":   # Explore projects silently
            print("\n🌐 Choose a project to open:")
            print("  1) Love Games (https://love-games.netlify.app)")
            print("  2) Watch Party (https://watch-party-yt.netlify.app/)")
            proj_choice = input("Enter 1 or 2: ").strip()

            if proj_choice == "1":
                url = "https://love-games.netlify.app"
            elif proj_choice == "2":
                url = "https://watch-party-yt.netlify.app/"
            else:
                print("⚠️ Invalid choice.")
                continue

            try:
                # Android / Termux
                if os.path.exists("/data/data/com.termux/files/usr/bin/am"):
                    os.system(f'am start -a android.intent.action.VIEW -d "{url}" >/dev/null 2>&1')
                else:  # Desktop / Linux
                    os.system(f'xdg-open "{url}" >/dev/null 2>&1')
            except Exception:
                print(f"⚠️ Failed to open: {url}")

        elif choice == "0":  
            print("👋 Exiting.")  
            break  
        else:  
            print("Invalid option. Enter 0–7.")  

# ---------- Entry ----------  
if __name__ == "__main__":  
    try:  
        main_menu()  
    except KeyboardInterrupt:  
        print("\nStopped by user.")  
        sys.exit(0)
