from urllib.parse import urljoin

import requests


class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def search(self, search_content, search_mode):
        json = {
            "search_content": search_content,
            "search_mode": search_mode
        }
        r = requests.post(self.url_prefix, json=json)
        return r.content, r.status_code
