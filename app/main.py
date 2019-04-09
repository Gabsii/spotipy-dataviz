import sys
import os
import json
import math
from collections import Counter
import spotipy
import spotipy.util as util
import copy

scope = 'playlist-read-collaborative'
redirect_url = 'http://localhost:8000/'

def get_playlist(token, user_id, playlist_id):
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist(user_id,playlist_id)
    # print(json.dumps(results, sort_keys=True, indent=4))
    return results

def get_playlist_tracks(token, username, playlist_id):
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    del sp
    return check_for_local_tracks(tracks)

def check_for_local_tracks(tracks):
    tracks_new = []
    for track in tracks:
        if not track['is_local']:
            tracks_new.append(track)
    return tracks_new

def get_track_ids(tracks):
    # text_file = open("Output.txt", "w")
    # text_file.write("%s" % tracks)
    # text_file.close()
    tids = []
    for i, t in enumerate(tracks):
        tids.append(t['track']['uri'])
    return tids

def get_audio_features(token, trackIDs):
    sp = spotipy.Spotify(auth=token)
    turns = int(math.ceil(len(trackIDs)/50))
    features = []
    for x in range(0, turns):
        start = x * 50
        if (start + 50 < len(trackIDs)):
            end = start + 50
        else:
            end = len(trackIDs)
        results = sp.audio_features(trackIDs[start:end])
        features.extend(results)
    del sp
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

def generate_auth_url():
    auth_url = spotipy.oauth2.SpotifyOAuth(os.environ['SPOTIPY_CLIENT_ID'], os.environ['SPOTIPY_CLIENT_SECRET'], redirect_url , None, scope).get_authorize_url();
    return auth_url;

def get_token_for_frontend(code):
    json_token_response = spotipy.oauth2.SpotifyOAuth(os.environ['SPOTIPY_CLIENT_ID'], os.environ['SPOTIPY_CLIENT_SECRET'], redirect_url , None, scope).get_access_token(code)
    return json_token_response

def get_playlists(token):
    sp = spotipy.Spotify(auth=token)
    playlists = sp.current_user_playlists()
    del sp
    return playlists

def get_current_user(token):
    sp = spotipy.Spotify(auth=token)
    me = sp.current_user()
    del sp
    return me


def get_token_for_console():
    if len(sys.argv) > 1:
        username = sys.argv[1]
        token = util.prompt_for_user_token(username, scope)
    else:
        print('Usage: %s username' % (sys.argv[0]))
        auth_url = generate_auth_url();
        print(auth_url);
        sys.exit()

def is_collaborative_playlist(token, user_id, playlist_id):
    sp = spotipy.Spotify(auth=token)
    result = sp.user_playlist(user_id, playlist_id)
    if result['collaborative']:
        return True
    else:
        return False

def get_user_frequency(token, tracks):
    sp = spotipy.Spotify(auth=token)
    user_tracks = []
    user_frequency = {}
    for track in tracks:
        user_tracks.append(track['added_by']['id'])

    for key in Counter(user_tracks):
        user = sp.user(key)['display_name']
        frequency = Counter(user_tracks)[key]
        relFrequency = float(100*frequency/len(tracks))
        print(user + ": " + str(frequency) + " ("+ str(float("%0.2f"%relFrequency)) +"%)")
        user_frequency[user] = str(frequency)
    return user_frequency

def get_closest_song(token, tracks, features, avFeatures):
    sp = spotipy.Spotify(auth=token)

    def key(d, t=avFeatures):
        return sum(abs(t[k] - v) for k, v in d.items())

    cutFeatures = copy.deepcopy(features)

    for f in cutFeatures:
        remove_useless_keys(f)
    closestSongFeatures = min(cutFeatures, key=key)

    return sp.track(get_song_by_audio_features(closestSongFeatures, features)["id"])

def main_console():
    token = get_token_for_console()
    if token:
        playlists = get_playlists(token)
        inp = input('Choose the number in front of the playlist to get more info about it: ')
        print()
        selectedPlaylist = playlists['items'][int(float((inp)))]
        tracks = get_playlist_tracks(username, selectedPlaylist['id'])


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
        avFeatures = get_average_audio_features(features)

        def key(d, t=avFeatures):
            return sum(abs(t[k] - v) for k, v in d.items())

        cutFeatures = copy.deepcopy(features)

        for f in cutFeatures:
            remove_useless_keys(f)
        closestSongFeatures = min(cutFeatures, key=key)

        closestSong = sp.track(get_song_by_audio_features(closestSongFeatures, features)["id"])
        print(json.dumps(closestSongFeatures, sort_keys=True, indent=4))

        print("This song describes your playlist best: %r" %closestSong["name"])

    else:
        print('Error. Token not set!')


# main_console()
