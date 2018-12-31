import sys
import json
import math
from collections import Counter
import spotipy
import spotipy.util as util
import copy

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

def remove_useless_keys(array):
    keys = ["type", "key", "mode", "track_href", "speechiness", "instrumentalness", "id", "uri", "analysis_url", "duration_ms", "time_signature"]
    for key in keys:
        del array[key]

def get_average_audio_features(audioFeatures):
    average = {'acousticness': 0, 'danceability': 0, 'energy': 0, 'liveness': 0, 'loudness': 0, 'tempo': 0, 'valence': 0}
    for feature in audioFeatures:
        average['acousticness'] = average['acousticness'] + feature['acousticness']
        average['danceability'] = average['danceability'] + feature['danceability']
        average['energy'] = average['energy'] + feature['energy']
        average['liveness'] = average['liveness'] + feature['liveness']
        average['loudness'] = average['loudness'] + feature['loudness']
        average['tempo'] = average['tempo'] + feature['tempo']
        average['valence'] = average['valence'] + feature['valence']
    for feature in average:
        a = average[feature] / len(audioFeatures)
        average[feature] = float("%0.4f"%a)
    return average

def get_song_by_audio_features(song, features):
    for feature in features:
        if song["acousticness"] == feature["acousticness"]:
            if song["danceability"] == feature["danceability"]:
                if song["energy"] == feature["energy"]:
                    if song["liveness"] == feature["liveness"]:
                        if song["loudness"] == feature["loudness"]:
                            if song["tempo"] == feature["tempo"]:
                                if song["valence"] == feature["valence"]:
                                    return feature


# My UserID: 1190915995

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print('Usage: %s username' % (sys.argv[0]))
    sys.exit()

token = util.prompt_for_user_token(username, scope)

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

    print()

    features = get_audio_features(get_track_ids(tracks))
    # debugging:
    # f = open("log.txt", "a")
    # f.write(json.dumps(features, sort_keys=True, indent=4))
    # print(json.dumps(features, sort_keys=True, indent=4))

    avFeatures = get_average_audio_features(features)
    # print(json.dumps(avFeatures, sort_keys=True, indent=4))

    def key(d, t=avFeatures):
        return sum(abs(t[k] - v) for k, v in d.items())

    cutFeatures = copy.deepcopy(features)

    for f in cutFeatures:
        remove_useless_keys(f)
    closestSongFeatures = min(cutFeatures, key=key)
    # print(json.dumps(closestSongFeatures, sort_keys=True, indent=4))

    closestSong = sp.track(get_song_by_audio_features(closestSongFeatures, features)["id"])
    # print(json.dumps(song, sort_keys=True, indent=4))
    print("This song describes your playlist best: %r" %closestSong["name"])

else:
    print('Error. Token not set!')
