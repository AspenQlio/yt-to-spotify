import os
import json
import argparse
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()
def extract_from_youtube(cookies_path='cookies.json', output_path='songs.json'):
    """Extracts 'Liked Music' from YouTube Music using Playwright."""
    print("Starting extraction from YouTube Music...")
    songs = []
    
    if not os.path.exists(cookies_path):
        print(f"Error: Cookie file '{cookies_path}' not found.")
        print("Check README.md for instructions on how to obtain it.")
        return []

    with sync_playwright() as p:
        # Use a realistic User-Agent to avoid "Unsupported Browser" blocks
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Load cookies
        with open(cookies_path, 'r') as f:
            cookie_data = json.load(f)
            
        # Format cookies for Playwright
        cookie_string = ""
        if 'requestHeaders' in cookie_data:
            for header in cookie_data['requestHeaders']['headers']:
                if header['name'] == 'Cookie':
                    cookie_string = header['value']
                    break
        elif 'headers' in cookie_data and 'Cookie' in cookie_data['headers']:
            cookie_string = cookie_data['headers']['Cookie']
            
        playwright_cookies = []
        for c in cookie_string.split(';'):
            if '=' in c:
                name, value = c.split('=', 1)
                playwright_cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'url': 'https://music.youtube.com'
                })
                
        context.add_cookies(playwright_cookies)
        page = context.new_page()
        
        print("Navigating to your 'Liked Songs'...")
        page.goto("https://music.youtube.com/playlist?list=LM")
        page.wait_for_load_state("networkidle")
        
        try:
            page.wait_for_selector("ytmusic-responsive-list-item-renderer", timeout=15000)
            print("Song list found. Processing...")
            
            elements = page.query_selector_all("ytmusic-responsive-list-item-renderer")
            for el in elements:
                title_el = el.query_selector(".title")
                artist_el = el.query_selector(".secondary-flex-columns yt-formatted-string")
                if title_el and artist_el:
                    title = title_el.inner_text()
                    artist = artist_el.inner_text()
                    # Clean text
                    artist = artist.split('•')[0].strip() if '•' in artist else artist.strip()
                    songs.append({"title": title, "artist": artist})
                    
            print(f"Successfully extracted {len(songs)} songs.")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(songs, f, indent=4, ensure_ascii=False)
            print(f"Saved temporarily to '{output_path}'.")
            
        except Exception as e:
            print(f"Error extracting songs. Make sure cookies are updated.\nDetail: {e}")
            
        browser.close()
    return songs
def import_to_spotify(input_path='songs.json'):
    """Reads extracted songs and injects them into Spotify's 'Liked Songs'."""
    if not os.path.exists(input_path):
        print(f"Error: '{input_path}' not found. Run the extraction first.")
        return

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    
    if not client_id or not client_secret:
        print("Error: Missing Spotify credentials in .env file.")
        return

    print("Connecting to Spotify...")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='user-library-modify',
        cache_path='.spotify_cache'
    ))
    
    # Force auth if necessary
    try:
        sp.me()
    except Exception as e:
        print(f"Spotify authentication error: {e}")
        return

    print(f"Reading songs from '{input_path}'...")
    with open(input_path, 'r', encoding='utf-8') as f:
        liked_songs = json.load(f)
        
    # Reverse to keep chronological order (oldest first, newest last)
    liked_songs.reverse()
    
    tracks_to_add = []
    total_added = 0
    
    for song in liked_songs:
        query = f"{song['title']} {song['artist']}"
        print(f"Searching: {query}")
        
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            tracks_to_add.append(track_uri)
        else:
            print(f"   Not found: {query}")
            
        # Send in batches of 20 to avoid URI length limits
        if len(tracks_to_add) >= 20:
            sp.current_user_saved_tracks_add(tracks_to_add)
            total_added += len(tracks_to_add)
            print(f"   Saved {len(tracks_to_add)} songs to your library...")
            tracks_to_add = []
            
    if tracks_to_add:
        sp.current_user_saved_tracks_add(tracks_to_add)
        total_added += len(tracks_to_add)
        print(f"   Saved {len(tracks_to_add)} songs to your library...")
    
    print(f"Migration completed! {total_added} songs imported to Spotify.")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate your Liked Songs from YouTube Music to Spotify.")
    parser.add_argument('--extract', action='store_true', help="Extract songs from YouTube Music")
    parser.add_argument('--import-sp', action='store_true', help="Import extracted songs to Spotify")
    parser.add_argument('--all', action='store_true', help="Run extraction and then import")
    
    args = parser.parse_args()
    
    if args.all:
        extract_from_youtube()
        import_to_spotify()
    elif args.extract:
        extract_from_youtube()
    elif args.import_sp:
        import_to_spotify()
    else:
        parser.print_help()