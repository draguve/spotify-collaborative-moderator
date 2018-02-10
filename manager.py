import pprint
import spotipy
import spotipy.util as util
from collections import defaultdict
import settings
import os.path as path 
import pickle

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
    
def add_tracks(tracks):
    if tracks == []:
        return
    token = get_token()
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        sp.user_playlist_add_tracks(username, playlist_id, tracks, position=None)
        #pprint.pprint(results)
    else:
        print("Can't get token for", username)


def load_backup():
    filename = settings.playlist_id + '.backup'
    if(not(path.isfile(filename))):
        return None
    with open(filename,'rb') as f:
        __playlist__ = pickle.load(f)
    return __playlist__

def backup_playlist(songs_list):
    songs = {}
    filename = settings.playlist_id + '.backup'
    old_backup = load_backup()
    songs[0]=songs_list

    if old_backup!=None:
        for i in range(settings.number_of_backups):
            if i in old_backup:
                songs[i+1] = old_backup[i]

    with open(filename,'wb') as f:
        pickle.dump(songs,f)

def remove_all_songs():
    allsongs = build_list(get_list())
    remove_tracks(removal_conversion(allsongs))

def revert_from_backup(backup_number):
    backup = load_backup()
    if backup_number in backup:
        songs = []
        for song in backup[backup_number]:
            songs.append(song['uri'])
        remove_all_songs()
        add_tracks(songs)
    else:
        print("Could'nt find specific backup")

#if __name__ == "__main__":
#    remove_double_tracks()