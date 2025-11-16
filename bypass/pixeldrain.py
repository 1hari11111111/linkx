
import re
import requests

def pixeldrain_bypass(url):
    try:
        file_id = re.findall(r"/u/([A-Za-z0-9]+)", url)[0]
        return f"https://pixeldrain.com/api/file/{file_id}"
    except:
        return None
