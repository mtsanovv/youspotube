import unittest
from unittest import mock

@mock.patch("youspotube.util.bootstrapper.Bootstrap")
class YsptbTest(unittest.TestCase):
    def test_bootstrap_youspotube(self, bootstrap_mock):
        import src.ysptb
        bootstrap_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()