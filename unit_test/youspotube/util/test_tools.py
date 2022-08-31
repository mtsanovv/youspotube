import unittest

from youspotube.util.tools import Tools


class ToolsTest(unittest.TestCase):
    def test_Tools_convert_string_time_to_seconds(self):
        expected_seconds = 86700  # one day (86400) + 5 minutes (300 seconds)
        time_string = '24:05:00'

        self.assertEqual(Tools.time_to_seconds(time_string), expected_seconds)

    def test_Tools_single_artist_get_non_beautiful_track_string(self):
        artist = 'Test'
        title = 'A Love To Unit Test'
        expected_track_string = "%s %s" % (artist, title)

        self.assertEqual(Tools.get_track_string(title, [artist]), expected_track_string)

    def test_Tools_multiple_artists_get_non_beautiful_track_string(self):
        artist1 = 'Test'
        artist2 = 'Tester'
        title = 'A Love To Unit Test'
        expected_track_string = "%s %s %s" % (artist1, artist2, title)

        self.assertEqual(Tools.get_track_string(title, [artist1, artist2]), expected_track_string)

    def test_Tools_single_artist_get_beautiful_track_string(self):
        artist = 'Test'
        title = 'A Love To Unit Test'
        expected_track_string = "%s - %s" % (artist, title)

        self.assertEqual(Tools.get_track_string(title, [artist], True), expected_track_string)

    def test_Tools_multiple_artists_get_beautiful_track_string(self):
        artist1 = 'Test'
        artist2 = 'Tester'
        title = 'A Love To Unit Test'
        expected_track_string = "%s, %s - %s" % (artist1, artist2, title)

        self.assertEqual(Tools.get_track_string(title, [artist1, artist2], True), expected_track_string)
