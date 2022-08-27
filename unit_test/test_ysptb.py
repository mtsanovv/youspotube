import unittest
from unittest import mock


@mock.patch("youspotube.util.bootstrapper.Bootstrap")
class YsptbTest(unittest.TestCase):
    def test_ysptb(self, bootstrap_mock):
        import ysptb
        self.assertIs(ysptb, ysptb)   # just because the linter considers ysptb as unused...
        bootstrap_mock.assert_called_once()
