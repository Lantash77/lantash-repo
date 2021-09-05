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

try:
    import urlparse
except:
    import urllib.parse as urlparse

import requests, json
from ptw.libraries import cleantitle, source_utils
from ptw.libraries import client, cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['cda-hd.cc']
        self.search_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Origin': 'https://cda-hd.cc',
            'Connection': 'keep-alive',
            'Referer': 'https://cda-hd.cc/',
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        self.base_link = 'http://cda-hd.cc/'
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
            cookies = client.request(self.base_link, output='cookie', headers=self.headers)
            cache.cache_insert('cdahd_cookie', cookies)

            for title in titles:
                try:
                    url = urlparse.urljoin(self.base_link, self.search_link)
                    url = url % urlparse.quote_plus(cleantitle.query(title))
                    result = client.request('https://api.searchiq.co/api/search/results?q=%s&engineKey=59344ef44ca3ca07a4bbbeb7b6ee6b38&page=0&itemsPerPage=8&group=0&autocomplete=1' % url.replace("+", "%20"), headers=self.search_headers)
                    result = json.loads(result)
                    for row in result[u'main'][u'records']:
                        name = row[u'title']
                        rok = row[u'ct_release-year'][0]
                        words = title.split(' ')
                        if self.contains_all_words(cleantitle.normalize(cleantitle.getsearch(name)), words) and str(year) in str(rok):
                            url = row[u'url']
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
            if url == None: return sources
            try:
                cookies = cache.cache_get('cdahd_cookie')['value']
            except:
                cookies = ''
            sources = []

            result = client.request(url, cookie=cookies, headers=self.headers)
            result = client.parseDOM(result, 'li', attrs={'class': 'elemento'})
            for item in result:
                try:
                    jezyk = client.parseDOM(item, 'span', attrs={'class': 'c'})[0]
                    jezyk, info = self.get_lang_by_type(jezyk)
                    quality = client.parseDOM(item, 'span', attrs={'class': 'd'})[0]
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if "wysoka" in quality.lower():
                        sources.append({'source': host, 'quality': 'HD', 'language': jezyk, 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                    elif "rednia" in quality.lower():
                        sources.append({'source': host, 'quality': 'SD', 'language': jezyk, 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                    elif "niska" in quality.lower():
                        sources.append({'source': host, 'quality': 'SD', 'language': jezyk, 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                    else:
                        sources.append({'source': host, 'quality': 'SD', 'language': jezyk, 'url': url, 'info': info, 'direct': False, 'debridonly': False})
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
        data = {'action': 'doo_player_ajax', 'post': url[0], 'nume': url[1], 'type': 'movie'}
        response = requests.post('https://cda-hd.cc/wp-admin/admin-ajax.php', data=data).text
        url = client.parseDOM(response, 'iframe', ret='src')[0]

        return url

