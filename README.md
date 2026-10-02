# YT to Spotify Migrator

A simple script created for one reason: I was too lazy (and paranoid) to use third-party apps like Soundiiz or TuneMyMusic and give them full access to my accounts.

This project automates the import of your "Liked Songs" from YouTube Music directly into your Spotify "Liked Songs" library, maintaining the exact chronological order in which you saved them.

## Why this script?
YouTube Music has strict anti-bot protections that block most unofficial API libraries. This script bypasses that issue by using Playwright to simulate a real browser (using your session cookies), cleanly extracting the data, and pushing it to Spotify via their official API (spotipy).

## Roadmap
- [x] Migrate "Liked Songs" from YT Music to Spotify.
- [ ] Support for migrating specific playlists.
- [ ] Export support for Apple Music.
- [ ] Export support for Tidal.

---

## Installation

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Set up the environment:
   - Copy the example environment variables file:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and paste your Spotify API credentials.

---

## Step 1: Set up Spotify Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in and click "Create App" (name it whatever you like).
3. Go to the Settings of your App and in "Redirect URIs" add exactly this: `http://127.0.0.1:8888/callback` (make sure to save the changes).
4. Copy your `Client ID` and `Client Secret` and paste them into the `.env` file.

---

## Step 2: Get YouTube Music Cookies

For the script to read your songs without asking for Google passwords, it uses your current session cookies.

1. Open your regular browser and go to your Liked Music page on [YouTube Music](https://music.youtube.com/playlist?list=LM).
2. Open Developer Tools (F12) -> Network tab.
3. Refresh the page (F5).
4. Look for any request (they are usually named `browse` or `?list=LM`).
5. Right-click the request -> Copy -> Copy Request Headers.
6. Paste that into a new file named `cookies.json` in the same folder as the script.
*(It should look like a JSON object containing a "headers" key that includes "Cookie").*

---

## Step 3: Run the Migration

You can run the migration in a single step or in two parts if you prefer to review the extracted songs first.

**To do it all at once:**
```bash
python yt2spotify.py --all
```

**If you prefer doing it step by step:**
1. Extract from YouTube Music:
   ```bash
   python yt2spotify.py --extract
   ```
   *(This will generate a `songs.json` file)*
   
2. Import to Spotify:
   ```bash
   python yt2spotify.py --import-sp
   ```

Done. Enjoy your music.