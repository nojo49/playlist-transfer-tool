import requests
import webbrowser
import base64

class SpotifyClient:
    CONST_AUTH_URL = 'https://accounts.spotify.com/api/token'
    CONST_USER_AUTH_URL_BASE = 'https://accounts.spotify.com/authorize?'
    CONST_CURRENT_USER_URL = 'https://api.spotify.com/v1/me'
    
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

        response = requests.post(self.CONST_AUTH_URL, {'grant_type': 'authorization_code', 'code': self.user_auth_code, 'redirect_uri': self.redirect_uri},
                                 headers={'Authorization': 'Basic ' + b64_encode_auth_string, 'Content-Type': 'application/x-www-form-urlencoded'})
        
        self.auth_token = response.json()['access_token']
        
    def get_current_user_id(self):
        response = requests.get(self.CONST_CURRENT_USER_URL, headers = {'Authorization': 'Bearer ' + self.auth_token})
        self.current_user_id = response.json()['display_name']
        
    def get_user_auth(self):
        # prompt user to permit access / login to account
        auth_url = f"{self.CONST_USER_AUTH_URL_BASE}client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&show_dialog=true"
        webbrowser.open(auth_url)
        self.user_auth_code = input("Please input the auth code url query param following ?code= \n")
    
    def get_user_playlists(self):
        self.get_user_auth()
        self.get_auth_token()
        self.get_current_user_id()
        