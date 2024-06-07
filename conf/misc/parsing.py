import urllib.parse


def extract_weights_from_url(url):
    """
    Extract weights from the Spotify recommendations URL.

    :param url: URL string from the Spotify recommendations API.
    :return: Dictionary of weights.
    """
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    weights = {key: float(value[0]) for key, value in query_params.items() if key.startswith('target_')}
    return weights
