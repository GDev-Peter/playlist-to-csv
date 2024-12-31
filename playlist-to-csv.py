import requests
import json
import re
import csv
import argparse

def get_spotify_playlist_tracks(playlist_url, api_key):
    """
    Scrapes the tracks in a Spotify playlist given its URL.

    Args:
        playlist_url (str): URL of the Spotify playlist.
        api_key (str): Spotify API access token.

    Returns:
        list: A list of dictionaries containing track names, their artists, and duration.
    """
    # Validate the playlist URL
    if not re.match(r'^https://open\.spotify\.com/playlist/[a-zA-Z0-9]+$', playlist_url):
        raise ValueError("Invalid Spotify playlist URL")

    # Extract playlist ID from URL
    playlist_id = playlist_url.split('/')[-1].split('?')[0]

    # Define headers for Spotify web API
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    # Spotify API endpoint for playlist details
    endpoint = f'https://api.spotify.com/v1/playlists/{playlist_id}'

    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extract tracks from the playlist
        tracks = []
        for item in data['tracks']['items']:
            track = item['track']
            track_name = track['name']
            track_artists = ', '.join(artist['name'] for artist in track['artists'])
            track_duration_ms = track['duration_ms']
            track_duration_min = track_duration_ms // 60000
            track_duration_sec = (track_duration_ms % 60000) // 1000
            track_duration = f"{track_duration_min}:{track_duration_sec:02}"
            tracks.append({
                'track_name': track_name,
                'track_artists': track_artists,
                'track_duration': track_duration
            })

        return tracks

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape Spotify playlist tracks and save them to a CSV file.")
    parser.add_argument("--api-key", required=True, help="Spotify API access token.")
    parser.add_argument("--playlist-url", required=True, help="URL of the Spotify playlist.")
    args = parser.parse_args()

    try:
        tracks = get_spotify_playlist_tracks(args.playlist_url, args.api_key)
        if tracks:
            # Write the tracks to a CSV file
            csv_file = 'spotify_playlist.csv'
            with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['track_name', 'track_artists', 'track_duration'])
                writer.writeheader()
                writer.writerows(tracks)
            print(f"Tracks have been saved to {csv_file}.")
        else:
            print("No tracks found in the playlist.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print("An error occurred:", e)

