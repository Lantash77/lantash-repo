# -*- coding: utf-8 -*-
'''
    Covenant Add-on
    Copyright (C) 2018 :)

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

import base64
import json
import urllib

try:
    import urllib.parse as urllib
except:
    pass

from ptw.libraries import source_utils
from ptw.libraries import cleantitle
from ptw.libraries import client
from ptw.debug import log_exception


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['3ksodus']

        self.base_link = 'https://3ksodus.com/'
        self.search_link = 'search?v=%s'

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def search(self, title, localtitle, year, is_movie_search):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))

            for title in titles:
                try:
                    url = urllib.urljoin(self.base_link, self.search_link)
                    url = url % urllib.quote(str(title))
                    result = client.request(url)
                    result = client.parseDOM(result, 'div', attrs={
                        'class': 'col-md-3 col-main'})
                except:
                    continue

                for item in result:
                    try:
                        link = str(client.parseDOM(item, 'p', ret='link')[0])
                        nazwa = str(client.parseDOM(item, 'p')[0])
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in link and not '3d' in name:
                            return link
                    except:
                        continue
        except Exception as e:
            log_exception()
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, True)

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None:
                return sources
            url = url
            result = client.request(url)
            results = client.parseDOM(result, 'a', ret='data-iframe')
            for item in results:
                try:
                    test = base64.b64decode(item)
                    item = json.loads(test)
                    valid, host = source_utils.is_host_valid(item['src'], hostDict)
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'pl',
                        'url': item['src'],
                        'info': '',
                        'direct': False,
                        'debridonly': False})
                except:
                    continue
            return sources
        except:
            log_exception()
            return sources

    def get_lang_by_type(self, lang_type):
        if "dubbing" in lang_type.lower():
            if "kino" in lang_type.lower():
                return 'pl', 'Dubbing Kino'
            return 'pl', 'Dubbing'
        elif 'napisy pl' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'napisy' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'lektor pl' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'lektor' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'POLSKI' in lang_type.lower():
            return 'pl', None
        elif 'pl' in lang_type.lower():
            return 'pl', None
        return 'en', None

    def resolve(self, url):
        link = str(url).replace("//", "/").replace(":/", "://").split("?")[0]
        return str(link)
