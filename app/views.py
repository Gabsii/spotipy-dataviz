import os
from django.shortcuts import render, redirect
from app.main import generate_auth_url, get_token_for_frontend, get_playlists, get_playlist, get_current_user, is_collaborative_playlist, get_playlist_tracks, get_average_audio_features, get_closest_song,  get_audio_features, get_track_ids, get_user_frequency

# Create your views here.

def index(request):
    login_auth_url = generate_auth_url()
    url_params = request.GET
    if url_params.get('code'):
        code = url_params.get('code')
        token = get_token_for_frontend(code)
        response = redirect('/user')
        response.set_cookie('token', token.get('access_token'), max_age=token.get('expires_in'))
        response.set_cookie('refresh_token', token.get('refresh_token'), max_age=token.get('expires_in'))
        return response
    else:
        return render(request, 'index.html', {"login_link": login_auth_url})

def user(request):
    if request.COOKIES.get('token'):
        token = request.COOKIES.get('token')
        playlists = get_playlists(token)
        user = get_current_user(token)
        return render(request, 'user.html', {'user': user, 'playlists': playlists, 'n': range(3)})
    else:
        redirect('/')

def playlist(request):
    if request.COOKIES.get('token'):
        token = request.COOKIES.get('token')
        playlist_id = request.GET.get('playlist')
        user_id = request.GET.get('user')

        user = get_current_user(token)
        playlist = get_playlist(token, user_id, playlist_id)

        is_collaborative = is_collaborative_playlist(token, user_id, playlist_id)
        tracks = get_playlist_tracks(token, user_id, playlist_id)
        trackIDs = get_track_ids(tracks)
        features = get_audio_features(token, trackIDs)

        if is_collaborative:
            frequency = get_user_frequency(token, tracks)
        else:
            frequency = None

        average_features = get_average_audio_features(features)
        closestSong = get_closest_song(token, tracks, features, average_features)
        return render(request, 'playlist.html', {'user': user, 'playlist': playlist, 'frequency': frequency, 'average_features': average_features, 'closestSong': closestSong})
    else:
        redirect('/')
