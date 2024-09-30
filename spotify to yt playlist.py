
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

token = 'BQCwT9_zr6heouVVkzAx_BZ8rUmgUlXXBLCRHalLwj7CqIPckeYe-vwCRzwvvyvfJ1qo9PeYNtobTRBcjbBrvdD97Ri7huxJe9OfY7SRjPL6YlbOZctf-wFoLKhBae5QioGfy9mAiSsD9gyeccq8bZGKSEn31K3RYw1-GPx81obHEcTcVRLws8oOHWjmG-qEpqBoHrnG0MdNj3iC6MPYpdinEl-ask2XLsMYdnGPZJJOQyfJQZRXDHf2f8jb77MGO0BXnzAsRnd9iKu9AYJZMqSv'
user_headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}

def playlist_read():
    playlist_id = "3QwtVQ404pmp68BjdaI5XG"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    song_names = []

    while url:
        response = requests.get(url, headers=user_headers)
        data = response.json()
        tracks = data['items']
        song_names.extend([item.get('track', {}).get('name') for item in tracks if item.get('track')])
        url = data.get('next')

    return song_names

def create_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["sample", "playlist"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    print(f'Playlist created: {response["snippet"]["title"]}')
    return response["id"]

def search_video(youtube, query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    return response['items'][0]['id']['videoId'] if response['items'] else None

def add_videos_to_playlist(youtube, playlist_id, video_ids):
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        requests = []
        for video_id in batch:
            requests.append({
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            })

        for request_body in requests:
            try:
                request = youtube.playlistItems().insert(
                    part="snippet",
                    body=request_body
                )
                response = request.execute()
                print(f'Added video ID {request_body["snippet"]["resourceId"]["videoId"]} to playlist {playlist_id}')
            except HttpError as e:
                if e.resp.status == 403:
                    print("Quota limit exceeded or permission issue.")
                else:
                    print(f'An error occurred: {e}')

if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/youtube']
    )
    creds = flow.run_local_server(port=0)
    youtube = build('youtube', 'v3', credentials=creds)

    playlist_title = "750 songs"
    playlist_description = "This is a description of my new playlist."
    playlist_id = create_playlist(youtube, playlist_title, playlist_description)
    print(f'Playlist ID: {playlist_id}')

    songs = playlist_read()

    video_ids = [search_video(youtube, song) for song in songs]
    video_ids = [video_id for video_id in video_ids if video_id]

    add_videos_to_playlist(youtube, playlist_id, video_ids)
