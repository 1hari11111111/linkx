
import requests

def universal_bypass(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=12)
        return r.url
    except:
        return None
