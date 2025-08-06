from SpotifyClient import SpotifyClient

def main():
    input_client_id = input("Spotify client id: \n")
    input_client_secret = input("Spotify client secret: \n")
    sc = SpotifyClient(input_client_id, input_client_secret)
    sc.get_user_playlists()

if __name__ == "__main__":
    main()
