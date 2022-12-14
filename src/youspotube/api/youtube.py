import logging
import time
import os
import pickle
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youspotube.api.base import BaseAPI
from youtubesearchpython import CustomSearch, VideoSortOrder
import youspotube.constants as constants
from youspotube.util.tools import Tools


class YouTube(BaseAPI):
    @property
    def connection(self):
        # _init_connection should have been called in order to be able to use this property
        credentials = self._get_credentials()
        if credentials.expired:
            self._init_connection(credentials)
        return self.youtube

    def _init_connection(self, credentials=None):
        if credentials is None:
            credentials = self._get_credentials()

        if credentials.expired:
            credentials.refresh(Request())
            self._save_credentials(credentials)

        self.youtube = build('youtube', 'v3', credentials=credentials, static_discovery=False, cache_discovery=False)

    def _get_credentials(self):
        token_storage_file_path = Tools.get_filepath_relative_to_ysptb(constants.YOUTUBE_TOKEN_STORAGE_FILE)

        if not os.path.exists(token_storage_file_path):
            flow = InstalledAppFlow.from_client_config(
                client_config={
                   "installed": {
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://accounts.google.com/o/oauth2/token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                },
                scopes=[constants.YOUTUBE_SCOPE]
            )
            credentials = flow.run_local_server(port=4467)

            self._save_credentials(credentials)
        else:
            with open(token_storage_file_path, 'rb') as credentials_file:
                credentials = pickle.load(credentials_file)

        return credentials

    def _save_credentials(self, credentials):
        token_storage_file_path = Tools.get_filepath_relative_to_ysptb(constants.YOUTUBE_TOKEN_STORAGE_FILE)
        with open(token_storage_file_path, 'wb') as credentials_file:
            pickle.dump(credentials, credentials_file)

    def _test_connection(self):
        request = self.connection.channels().list(
            part="snippet,contentDetails,statistics",
            id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
        )

        request.execute()

    def spotify_playlist_to_video_ids(self, spotify_playlist):
        video_ids = []

        track_position = 0
        for track_id in spotify_playlist:
            track = spotify_playlist[track_id]

            video_id, search_results = self._lookup_spotify_track_on_youtube(track, track_id)

            if video_id is None:
                continue

            video_ids.append({
                constants.YOUTUBE_VIDEO_ID_DATA_KEY: video_id,
                constants.SEARCH_RESULTS_DATA_KEY: search_results,
                constants.TRACK_POSITION_DATA_KEY: track_position
            })

            track_position += 1

        return video_ids

    def _lookup_spotify_track_on_youtube(self, track, track_id, search_limit=constants.INITIAL_SEARCH_LIMIT):
        track_name = track['name']
        track_artists = track['artists']
        track_duration_s = track['duration_ms'] // 1000
        track_beautiful = Tools.get_track_string(track_name, track_artists, True)
        track_lookup_string = Tools.get_track_string(track_name, track_artists)

        tied_video_id_to_track_id = self._get_tied_video_id_to_track_id(track_id)
        if tied_video_id_to_track_id is not None:
            logging.debug(
                "Using tied video ID '%s' to track '%s' instead of looking it up on YouTube" % (
                    tied_video_id_to_track_id,
                    track_beautiful
                )
            )
            return tied_video_id_to_track_id, None

        logging.debug("YouTube search query: %s" % track_lookup_string)

        videos_result = CustomSearch(
            track_lookup_string,
            VideoSortOrder.relevance,
            search_limit
        ).result()['result']
        videos = self._get_relevant_videos_from_search_result(track_duration_s, videos_result, search_limit)

        # in order to produce more accurate results, choose the video that has the smallest duration delta compared to the Spotify # noqa: E501
        # this is probably one of the best ways to mitigate duration issues similar to Taylor Swift's I Knew You Were Trouble # noqa: E501
        # should this prove to be misleading, one could probably switch back to getting the top result... after all, AI knows best # noqa: E501

        if not videos and search_limit == constants.INITIAL_SEARCH_LIMIT:
            logging.debug(
                "Could not find a relevant video in the top %s YouTube search results for: %s, checking the top %s results" % (
                    constants.INITIAL_SEARCH_LIMIT,
                    track_beautiful,
                    constants.EXTENDED_SEARCH_LIMIT
                )
            )
            return self._lookup_spotify_track_on_youtube(track, track_id, constants.EXTENDED_SEARCH_LIMIT)

        if not videos:
            logging.warning(
                "Could not find a relevant video in the top %s YouTube search results for: %s, song cannot be synchronized" % (
                    constants.EXTENDED_SEARCH_LIMIT,
                    track_beautiful
                )
            )
            return None, videos_result

        videos.sort(key=lambda x: x[constants.YOUTUBE_SPOTIFY_DURATION_DELTA_DATA_KEY])
        best_match_video = videos[0][constants.YOUTUBE_VIDEO_ID_DATA_KEY]

        return best_match_video, videos_result

    def _get_relevant_videos_from_search_result(self, required_video_duration, search_result, search_limit):
        relevant_videos = []

        for video_index, video_data in enumerate(search_result):
            if video_index == search_limit:
                break

            video_id = video_data['id']
            video_duration = video_data['duration']
            video_duration_s = Tools.time_to_seconds(video_duration)
            duration_delta = abs(required_video_duration - video_duration_s)

            if duration_delta > constants.MAX_YOUTUBE_SPOTIFY_DURATION_DELTA_SECONDS:
                continue

            relevant_videos.append({
                constants.YOUTUBE_SPOTIFY_DURATION_DELTA_DATA_KEY: abs(required_video_duration - video_duration_s),
                constants.YOUTUBE_VIDEO_ID_DATA_KEY: video_id
            })

        return relevant_videos

    def _get_tied_video_id_to_track_id(self, track_id):
        for tie_name in self.tied_songs:
            tie = self.tied_songs[tie_name]
            if track_id == tie[constants.ORIGIN_SPOTIFY]:
                return tie[constants.ORIGIN_YOUTUBE]

        return None

    def add_videos_to_playlist(self, playlist_details, videos):
        playlist_id = playlist_details[constants.ORIGIN_YOUTUBE]

        for video_data in videos:
            playlist_length = len(self._get_playlist_items(playlist_id))
            video_id = video_data[constants.YOUTUBE_VIDEO_ID_DATA_KEY]
            request_body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "position": video_data[constants.TRACK_POSITION_DATA_KEY],
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            if video_data[constants.TRACK_POSITION_DATA_KEY] > playlist_length - 1:
                # remove the position property when it is not in the playlist range
                # that's done in order to prevent invalid arguments due to invalid positions
                request_body['snippet'].pop('position')

            logging.debug("Pushing video ID '%s' to YouTube playlist '%s'" % (video_id, playlist_id))

            request = self.connection.playlistItems().insert(
                part="snippet",
                body=request_body
            )

            should_stop_iterating_over_videos = False
            retried_once = False
            while True:
                response = None
                try:
                    time.sleep(constants.SLEEP_BETWEEN_PLAYLIST_PUSHES)
                    response = request.execute()
                    break
                except HttpError as httperr:
                    if not retried_once and httperr.resp.status in [400, 500, 503]:
                        # in case of a connection error, retry
                        retried_once = True
                        continue
                    logging.warning(
                        "An error has occurred while pushing video ID '%s' to YouTube playlist '%s'" % (
                            video_id,
                            playlist_id
                        )
                    )
                    logging.debug(
                        "An error has occurred while pushing video ID '%s' to YouTube playlist '%s': %s" % (
                            video_id,
                            playlist_id,
                            str(httperr)
                        )
                    )
                    logging.debug("Request was: %s" % request_body)
                    logging.debug("Response was: %s" % response)
                    should_stop_iterating_over_videos = True
                    break

            if should_stop_iterating_over_videos:
                break

    def get_missing_videos_in_playlist(self, playlist_details, all_videos):
        playlist_id = playlist_details[constants.ORIGIN_YOUTUBE]
        playlist_items = self._get_playlist_items(playlist_id)

        all_missing_videos = []

        for video_data in all_videos:
            video_id = video_data[constants.YOUTUBE_VIDEO_ID_DATA_KEY]
            is_video_missing = True
            for video_details in playlist_items:
                if video_details['contentDetails']['videoId'] == video_id:
                    is_video_missing = False
                    break

            if is_video_missing:
                all_missing_videos.append(video_data)

        actual_missing_video_ids = self._find_actually_missing_videos(all_missing_videos, playlist_items)

        return actual_missing_video_ids

    def _get_playlist_items(self, playlist_id):
        desired_parts = 'snippet,contentDetails'
        max_results = 50

        partial_youtube_playlist = self.connection.playlistItems().list(
            part=desired_parts,
            playlistId=playlist_id,
            maxResults=max_results
        ).execute()

        playlist_items = partial_youtube_playlist['items']

        next_page_token = partial_youtube_playlist.get('nextPageToken')
        while ('nextPageToken' in partial_youtube_playlist):
            next_page = self.connection.playlistItems().list(
                part=desired_parts,
                playlistId=playlist_id,
                maxResults=max_results,
                pageToken=next_page_token
            ).execute()
            playlist_items.extend(next_page['items'])

            if 'nextPageToken' not in next_page:
                partial_youtube_playlist.pop('nextPageToken', None)
            else:
                next_page_token = next_page['nextPageToken']

        return playlist_items

    def _find_actually_missing_videos(self, all_missing_videos, playlist_items):
        playlist_video_titles = self._get_video_titles_from_youtube_playlist(playlist_items)

        actually_missing_videos = []

        for video_data in all_missing_videos:
            search_results = video_data[constants.SEARCH_RESULTS_DATA_KEY]
            # a video without search_results is a tied video
            # since they're manually entered by the user no search results will be accurate
            if search_results is not None:
                search_results_video_titles = self._get_video_titles_from_videos_search_result(search_results)

                title_found_in_search_results = False
                for playlist_video_title in playlist_video_titles:
                    if playlist_video_title in search_results_video_titles:
                        title_found_in_search_results = True
                        break

            if search_results is None or not title_found_in_search_results:
                actually_missing_videos.append(video_data)

        return actually_missing_videos

    def _get_video_titles_from_videos_search_result(self, videos_result):
        video_titles = []

        for video_data in videos_result:
            video_titles.append(video_data['title'])

        return video_titles

    def _get_video_titles_from_youtube_playlist(self, playlist_items):
        video_titles = []

        for video_data in playlist_items:
            video_titles.append(video_data['snippet']['title'])

        return video_titles

    def parse_playlist(self, playlist_details):
        playlist_id = playlist_details[constants.ORIGIN_YOUTUBE]
        playlist_items = self._get_playlist_items(playlist_id)

        playlist = {}

        for video_data in playlist_items:
            video_id = video_data['contentDetails']['videoId']
            video_title = video_data['snippet']['title']
            playlist[video_id] = {
                'title': video_title
            }

        return playlist

    def get_relevant_spotify_tracks(self, all_tracks):
        relevant_tracks = []

        for track in all_tracks:
            track_query = track[constants.SPOTIFY_TRACK_TITLE_ARTISTS_DATA_KEY]
            origin_video_id = track[constants.YOUTUBE_VIDEO_ID_DATA_KEY]

            if track_query is None:
                # a track without a YouTube search query is a tied track
                # since they're manually entered by the user no search results will be accurate
                relevant_tracks.append(track)
                continue

            video_results = CustomSearch(
                track_query,
                VideoSortOrder.relevance,
                constants.YOUTUBE_SEARCH_LIMIT
            ).result()['result']

            origin_video_found = False
            for video_data in video_results:
                video_id = video_data['id']
                if video_id == origin_video_id:
                    relevant_tracks.append(track)
                    origin_video_found = True
                    break

            if not origin_video_found:
                logging.warning("Could not find a relevant track on YouTube for: %s, song cannot be synchronized" % (
                        track[constants.YOUTUBE_VIDEO_TITLE_DATA_KEY]
                    )
                )

        return relevant_tracks
