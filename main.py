import os
import requests
import datetime
import pickle
from pathlib import Path
import config

api_key = config.api_key
save_path = config.save_path
#

# stores playlist ID and corresponding playlist name
playlist_names = {
    'PLIW5foipZqFH4oBVXEg2_BqvZgtQ_Vs5y': 'osu!',
    'PL_qgCkE-Zy21qbjk0m07Tib0ZEPlzVJB-': 'Bop',
    'PL_qgCkE-Zy23Qr9GhBgaLapYxGH9_3wJZ': 'J-Rock Pop whatever',
    'PL_qgCkE-Zy20ooB5RzH9W_WjNphRAJh3-': 'Metal Vocals',
    'PL_qgCkE-Zy2028u7v98qe5UGmfwtojMDS': 'Instrumental Artcore',
    'PL_qgCkE-Zy21-6fuGBter-HqukdSLDQun': 'DnB',
    'PL_qgCkE-Zy20heQ4ntZxwNeRv3ve4u6Ef': 'Vocaloid',
    'PL_qgCkE-Zy22qDteav2_PoR1K9JwyRPTK': 'Breakcore',
    'PL_qgCkE-Zy22nG22ch-d7_i9G10i6bzvh': 'Metal no vocals',
    'PL_qgCkE-Zy210S6f-EMbhgRHoOY7v047u': 'Atmospheric Metal edition',
    'PL_qgCkE-Zy21cNXiocycsJXiQsXwz3ElV': 'Atmospheric',

}

# list with the sorted saved playlists
logs = sorted(os.listdir(save_path))


# output = [json_output['items'][i]['snippet']['title'] for i in range(len(json_output['items']))]


def get_request_url(playlist_id, page_token=''):
    """creates the request"""
    # yt api responds with a page containing 50 items and a token to request the next page
    # first page doesn't need a pageToken, so it's omitted from the url
    if page_token != '':
        page_token = '&pageToken=' + page_token
    return f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50{page_token}&playlistId={playlist_id}&key={api_key}'


def validate_playlist(playlist_id):
    """checks if the playlist id exists"""
    pass


def add_playlist(playlist_name, playlist_id):
    """adds e playlist to the tracker"""
    playlist_names[playlist_id] = playlist_name
    print(f'Playlist {playlist_name} successfully added to the tracker.')


def remove_playlist(playlist_id):
    """removes a playlist from the tracker"""
    del playlist_names[playlist_id]


def list_playlists():
    """lists all tracked playlists with name and ID"""
    for playlist_id, title in playlist_names:
        print(f'Playlist: {title:>10}, ID: {playlist_id}')


def list_missing_songs(*playlists):
    print('\nAll missing songs:')
    if playlists[0] == 'all':
        for playlist in playlist_names.values():
            with open(f'{save_path}/{playlist}/missing_songs', 'r') as file:
                file_content = file.read().split('\n')
                del file_content[-1] # last line gets removed because it's just a new line without content
                for line in file_content:
                    print(f'{playlist}: {line}')
    else:
        for playlist in playlists:
            with open(f'{save_path}/{playlist}/missing_songs', 'r') as file:
                file_content = file.read().split('\n')
                del file_content[-1] # last line gets removed because it's just a new line without content
                for line in file_content:
                    print(f'{playlist}: {line}')


def save_missing_songs(  # loop through each folder, create a file with the missing songs
        period=1):  # period should by default be 1 day but also with possibility to list all (coming soontm)
    """compares previous log to the current one and lists the missing entires"""
    for playlist in logs:
        print(f'Searching for missing songs in {playlist}...')
        playlist_logs = sorted(os.listdir(f'{save_path}/{playlist}'))
        if 'missing_songs' in playlist_logs:
            playlist_logs.remove('missing_songs')

        with open(f'{save_path}/{playlist}/{playlist_logs[-1]}', 'rb') as file:
            # current_playlist = file.read().split('\n')
            # print(current_playlist)
            current_playlist = pickle.load(file)

        with open(f'{save_path}/{playlist}/{playlist_logs[-1 - period]}', 'rb') as file:
            # past_playlist = file.read().split('\n')
            past_playlist = pickle.load(file)

        # append missing maps to the "missing_songs" file
        with open(f'{save_path}/{playlist}/missing_songs', 'a') as file:
            # past_playlist = file.read().split('\n')
            new_missing_songs = [item for item in past_playlist if item not in current_playlist]
            if len(new_missing_songs) == 0:
                print('No new missing songs found')
            else:
                print(f'Missing songs:')
                for video_id, title in new_missing_songs:
                    file.write(title)
                    file.write('\n')
                    print(title)


def get_playlist_titles():
    for playlist_id in playlist_names.keys():
        titles = []
        nextPageToken = ''

        while True:

            json_output = requests.get(get_request_url(playlist_id, nextPageToken)).json()
            video_titles = [(json_output['items'][i]['id'], json_output['items'][i]['snippet']['title']) for i in
                            range(len(json_output['items']))]  # creates tuple (video_id, video_title)

            titles += video_titles

            # if there is no next page, the "nextPageToken" attribute won't exist, thus causing a KeyError
            try:
                nextPageToken = json_output['nextPageToken']
            except KeyError:
                break

        save_playlist_to_file(titles, playlist_id)
    return titles


def save_playlist_to_file(playlist_content, playlist_id):
    # create folder for playlist, if it does not exist yet
    Path(f'{save_path}/{playlist_names[playlist_id]}').mkdir(parents=True, exist_ok=True)
    with open(
            f'{save_path}/{playlist_names[playlist_id]}/{playlist_names[playlist_id]} {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}',
            'wb') as file:
        pickle.dump(playlist_content, file)
        # for item in playlist:
        #     # write each item on a new line
        #     pickle.dump(item, file)
        #     # file.write(f'{id}, ')
        #     # file.write(song_title)
        #     # file.write('\n')
        print(f'Playlist "{playlist_names[playlist_id]}" saved.')


get_playlist_titles()
save_missing_songs()
list_missing_songs('all')
