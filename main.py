import sys
import json
import math
from collections import Counter
import spotipy
import spotipy.util as util

scope = 'playlist-read-collaborative'

def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def get_track_ids(tracks):
    tids = []
    for i, t in enumerate(tracks):
        # print(' ', i, t['track']['name'])
        tids.append(t['track']['uri'])
    return tids

def get_audio_features(trackIDs):
    turns = int(math.ceil(len(trackIDs)/50))
    features = []
    for x in range(0, turns):
        start = x * 50
        if (start + 50 < len(trackIDs)):
            end = start + 50
        else:
            end = len(trackIDs)
        results = sp.audio_features(trackIDs[start:end])
        # print(results)
        features.extend(results)
    return features


# My UserID: 1190915995

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print('Usage: %s username' % (sys.argv[0]))
    sys.exit()


token = util.prompt_for_user_token(username, scope)

# print token
#
if token:
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)
    # print(json.dumps(playlists, sort_keys=True, indent=4))
    print()
    playlistNames = []
    for ind, playlist in enumerate(playlists['items']):
        print('['+ str(ind) +']: '+ playlist['name'])
        playlistNames.append(playlist['name'])
    # print(playlistNames)
    print()
    inp = input('Choose the number in front of the playlist to get more info about it: ')
    print()
    selectedPlaylist = playlists['items'][int(float((inp)))]
    print(selectedPlaylist)
    # print(selectedPlaylist)
    tracks = get_playlist_tracks(username, selectedPlaylist['id'])
    # print(json.dumps(tracks, sort_keys=True, indent=4))


    # Frequency Analysis of added_by
    if(selectedPlaylist['collaborative']):
        userFrequency = []
        for track in tracks:
            userFrequency.append(track['added_by']['id'])

        for key in Counter(userFrequency):
            user = sp.user(key)['display_name']
            frequency = Counter(userFrequency)[key]
            relFrequency = float(100*frequency/len(tracks))
            print(user + ": " + str(frequency) + " ("+ str(float("%0.2f"%relFrequency)) +"%)")

    trackIDs = get_track_ids(tracks)
    features = get_audio_features(trackIDs)
    # print(json.dumps(features, sort_keys=True, indent=4))
else:
    print('Error. Token not set!')
