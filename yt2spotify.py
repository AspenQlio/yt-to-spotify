import os
import json
import argparse
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()
