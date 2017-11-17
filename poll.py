#! /usr/bin/env python3

import glob
import json
import os
import re
import sys
import urllib.parse
import urllib.request

class LastFmApi:
    API_ROOT = 'http://ws.audioscrobbler.com/2.0/'

    PERIOD_OVERALL = 'overall'
    PERIOD_7_DAYS = '7day'
    PERIOD_1_MONTHS = '1month'
    PERIOD_3_MONTHS = '3month'
    PERIOD_6_MONTHS = '6month'
    PERIOD_12_MONTHS = '12month'

    def __init__(self, api_key):
        self._api_key = api_key

    def _call(self, method, **kwargs):
        params = {'method': method, 'format': 'json', 'api_key': self._api_key}
        params.update(kwargs)
        query = urllib.parse.urlencode(params)
        request = urllib.request.urlopen('%s?%s' % (LastFmApi.API_ROOT, query))
        return json.loads(request.read())

    def userGetTopAlbums(self, user, period=PERIOD_OVERALL, limit=50, page=1):
        return self._call('user.gettopalbums', user=user, period=period, limit=limit, page=page)

def usage(error=None):
    if error is not None:
        print('Error: %s' % error)
    print('Usage: LASTFM_API_KEY=... python3 %s lastfm-user' % sys.argv[0])
    sys.exit(1 if error is not None else 0)

if __name__ == '__main__':
    if len(sys.argv) > 1 and re.match(r'--?h(elp)?', sys.argv[1]):
        usage()

    if len(sys.argv) < 2:
        usage('no Last.fm username given!')

    if 'LASTFM_API_KEY' not in os.environ:
        usage('Last.fm API key must be given via the "LASTFM_API_KEY" environment variable!')

    lastfm_api_key = os.environ['LASTFM_API_KEY']
    username = sys.argv[1]

    api = LastFmApi(lastfm_api_key)

    albums = set()
    for period, limit in ((LastFmApi.PERIOD_OVERALL, 25),
                          (LastFmApi.PERIOD_3_MONTHS, 50),
                          (LastFmApi.PERIOD_1_MONTHS, 250),
                          (LastFmApi.PERIOD_7_DAYS, 100)):
        for album in api.userGetTopAlbums(username, period=period, limit=limit)['topalbums']['album']:
            artist_name = album['artist']['name']
            album_name = album['name']

            # Any “feat.” or “with” in the name is almost certainly the track
            # artist, not the album artist.
            artist_name = re.sub(r' (feat\.|with) .*', '', artist_name, flags=re.IGNORECASE)

            albums.add((artist_name, album_name))

    for album in sorted(list(albums), key=lambda album: (album[0].lower(), album[1].lower())):
        print('%s - %s' % album)
