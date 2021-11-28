# importing libraries
import csv
import os
import json
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

######################
# Loading channels id
with open('./channels_info.json', 'r') as f:
    channels_info = json.load(f)

channel_source = channels_info['channel_source']


# creating data folder to save all outputs in it
if not os.path.exists('./data'):
    os.mkdir('data')

###################################################
# # Start fetching data from the source channel # #
###################################################


###############################
# Authenticating Source Channel
credentials_source = None

# Load credentials if already exists
if os.path.exists('./credentials_source.pickel'):
    print('Loading Credentials...')
    with open('./credentials_source.pickel', 'rb') as cre:
        credentials_source = pickle.load(cre)

# Refresh or ask for new credentials if not valid
if not credentials_source or not credentials_source.valid:
    # refresh credentials
    if credentials_source and credentials_source.expired:
        print('Refreshing Credentials...')
        credentials_source.refresh(Request())
    else:
        print('Fetching new Credentials...')

        # creating flow object with read only
        flow = InstalledAppFlow.from_client_secrets_file(
            './SECRETS.json',
            scopes=['https://www.googleapis.com/auth/youtube.readonly']
        )

        flow.run_local_server(port=8080, prompt='consent')

        credentials_source = flow.credentials
        # saving credentials
        with open('./credentials_source.pickel', 'wb') as cre:
            print('Saving new Credentials...')
            pickle.dump(credentials_source, cre)

print('Done Authenticating Source Channel!')


# creating connector using credentials
youtubeSource = build('youtube', 'v3', credentials=credentials_source)


#####################
# fetch subscriptions
if not os.path.exists('./data/subscribtions.csv'):
    print('Start fetching - Subscribtions from the source channel!')

    # saving subscribtions
    with open('./data/subscribtions.csv', 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(['title','channelId'])
        next_page_token = None

        # stop if last page
        while not next_page_token:
            subsResponse = youtubeSource.subscriptions().list(
                part='snippet',
                channelId=channel_source,
                pageToken=next_page_token,
                maxResults=50
            ).execute()

            next_page_token = subsResponse.get('next_page_token')

            for item in subsResponse.get('items'):
                row = [
                    item['snippet']['title'],
                    item['snippet']['resourceId']['channelId']
                ]
                csv_writer.writerow(row)

    print('Done Fetching - Subscribtions from the source channel!')
else:
    print('Already Statisfied - Subscribtions from the source channel!')


#################
# fetch playlists
if not os.path.exists('./data/playlists.csv'):
    print('Start fetching - Playlists from the source channel!')

    # saving playlists
    with open('./data/playlists.csv', 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(['name','status','description','id','count'])

        next_page_token = None

        # stop if last page
        while not next_page_token:
            playlistResponse = youtubeSource.playlists().list(
                part='id,snippet,status,contentDetails',
                channelId=channel_source,
                pageToken=next_page_token,
                maxResults=50
            ).execute()

            next_page_token = playlistResponse.get('next_page_token')

            for item in playlistResponse.get('items'):
                row = [
                    item['snippet']['title'],
                    item['status']['privacyStatus'],
                    item['snippet']['localized']['description'],
                    item['id'],
                    item['contentDetails']['itemCount']
                ]

                csv_writer.writerow(row)

    print('Done Fetching - Playlists from the source channel!')
else:
    print('Already Statisfied - Playlists from the source channel!')


##############
# fetch videos
if not os.path.exists('./data/videos.csv'):
    print('Start Fetching - Videos!')

    # saving videos
    with open('./data/videos.csv', 'w', encoding='utf-8', newline='') as videos_CSV:
        csv_writer = csv.writer(videos_CSV, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(['playlist_name','playlist_id','video_id'])

        # getting videos from each playlist
        with open('./data/playlists.csv', 'r', encoding='utf-8') as playlist_CSV:
            csv_reader = csv.reader(playlist_CSV)
            next(csv_reader) # header

            for playlist in csv_reader:
                next_page_token = None

                # stop if last page
                while not next_page_token:
                    videos_respons = youtubeSource.playlistItems().list(
                        part='contentDetails',
                        playlistId=playlist[3],
                        pageToken=next_page_token,
                        maxResults=50
                    ).execute()

                    next_page_token = videos_respons.get('next_page_token')

                    for item in videos_respons.get('items'):
                        row = [
                            playlist[0],
                            playlist[3],
                            item['contentDetails']['videoId']
                        ]
                        csv_writer.writerow(row)

                    print(f'Done Fetching - Videos from playlist: {playlist[0]}...')

    print(f'Done Fetching - Videos!')
else:
    print('Already Statisfied - Videos!')