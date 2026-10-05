# YT to Spotify Migrator

> A highly reliable browser automation script to migrate your "Liked Songs" from YouTube Music directly into your Spotify library, bypassing anti-bot protections.

YT to Spotify Migrator automates the tedious process of moving your music library between platforms. Instead of relying on third-party services that require full access to your accounts and often fail due to strict APIs, this tool uses Playwright to simulate a real browser session (using your own cookies) to extract your music and pushes it to Spotify via their official API (spotipy).

## Features

- **Anti-Bot Bypass:** Uses Playwright browser simulation to bypass YouTube Music's strict scraping protections.
- **Chronological Sync:** Maintains the exact order in which you saved your songs on YouTube.
- **Privacy-First:** Your credentials and cookies never leave your machine; no third-party data sharing.
- **Modular Execution:** Extract data first to review it (`songs.json`), or run the entire migration in one step.
- **Future-Ready:** Roadmap includes migrating specific playlists and exporting to Apple Music and Tidal.

## Architecture

The migration consists of a two-step pipeline. First, the extraction module reads your YouTube Music session cookies (provided manually) and drives a headless Chromium browser via Playwright to scroll and extract your "Liked Songs". Second, the import module authenticates with Spotify via OAuth2 (`spotipy`) and incrementally adds the extracted tracks to your Spotify library.

## Tech Stack

- **Language:** Python
- **Browser Automation:** Playwright
- **Spotify Integration:** Spotipy (Official Spotify API Wrapper)

## Getting Started

### Prerequisites

- Python 3.11+
- A Spotify Developer account (for API credentials).
- Your YouTube Music session cookies.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AspenQlio/yt-to-spotify.git
   cd yt-to-spotify
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Set up Environment:**
   ```bash
   cp .env.example .env
   ```
   Add your Spotify `Client ID` and `Client Secret` to `.env`.

## Usage

1. **Obtain Spotify Credentials:**
   Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/), set the Redirect URI to `http://127.0.0.1:8888/callback`, and copy your credentials to `.env`.
2. **Obtain YouTube Cookies:**
   Go to YouTube Music's Liked Music page in your browser, copy the request headers from the Network tab (F12), and save them in a `cookies.json` file.
3. **Run the Migration:**
   - For a single-step migration: `python yt2spotify.py --all`
   - To extract only: `python yt2spotify.py --extract`
   - To import to Spotify: `python yt2spotify.py --import-sp`

## License

This project is licensed under the MIT License.
