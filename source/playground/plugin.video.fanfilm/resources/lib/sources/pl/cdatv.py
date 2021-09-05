# -*- coding: utf-8 -*-

'''
    Covenant Add-on
    Copyright (C) 2017 homik

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

import urllib

try:
    import urllib.parse as urllib
except:
    pass

from ptw.libraries import cleantitle
from ptw.libraries import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['cda-tv.pl']

        self.base_link = 'https://cda-tv.pl/'
        self.search_link = '/?s=%s'

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def do_search(self, title, local_title, year):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(local_title)))

            for title in titles:
                try:
                    url = urllib.urljoin(self.base_link, self.search_link)
                    url = url % urllib.quote_plus(cleantitle.query(title))
                    result = client.request(url)
                    result = client.parseDOM(result, 'div', attrs={
                        'class': 'result-item'})
                    for row in result:
                        name = client.parseDOM(row, 'img', ret='alt')[0]
                        words = title.split(' ')
                        if self.contains_all_words(name, words) and str(year) in row:
                            url = client.parseDOM(row, 'a', ret='href')[0]
                            return url
                except:
                    continue
        except:
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.do_search(title, localtitle, year)

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None:
                return sources
            result = client.request(url)
            result1 = client.parseDOM(result, 'li', ret='data-post')
            result3 = client.parseDOM(result, 'li', ret='data-nume')
            result2 = client.parseDOM(result, 'li', attrs={
                'class': 'dooplay_player_option'})
            if not result2:
                result2 = client.parseDOM(result, 'li', attrs={
                    'class': 'dooplay_player_option jump'})
            for item in zip(result1, result2, result3):
                try:
                    jezyk = client.parseDOM(item[1], 'span')[0]
                    jezyk, info = self.get_lang_by_type(jezyk)
                    host = client.parseDOM(item[1], 'span')[1]
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': jezyk,
                        'url': str(item[0] + ";" + item[2]),
                        'info': info,
                        'direct': False,
                        'debridonly': False})
                except:
                    continue
            return sources

        except:
            return sources

    def get_lang_by_type(self, lang_type):
        if "dubbing" in lang_type.lower():
            if "kino" in lang_type.lower():
                return 'pl', 'Dubbing Kino'
            return 'pl', 'Dubbing'
        elif 'lektor pl' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'lektor' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'napisy pl' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'napisy' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'POLSKI' in lang_type.lower():
            return 'pl', None
        elif 'pl' in lang_type.lower():
            return 'pl', None
        return 'en', None

    def resolve(self, url):
        url = url.split(";")
        import requests
        data = {
            'action': 'doo_player_ajax',
            'post': url[0],
            'nume': url[1],
            'type': 'movie'}

        response = requests.post('https://cda-tv.pl/wp-admin/admin-ajax.php', data=data).text
        url = client.parseDOM(response, 'iframe', ret='src')[0]

        return url
