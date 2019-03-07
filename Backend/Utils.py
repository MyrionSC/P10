import urllib.parse


def url_ascii_encode(url):
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    return urllib.parse.urlunsplit(url)
