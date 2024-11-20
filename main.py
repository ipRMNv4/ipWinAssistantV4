import os
import webbrowser
import requests
import google.generativeai as genai
import schedule
import time
import re
import psutil
import subprocess
import notes
from download import download_file
from spotify_to_yt import final, access_token
import sys


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Use resource_path to load files
with open(resource_path('access_token.txt'), 'r') as f:
    access_token = f.read()


def show_news(newsapi, country='in'):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': newsapi,
        'country': country,
        'pageSize': 100
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        news_list = [
            {
                'title': article.get('title'),
                'url': article.get('url')
            }
            for article in articles
        ]
        return news_list
    else:
        print(f"Error: {response.status_code}")
        return None

def open_yt():
    webbrowser.open_new_tab("https://www.youtube.com")

def yt():
    args = input("search youtube: ")
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={args}")

def open_spotify():
    subprocess.Popen(r'"C:\Users\Raman Maan\AppData\Roaming\Spotify\Spotify.exe"')

def is_spotify_running():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'Spotify.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
result1 = is_spotify_running()



def final_check():
    if result1 == True and result1 == True:
        return True
final_result = final_check()

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



user_headers = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/json"
}
def playback_state():
    url = "https://api.spotify.com/v1/me/player"
    response = requests.get(url, headers=user_headers)

    if response.status_code == 200:
        try:
            data = response.json()
            if data["is_playing"]:
                return True
            else:
                return False
        except ValueError as e:
            print("Error decoding JSON:", e)

result2 = playback_state()
# playback controls [play,pause,play previous, play next]
def pause_playback():
    if final_result == True:
        url = "https://api.spotify.com/v1/me/player/pause"
        response = requests.put(url, headers=user_headers)
        if response.status_code == 200:
            print("Playback paused successfully!")
        else:
            print(f"Error pausing playback: {response.status_code}, {response.text}")
    else:
        print("No playback state available")
def resume_playback():
    if final_result == True:
        url = "https://api.spotify.com/v1/me/player/play"
        response = requests.put(url, headers=user_headers)
        if response.status_code == 200:
            print("Playback resumed successfully!")
        else:
            print(f"Error resuming playback: {response.status_code}")
    else:
        print("No playback state available")

def get_device_id():
    url = "https://api.spotify.com/v1/me/player/devices"
    response = requests.get(url, headers=user_headers)

    if response.status_code == 200:
        devices = response.json().get("devices", [])
        if devices:
            device_id = devices[0]['id']
            return device_id
        else:
            print("No devices found.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

def play_next():
    device_id = get_device_id()
    if final_result == True:
        url = "https://api.spotify.com/v1/me/player/next"
        response = requests.post(url, headers=user_headers, json={"device_id": device_id})
        if response.status_code == 200:
            print("Next playback resumed successfully!")
        else:
            print(f"Error next playback: {response.status_code}")
    else:
        print("No playback state available")
def play_previous():
    device_id = get_device_id()
    if final_result == True:
        url = "https://api.spotify.com/v1/me/player/previous"
        response = requests.post(url, headers=user_headers, json={"device_id": device_id})
        if response.status_code == 200:
            print("Previous playback resumed successfully!")
        else:
            print(f"Error previous playback: {response.status_code}")
    else:
        print("No playback state available")

def currently_playing():
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    response = requests.get(url, headers=user_headers)

    if response.status_code == 200:
        data = response.json()


        song_name = data.get('item', {}).get('name')
        artist_name = data.get('item', {}).get('artists', [{}])[0].get('name')
        if song_name and artist_name:
            return f"{song_name} by {artist_name}"
        else:
            return "error", "error"
    else:
        print("No song playing")
        return "error", "error"


def clean_text(text):
    cleaned_text = re.sub(r'[*]', '', text)
    return cleaned_text.strip()
def main():
    newsapi = os.getenv('NEWS_API_KEY')

    '''
     open_spotify()
     pause_playback()
     resume_playback()
    '''
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])

    while True:
        final_check()
        i = input("You: ").lower()
        if i == "open youtube":
            open_yt()

        elif i == "youtube":
            yt()

        elif i == "transfer playlist":
            final()

        elif i == "open spotify":
            open_spotify()

        elif i == "pause":
            pause_playback()

        elif i == "resume":
            resume_playback()

        elif i == "play next":
            play_next()

        elif i == "play previous" or i == "play prev":
            play_previous()

        elif i == "news":
            news = show_news(newsapi, country='in')
            if news:
                for article in news:
                    print(f"Title: {article['title']}\nURL: {article['url']}\n")

        elif i == "notes":
            while True:
                notes.notes()
                if input("Type 'exit' to go back: ").lower() == "exit":
                    break

        elif i == "open discord" or i == "open dc":
            subprocess.Popen(r"C:\Users\Raman Maan\AppData\Local\Discord\app-1.0.9155\Discord.exe")

        elif i.startswith("https://"):
            download_file(i)
        else:
            chat.send_message(i)
            latest_message = chat.history[-1]
            response_text = latest_message.parts[0].text
            cleaned_response = clean_text(response_text)
            print("AI:", cleaned_response)

if __name__ == '__main__':
    main()
