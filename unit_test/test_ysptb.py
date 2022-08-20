import unittest
from unittest import mock

@mock.patch("youspotube.util.bootstrapper.Bootstrap")
class YsptbTest(unittest.TestCase):
    def test_ysptb_call_bootstrap(self, bootstrap_mock):
        import ysptb
        bootstrap_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()