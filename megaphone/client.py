import requests
from yarl import URL

BASE_URL = "https://cms.megaphone.fm/api/networks"

class APIError(Exception):
    """
    Any issue with the API.
    """


class AuthenticationError(Exception):
    """
    Error authenticating
    """


class HTTPClient:
    def __init__(self, token, base_url):
        self.base_url = base_url
        self.token = token
        self.headers = { 'Authorization': 'Token token="%s"' % token }
        
    def get(self, *parts, **args):
        url = self.base_url
        for part in parts:
            url = url / part
        url = url.with_query(per_page=5)
        r = requests.get(str(url), headers=self.headers)
        print(r.links["next"])
        if r.status_code == 401:
            raise AuthenticationError(r.text)
        elif r.status_code != 200:
            raise APIError(r.text)
        return r.json()

    def __truediv__(self, path):
        return HTTPClient(self.token, self.base_url / path)


class APIObject:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        return self.data[name]

    def __str__(self):
        attrs = ["%s=%s" % (k,v) for k, v in self.data.items()]
        attrs = ", ".join(attrs)
        return "<%s %s>" % (self.__class__.__name__, attrs)


class Episode(APIObject):
    def __init__(self, http, data):
        super().__init__(data)
        self.http = http / 'episodes' / data['id']


class Podcast(APIObject):
    def __init__(self, http, data):
        super().__init__(data)        
        self.http = http / 'podcasts' / data['id']

    @property
    def episodes(self):
        episodes = self.http.get('episodes')
        return [Episode(self.http, e) for e in episodes]


class NetworkClient:
    def __init__(self, token, network_id):
        self.network_id = network_id
        base_url = URL(BASE_URL) / self.network_id
        self.http = HTTPClient(token, base_url)        

    @property
    def podcasts(self):
        podcasts = self.http.get('podcasts')
        return [Podcast(self.http, p) for p in podcasts]



nc = NetworkClient()
es = nc.podcasts
#for podcast in nc.podcasts:
#    es = podcast.episodes
#for podcast in nc.podcasts:
#    print(podcast.title)
#for episode in podcast.episodes:
        
