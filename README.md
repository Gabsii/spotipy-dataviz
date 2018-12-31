# Goal

This project is made to fetch informations about collaborative playlists and visualize certain aspects of the playlist

# Setup

1. install spotipy

    `pip3 install spotipy`

2. setup Spotify developer account and create application

3. set environment variables

    ```export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
    export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
    ```

4. call app using

    `python main.py "username"`


# Visualized stuff

    - Cake diagram for submissions by user in collaborative playlists
    - Average Danceability, Energy, Liveness
    + the most fitting average song in the playlist

# Following ideas

- get the average song stats
- feed data via sockets to frontend app
