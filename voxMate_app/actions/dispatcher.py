from actions.handlers.spotify_app import SpotifyPlayer

# Initisalse SportifyPlayer
spotify_player = SpotifyPlayer()

def handle_cmd(cmd):
    if cmd.get('cmd') == 'spotify_play':
        play = spotify_player.handle_spotify_play(cmd)
        if not play:
            pass


        # add responses to handle_spotify_play
        # response = spotify_player.handle_spotify_play(cmd)
        #  if not spotify_player.handle_spotify_play(cmd):
        #       response("Failed to play spotify")

    # cmd should be in format:
    # {
    # "cmd": "spotify_play",
    # "params": query,
    # "type": "media"
    # }

    # Need to return true or false
    # To to effectively take state
