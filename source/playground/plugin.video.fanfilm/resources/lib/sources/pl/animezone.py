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

import re

import requests

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
        self.domains = ['animezone.pl']

        self.base_link = 'https://www.animezone.pl'
        self.search_link = 'https://www.animezone.pl/szukaj?q=%s'
        self.session = requests.Session()

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return (tvshowtitle, localtvshowtitle), year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search_ep(url[0], season, episode, tvdb)  # url = titles & year

    def search_ep(self, titles, season, episode, tvdb):
        try:
            odcinek = source_utils.absoluteNumber(tvdb, episode, season)
            for title in titles:
                title = cleantitle.normalize(cleantitle.getsearch(title)).replace(" ", "+").replace("shippuden", "shippuuden")
                r = self.session.get(self.search_link % title).text
                result = client.parseDOM(r, 'div', attrs={'class': 'description pull-right'})  ## na linki i opisy
                linki = client.parseDOM(result, 'a', ret='href')
                nazwy = client.parseDOM(result, 'a')
                for row in zip(linki, nazwy):
                    try:
                        tytul = re.findall("""<mark>(.*)</mark>""", row[1])[0]
                    except:
                        continue
                    tytul = cleantitle.normalize(cleantitle.getsearch(tytul)).replace("  ", " ")
                    words = tytul.split(" ")
                    if self.contains_all_words(title, words):
                        link = self.base_link + row[0].replace('odcinki', 'odcinek') + '/' + odcinek
                        return link
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            content = self.session.get(url).text
            results = client.parseDOM(content, 'table', attrs={'class': 'table table-bordered table-striped table-hover episode'})
            results = client.parseDOM(results, 'td', attrs={'class': 'text-center'})
            for item in results:
                if item.startswith('<span'):
                    continue
                r = re.findall("""data-.*="([0-9].*)">""", item)[0]
                headers = {'Accept': '*/*', 'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': str(url).replace("http://", "https://www."), 'Cache-Control': 'max-age=0', 'Connection': 'keep-alive', 'Host': 'www.animezone.pl',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0', }

                verify = self.session.get('https://www.animezone.pl/images/statistics.gif', headers=headers)

                headers = {'Host': 'www.animezone.pl', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0', 'Accept': '*/*', 'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                    'Referer': str(url).replace("http://", "https://www."), 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Connection': 'keep-alive', 'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache', }

                data = {'data': r}
                response = self.session.post(url, headers=headers, data=data).text
                try:
                    video_link = client.parseDOM(response, 'a', ret='href')[0]
                except:
                    video_link = client.parseDOM(response, 'iframe', ret='src')[0]
                valid, host = source_utils.is_host_valid(video_link, hostDict)
                sources.append({'source': host, 'quality': 'SD', 'language': 'pl', 'url': video_link, 'info': '', 'direct': False, 'debridonly': False})
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
        if not 'sibnet' in url:
            url = str(url).replace("//", "/").replace(":/", "://").split("?")[0]
        return str(url)
