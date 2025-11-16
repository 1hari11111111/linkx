
import requests
from bs4 import BeautifulSoup

def direct_bypass(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return None
