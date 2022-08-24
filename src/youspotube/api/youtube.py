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
    def __init__(self, api_key):
        try:
            self._init_connection(api_key)
            self._test_connection()
        except Exception as e:
            raise ConfigurationError("Test connection to YouTube API failed: %s" % str(e))

    def _init_connection(self, api_key):
        storage = oauth2client.file.Storage('.youtube_cache')
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flow = oauth2client.client.OAuth2WebServerFlow(
                client_id='73235194424-dleq85ngloegmij0t9nelne6qt4ng6da.apps.googleusercontent.com',
                scope='https://www.googleapis.com/auth/youtube',
                client_secret='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',
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

    def _lookup_spotify_track_on_youtube(self, track, track_id, search_limit=3):
        # TODO: tied songs - no need to lookup anything if this turns out to be a tied song
        track_name = track['name']
        track_artists = track['artists']
        track_duration_s = track['duration_ms'] // 1000
        track_beautiful = "%s - %s" % (
            ', '.join(track_artists),
            track_name
        )
        track_lookup_string = ' '.join([
            ' '.join(track_artists),
            track_name
        ])
        logging.info("Synchronizing: %s" % track_beautiful)
        logging.debug("YouTube search query: %s" % track_lookup_string)

        videos_result = VideosSearch(track_lookup_string, limit=search_limit).result()['result']
        videos = []

        # in order to produce more accurate results, choose the video that has the smallest duration delta compared to the Spotify
        # this is probably one of the best ways to mitigate duration issues similar to Taylor Swift's I Knew You Were Trouble
        # should this prove to be misleading, one could probably switch back to getting the top result... after all, AI knows best
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
            return self._lookup_spotify_track_on_youtube(track, track_id, 7)

        if not videos:
            logging.warning("Could not find any relevant results for %s, song cannot be synchronized" % track_beautiful)
            return None

        videos.sort(key=lambda x: x[constants.YOUTUBE_SPOTIFY_DURATION_DELTA_DATA_KEY])
        best_match_video = videos[0][constants.YOUTUBE_VIDEO_ID_DATA_KEY]
        return best_match_video

    def add_videos_to_playlist(self, playlist_details, video_ids):
        id = playlist_details[constants.ORIGIN_YOUTUBE]
        step = 50 # seems like youtube api allows only 50 videos to be pushed in batch at a time
        for i in range(0, len(video_ids), step):
            self._send_batch_playlist_items_insert(id, video_ids[i:i+step], i)

    def _send_batch_playlist_items_insert(self, playlist_id, items, offset):
        logging.info("Pushing %s videos to the YouTube playlist..." % len(items))
        batch = self.connection.new_batch_http_request()
        for video_index, video_id in enumerate(items):
            batch.add(
                self.connection.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "position": offset + video_index,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                )
            )
        batch.execute()
        time.sleep(2)
