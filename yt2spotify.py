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
