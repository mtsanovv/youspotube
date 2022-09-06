import unittest
from unittest import mock

from youspotube.util.tools import Tools
import os
import sys

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

    @mock.patch.object(Tools, 'getcwd')
    def test_Tools_get_filepath_relative_to_ysptb(self, getcwd_mock):
        getcwd_mock.return_value = os.getcwd()
        filepath = os.path.join('path', 'to', 'file')
        expected_fullpath = os.path.join(getcwd_mock.return_value, filepath)

        return_value = Tools.get_filepath_relative_to_ysptb(filepath)

        self.assertEqual(return_value, expected_fullpath)

    @mock.patch('youspotube.util.tools.sys')
    def test_Tools_getcwd_in_exe_bundle(self, sys_mock):
        sys_mock.frozen = True
        exe_path = os.path.join('.', 'ysptb')
        sys_mock.argv = [exe_path]
        expected_cwd = os.path.abspath(os.path.dirname(exe_path))

        return_value = Tools.getcwd()

        self.assertEqual(return_value, expected_cwd)

    @mock.patch('youspotube.util.tools.sys')
    def test_Tools_getcwd_in_python_script(self, sys_mock):
        sys_mock.frozen = False
        expected_cwd = os.getcwd()

        return_value = Tools.getcwd()

        self.assertEqual(return_value, expected_cwd)
