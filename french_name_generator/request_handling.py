#!python3
"""Methods to handle http or APIs."""
import requests


def html_fr_source(url):
    """Get an HTML object from the source url."""
    r = requests.get(url)
    return r.text
