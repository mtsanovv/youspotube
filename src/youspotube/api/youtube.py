import logging
import time
import httplib2
import oauth2client
from oauth2client import tools, file
from googleapiclient.discovery import build
from youspotube.exceptions import ConfigurationError
from youtubesearchpython import VideosSearch
import youspotube.constants as constants
from youspotube.util.tools import Tools


class YouTube:
    def __init__(self, client_id, client_secret):
        try:
            self._init_connection(client_id, client_secret)
            self._test_connection()
        except Exception as e:
            raise ConfigurationError("Test connection to YouTube API failed: %s" % str(e))

    def _init_connection(self, client_id, client_secret):
        storage = file.Storage(constants.YOUTUBE_TOKEN_STORAGE_FILE)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flow = oauth2client.client.OAuth2WebServerFlow(
                client_id=client_id,
                client_secret=client_secret,
                scope=constants.YOUTUBE_SCOPE
            )
            credentials = tools.run_flow(flow, storage)
        http = httplib2.Http()
        http = credentials.authorize(http)

        self.connection = build('youtube', 'v3', http=http, static_discovery=False, cache_discovery=False)

    def _test_connection(self):
        request = self.connection.channels().list(
            part="snippet,contentDetails,statistics",
            id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
        )
        request.execute()

    def spotify_playlist_to_video_ids(self, spotify_playlist):
        video_ids = []
        for track_id in spotify_playlist:
            track = spotify_playlist[track_id]
            video_id = self._lookup_spotify_track_on_youtube(track, track_id)
            if video_id is None:
                continue
            video_ids.append(video_id)
        return video_ids

    def _lookup_spotify_track_on_youtube(self, track, track_id, search_limit=constants.INITIAL_SEARCH_LIMIT):
        # TODO: tied songs - no need to lookup anything if this turns out to be a tied song
        track_name = track['name']
        track_artists = track['artists']
        track_duration_s = track['duration_ms'] // 1000
        track_beautiful = ' - '.join([
            ', '.join(track_artists),
            track_name
        ])
        track_lookup_string = ' '.join([
            ' '.join(track_artists),
            track_name
        ])
        logging.info("Looking for a relevant YouTube video for: %s" % track_beautiful)
        logging.debug("YouTube search query: %s" % track_lookup_string)

        videos_result = VideosSearch(track_lookup_string, limit=search_limit).result()['result']
        videos = []

        # in order to produce more accurate results, choose the video that has the smallest duration delta compared to the Spotify # noqa: E501
        # this is probably one of the best ways to mitigate duration issues similar to Taylor Swift's I Knew You Were Trouble # noqa: E501
        # should this prove to be misleading, one could probably switch back to getting the top result... after all, AI knows best # noqa: E501
        for video_data in videos_result:
            video_id = video_data['id']
            video_duration = video_data['duration']
            video_duration_s = Tools.time_to_seconds(video_duration)
            duration_delta = abs(track_duration_s - video_duration_s)
            if duration_delta > constants.MAX_YOUTUBE_SPOTIFY_DURATION_DELTA_SECONDS:
                # in order to further eliminate irrelevant results
                continue
            videos.append({
                constants.YOUTUBE_SPOTIFY_DURATION_DELTA_DATA_KEY: abs(track_duration_s - video_duration_s),
                constants.YOUTUBE_VIDEO_ID_DATA_KEY: video_id
            })

        if not videos and search_limit == 3:
            logging.warning(
                "Could not find a relevant video in the top %s earch results for: %s, checking the top %s results" % (
                    constants.INITIAL_SEARCH_LIMIT,
                    track_beautiful,
                    constants.EXTENDED_SEARCH_LIMIT
                )
            )
            return self._lookup_spotify_track_on_youtube(track, track_id, constants.EXTENDED_SEARCH_LIMIT)

        if not videos:
            logging.warning("Could not find any relevant results for %s, song cannot be synchronized" % track_beautiful)
            return None

        videos.sort(key=lambda x: x[constants.YOUTUBE_SPOTIFY_DURATION_DELTA_DATA_KEY])
        best_match_video = videos[0][constants.YOUTUBE_VIDEO_ID_DATA_KEY]
        return best_match_video

    def add_videos_to_playlist(self, playlist_details, video_ids):
        logging.info("Pushing %s videos to YouTube playlist..." % len(video_ids))
        id = playlist_details[constants.ORIGIN_YOUTUBE]
        for video_id_index, video_id in enumerate(video_ids):
            request = self.connection.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": id,
                        "position": video_id_index,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            request.execute()
            time.sleep(3)
