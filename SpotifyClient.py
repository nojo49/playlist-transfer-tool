import requests
import webbrowser
import base64
from spotifyplaylist import spotify_playlist


class SpotifyClient:
    CONST_AUTH_URL = 'https://accounts.spotify.com/api/token'
    CONST_USER_AUTH_URL_BASE = 'https://accounts.spotify.com/authorize?'
    CONST_CURRENT_USER_URL = 'https://api.spotify.com/v1/me'
    CONST_USERS_BASE_URL = 'https://api.spotify.com/v1/users/'
    CONST_PLAYLISTS_BASE_URL = 'https://api.spotify.com/v1/playlists/'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = 'http://127.0.0.1:3000'

    def get_auth_token(self):
        # base64 encode the client id and secret for auth header
        auth_string = self.client_id + ':' + self.client_secret
        auth_string_ascii_bytes = auth_string.encode("ascii")
        b64_bytes = base64.b64encode(auth_string_ascii_bytes)
        b64_encode_auth_string = b64_bytes.decode("ascii")

        response = requests.post(
            self.CONST_AUTH_URL,
            {'grant_type': 'authorization_code',
             'code': self.user_auth_code,
             'redirect_uri': self.redirect_uri},
            headers={'Authorization': 'Basic ' + b64_encode_auth_string,
                     'Content-Type': 'application/x-www-form-urlencoded'}
        )
        self.auth_token = response.json()['access_token']

    def get_current_user_id(self):
        response = requests.get(
            self.CONST_CURRENT_USER_URL,
            headers={'Authorization': 'Bearer ' + self.auth_token}
            )
        self.current_user_id = response.json()['display_name']

    def get_user_auth(self):
        # prompt user to permit access / login to account
        auth_url = (
            f"{self.CONST_USER_AUTH_URL_BASE}"
            f"client_id={self.client_id}&response_type=code"
            f"&scope=playlist-read-private playlist-read-collaborative"
            f"&redirect_uri={self.redirect_uri}&show_dialog=true"
            )

        webbrowser.open(auth_url)
        self.user_auth_code = input(
            "Please input the auth code url query param following ?code= \n"
            )

    def run_auth_flow(self):
        self.get_user_auth()
        self.get_auth_token()
        self.get_current_user_id()

    def get_user_playlists(self):
        playlist_url = (
            f"{self.CONST_USERS_BASE_URL}{self.current_user_id}"
            f"/playlists"
        )

        all_playlists_json = requests.get(
            playlist_url,
            {'limit': 50},
            headers={
                'Authorization': 'Bearer ' + self.auth_token
            })

        all_playlists = all_playlists_json.json()
        owned_playlists_dict = dict()
        for playlist in all_playlists['items']:
            if playlist['owner']['id'] != self.current_user_id:
                continue
            owned_playlists_dict[playlist['id']] = playlist['name']

        self.user_playlists_data = owned_playlists_dict.copy()

    def get_playlist_info(self):
        first_key = list(self.user_playlists_data.keys())[0]
        playlist_name = self.user_playlists_data[first_key]
        playlist_url = (
            f"{self.CONST_PLAYLISTS_BASE_URL}"
            f"{first_key}/tracks"
        )

        # loop through responses in case response is paginated
        while True:
            response = requests.get(
                playlist_url,
                {'limit': 50},
                headers={
                    'Authorization': 'Bearer ' + self.auth_token
                })

            tracks_json = response.json()['items']
            tracks_dict = dict()
            for track in tracks_json:
                track_name = track['track']['name']
                artists_name = ''
                for artist in track['track']['artists']:
                    artists_name += artist['name'] + ' '
                tracks_dict[track_name] = artists_name

            # 'next' will have a value if there is more content to get
            if (response.json()['next'] is None):
                # if next is null, we have everything, break loop
                break
            else:
                # if there is more content, set url and loop runs again
                playlist_url = response.json()['next']

        self.user_playlists = spotify_playlist(playlist_name, tracks_dict)
