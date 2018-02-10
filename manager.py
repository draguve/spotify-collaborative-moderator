import pprint
import spotipy
import spotipy.util as util
from collections import defaultdict
import settings

username = settings.username
client_id=settings.client_id
client_secret=settings.client_secret
redirect_uri=settings.redirect_uri
playlist_id=settings.playlist_id

def get_list():
    token = get_token()
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.user_playlist(username,playlist_id)
        return results
    else:
        return None

def get_token():
    scope = 'playlist-modify-private'
    token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
    return token

def build_list(json):
    tracks = json['tracks']['items']
    playlist = []
    for i in range(len(tracks)):
        track={}
        track['added_by'] = tracks[i]['added_by']['uri']
        track['uri'] = tracks[i]['track']['uri']
        track['position'] = i
        playlist.append(track)
    return playlist

def split_tracks(built_tracks,songs_per_user):
    users = defaultdict(lambda : 0)
    songs_to_keep = []
    songs_to_remove = []
    for track in reversed(built_tracks):
        if users[track['added_by']] < songs_per_user:
            songs_to_keep.append(track)
            users[track['added_by']] += 1
        else:
            songs_to_remove.append(track)
    return songs_to_keep,songs_to_remove

def removal_conversion(to_remove):
    tracks_to_remove = []
    for x in to_remove:
        track = {}
        track['uri'] = x['uri']
        track['positions'] = [x['position']]
        tracks_to_remove.append(track)
    return tracks_to_remove

def remove_tracks(tracks_to_remove):
    if tracks_to_remove == []:
        return
    token = get_token()
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, tracks_to_remove)
        pprint.pprint(results)
    else:
        print("Can't get token for", username)
    
#if __name__ == "__main__":
#    remove_double_tracks()