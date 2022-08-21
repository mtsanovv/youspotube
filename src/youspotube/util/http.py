import requests
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError


class HttpUtil:
    def check_connectivity():
        urls = [constants.SPOTIFY_API_URL, constants.YOUTUBE_API_URL]
        for url in urls:
            try:
                HttpUtil._check_url(url)
            except Exception as e:
                raise ConfigurationError("Failed to connect to %s: %s" % (url, str(e)))

    def _check_url(url):
        requests.head(url)
