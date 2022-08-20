import requests
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError

class HttpUtil:
    def check_connectivity():
        urls = [constants.SPOTIFY_API_URL, constants.YOUTUBE_API_URL]
        for url in urls:
            is_url_available = HttpUtil._check_url(url)
            if not is_url_available:
                raise ConfigurationError("Failed to connect to %s, are you online?" % url)


    def _check_url(url):
        try:
            requests.head(url)
        except requests.ConnectionError:
            return False
        return True