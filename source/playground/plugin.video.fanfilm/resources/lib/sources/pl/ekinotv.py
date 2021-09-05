# -*- coding: utf-8 -*-

'''
    FanFilm Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import re

try:
    import urlparse
except:
    import urllib.parse as urlparse

from ptw.debug import log
from ptw.libraries import cleantitle
from ptw.libraries import client, cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['ekino-tv.pl']

        self.base_link = 'https://ekino-tv.pl'
        self.search_link = '/search/qf/?q='
        self.resolve_link = '/watch/f/%s/%s'
        self.anime = False

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        if self.anime:
            words_to_check = str_to_check.split(" ")
            for word in words_to_check:
                try:
                    liczba = int(word)
                    for word2 in words:
                        try:
                            liczba2 = int(word2)
                            if liczba != liczba2 and liczba2 != self.year and liczba != self.year:
                                return False
                        except:
                            continue
                except:
                    continue
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def search(self, title, localtitle, year, search_type):
        try:
            url = self.do_search(cleantitle.query(title), title, localtitle, year, search_type)
            if not url:
                url = self.do_search(cleantitle.query(localtitle), title, localtitle, year, search_type)
            return url
        except:
            return

    def do_search(self, search_string, title, localtitle, year, search_type):
        cookies = client.request(self.base_link, output='cookie')
        cache.cache_insert('ekino_cookie', cookies)
        titles = []
        titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
        titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))

        for title in titles:
            try:
                r = client.request("https://ekino-tv.pl/search/qf/?q=%s" % str.lower(title + " HD").replace(" ", "%20"), headers={
                    'Cookie': cookies})
                r = client.parseDOM(r, 'div', attrs={
                    'class': 'movies-list-item'})
                for row in r:
                    # row = client.parseDOM(row, 'div', attrs={
                    #     'class': 'movieDesc'})[0]
                    title_found = client.parseDOM(row, 'a')[1]
                    link = client.parseDOM(row, 'a', ret='href')[0]
                    if not search_type in link:
                        continue

                    title_found = title_found.replace('&nbsp;', '')
                    words = title.split(" ")
                    if self.contains_all_words(title_found, words) and year in link:
                        return link
            except Exception as e:
                continue

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, '/movie/')

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.search(tvshowtitle, localtvshowtitle, year, '/serie/')

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        cookies = client.request(self.base_link, output='cookie')
        cache.cache_insert('ekino_cookie', cookies)

        url = urlparse.urljoin(self.base_link, url)
        r = client.request(url, headers={
            'Cookie': cookies})
        r = client.parseDOM(r, 'div', attrs={
            'id': 'list-series'})[0]
        p = client.parseDOM(r, 'p')
        index = p.index('Sezon ' + season)
        r = client.parseDOM(r, 'ul')[index]
        r = client.parseDOM(r, 'li')
        for row in r:
            ep_no = client.parseDOM(row, 'div')[0]
            if ep_no == episode:
                return client.parseDOM(row, 'a', ret='href')[0]
        return None

    def get_lang_by_type(self, lang_type):
        if lang_type:
            lang_type = lang_type[0]
            if 'Lektor' in lang_type:
                return 'pl', 'Lektor'
            if 'Dubbing' in lang_type:
                return 'pl', 'Dubbing'
            if 'Napisy' in lang_type:
                return 'pl', 'Napisy'
            if 'PL' in lang_type:
                return 'pl', None
        return 'en', None

    def sources(self, url, hostDict, hostprDict):
        sources = []
        cookies = cache.cache_get('ekino_cookie')['value']
        try:
            if url == None:
                return sources
            r = client.request(urlparse.urljoin(self.base_link, url), redirect=False, headers={
                'Cookie': cookies})
            rows = client.parseDOM(r, 'ul', attrs={
                'class': 'players'})[0]
            rows = client.parseDOM(rows, 'li')
            rows.pop()
            rows2 = client.parseDOM(r, 'div', attrs={
                'role': 'tabpanel'})

            for i in range(len(rows)):
                try:
                    row = rows[i]
                    row2 = rows2[i]
                    link = client.parseDOM(row2, 'a', ret='onClick')[0]
                    data = client.parseDOM(row, 'a')[0]
                    qual = client.parseDOM(row, 'img ', ret='title')
                    lang_type = client.parseDOM(row, 'i ', ret='title')
                    q = 'SD'
                    if qual and 'Wysoka' in qual[0]:
                        q = 'HD'
                    lang, info = self.get_lang_by_type(lang_type)
                    host = data.splitlines()[0].strip()
                    sources.append({
                        'source': host,
                        'quality': q,
                        'language': lang,
                        'url': link,
                        'info': info,
                        'direct': False,
                        'debridonly': False})
                except:
                    continue
            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            cookies = cache.cache_get('ekino_cookie')['value']
            splitted = url.split("'")
            host = splitted[1]
            video_id = splitted[3]
            transl_url = urlparse.urljoin(self.base_link, self.resolve_link) % (host, video_id)
            result = client.request(transl_url, redirect=False, headers={
                'Cookie': cookies + "; prch=true"})
            streams = re.findall('href="([^"]+)"\s*target=".+?"\s*class=".+?"',result,re.DOTALL)[0]
            return streams
        except:
            return None
