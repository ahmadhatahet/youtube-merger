# importing libraries
import csv
import os
import json
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.errors
from googleapiclient.discovery import build

######################
# Loading channels id
with open('./Channels_info.json', 'r') as f:
    channels_info = json.load(f)

channel_target = channels_info['channel_target']


# creating data folder to save all outputs in it
if not os.path.exists('./data'):
    os.mkdir('data')

##################################################
# # Start merging data from the source channel # #
##################################################


###############################
# Authenticating target Channel
credentials_target = None

# Load credentials if already exists
if os.path.exists('./credentials_target.pickel'):
    print('Loading Credentials...')
    with open('./credentials_target.pickel', 'rb') as cre:
        credentials_target = pickle.load(cre)

# Refresh or ask for new credentials if not valid
if not credentials_target or not credentials_target.valid:
    if credentials_target and credentials_target.expired:
        print('Refreshing Credentials...')
        credentials_target.refresh(Request())
    else:
        print('Fetching new Credentials...')

        # creating flow object with read only
        flow = InstalledAppFlow.from_client_secrets_file(
            './SECRETS.json',
            scopes=['https://www.googleapis.com/auth/youtube']
        )

        flow.run_local_server(port=8080, prompt='consent')

        credentials_target = flow.credentials
        # saving credentials
        with open('./credentials_target.pickel', 'wb') as cre:
            print('Saving new Credentials...')
            pickle.dump(credentials_target, cre)

print('Done Authenticating Target Channel!')



######################################
# creating connector using credentials
youtube_target = build('youtube', 'v3', credentials=credentials_target)


###########################
# subscribe to all channels
print('Start Subscribing to all channels...')

with open('./data/subscriptions.csv', 'r', encoding='utf-8') as subscriptionsCSV:
    csv_reader = csv.reader(subscriptionsCSV)
    next(csv_reader) # header

    for channel in csv_reader:

        youtube_target.subscriptions().insert(
            part='snippet',
            body={
                'snippet':{
                    'resourceId':{
                        'channelId':channel[1]
                    }
                }
            }
        ).execute()

print('Done Subscribing to all channels!')


####################
# creating playlists
print('Start Creating Playlists...')
openMode = 'w'
if os.path.exists('./data/playlists_inserted.csv'):
    openMode = 'a'
    # get the last line in the already inserted playlists
    with open('./data/playlists_inserted.csv', 'r', encoding='utf-8') as playlists_inserted_CSV:
        csv_reader = csv.reader(playlists_inserted_CSV)
        for instrtedPlaylist in csv_reader: pass

with open('./data/playlists_inserted.csv', openMode, encoding='utf-8', newline='') as playlists_inserted_CSV:
    csv_writer = csv.writer(playlists_inserted_CSV, quoting=csv.QUOTE_NONNUMERIC)
    # no need for headers when already new playlists is created
    if openMode == 'w':
        csv_writer.writerow(['name','old_id','new_id','count'])

    # get last not inserted playlists to continue inserting
    with open('./data/playlists.csv', 'r', encoding='utf-8') as playlists_CSV:
        csv_reader = csv.reader(playlists_CSV)
        for playlist in csv_reader:
            if playlist[0] == instrtedPlaylist[0]:
                break

        # starting after last inserted playlist
        exception_triggered = False
        for playlist in csv_reader:
            try:
                playlis_new_response = youtube_target.playlists().insert(
                    part='snippet,status',
                    body={
                        'snippet':{
                            'title':playlist[0],
                            'description':playlist[2]
                        },
                        'status':{
                            'privacyStatus':playlist[1]
                        }
                    }
                ).execute()
            except googleapiclient.errors.HttpError as e:
                exception_triggered = True
                print('\nError:')
                print('Unfortunately, Not all playlists were added, the Quota is reached for today.')
                print('Please try tomorrow.')
                print('This script will automatically restart from the last inserted playlist.')
                break

            row = [
                playlist[0],
                playlist[3],
                playlis_new_response['id'],
                playlist[4]
            ]
            # name, old_id, new_id
            csv_writer.writerow(row)
            print(f'Created {playlist[0]}...')

    if not exception_triggered: print('Done Creating PLaylists!')


####################################################################
# map each video playlist id from original to newly created playlist
if not os.path.exists('./data/videos_edited.csv'):
    print('Start mapping videos from old playlist id to new inserted one...')

    with open('./data/videos_edited.csv', 'w', encoding='utf-8', newline='') as edited_videos_CSV:
        csv_writer = csv.writer(edited_videos_CSV, quoting=csv.QUOTE_NONNUMERIC)

        with open('./data/videos.csv', 'r', encoding='utf-8') as videos_CSV:
            videos_reader = csv.reader(videos_CSV)

            # read header and write it, because same header is used in both files
            csv_writer.writerow(next(videos_reader))

            with open('./data/playlists_inserted.csv', 'r', encoding='utf-8') as playlists_CSV:
                playlists_reader = csv.reader(playlists_CSV)
                next(playlists_reader) # skip header

                for playlist in playlists_reader:
                    counter = int(playlist[3])

                    for video in videos_reader:
                        if video[1] == playlist[1]:
                            csv_writer.writerow([video[0], playlist[2], video[2]])
                        counter -= 1

                        if counter == 0: break

    print('Done Mapping!')
else:
    print('Already Satisfied mapping videos to new playlist id!')


############################################################
# create a file to continue working from last inserted video
print('Start Inserting Videos...')
openMode = 'w'

if os.path.exists('./data/videos_inserted.csv'):
    openMode = 'a'

    # get the last line in the already inserted playlists
    with open('./data/videos_inserted.csv', 'r', encoding='utf-8') as videos_inserted_CSV:
        csv_reader = csv.reader(videos_inserted_CSV)
        # get last inserted video
        for inserted_video in csv_reader: pass

with open('./data/videos_inserted.csv', openMode, encoding='utf-8', newline='') as videos_inserted_CSV:
    csv_writer = csv.writer(videos_inserted_CSV, quoting=csv.QUOTE_NONNUMERIC)

    # get last playlists not inserted to continue inserting
    with open('./data/videos_edited.csv', 'r', encoding='utf-8') as edited_videos_CSV:
        csv_reader = csv.reader(edited_videos_CSV)

        if openMode == 'w' or inserted_video == ['playlist_name','playlist_id','video_id']:
            # no need for headers when already new playlists is created
            csv_writer.writerow(['playlist_name','playlist_id','video_id'])
        else:
            # match both csv reader to the same video
            for video in csv_reader:
                if video == inserted_video: break

        # some videos are not available any more
        count_insert_error = 0

        exception_triggered = False

        for video in csv_reader:
            try:
                playlis_new_response = youtube_target.playlistItems().insert(
                    part='snippet',
                    body={
                        'snippet':{
                            'playlistId':video[1],
                            'resourceId':{
                                'kind': 'youtube#video',
                                'videoId':video[2]
                            }
                        }
                    }
                ).execute()

            except googleapiclient.errors.HttpError as e:
                exception_triggered = True
                print('\nError:')
                # handeling quota error
                if e.status_code == 403:
                    print('Unfortunately, Not all videos were inserted, the Quota is reached for today.')
                    print('Please try tomorrow.')
                    print('This script will automatically restart from the last inserted video.')
                # handeling inserting video error
                elif e.status_code == 404:
                    exception_triggered = False
                    count_insert_error += 1
                    print('Error Response: ', e.reason)
                    print(video[0], video[2])
                    continue

                else:
                    print('Error Code:',e.status_code)
                    print('Error Response: ', e.reason)

                break

            csv_writer.writerow(video)

    if not exception_triggered:
        print('Done Inserting Videos!')
        print(f'Error Inserting videos: {count_insert_error} due to not finding the video')