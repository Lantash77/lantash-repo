# -*- coding: utf-8 -*-

'''
    Covenant Add-on
    Copyright (C) 2018 CherryTeam

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

import requests
import re
from ptw.libraries import source_utils, client
from ptw.libraries import cleantitle

try:
    import urllib.parse as urllib
except:
    pass


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['iitv.info']

        self.base_link = 'https://iitv.info/'
        self.search_link = 'https://iitv.info/szukaj'
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

    def search(self, titles, season, episode):
        try:
            for title in titles:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                    'Referer': self.base_link}
                result = self.session.get(self.base_link, headers=headers).text
                if result is None:
                    continue

                query = "S%02dE%02d" % (int(season), int(episode))

                result = client.parseDOM(result, 'ul', attrs={'id': 'allSeries'})
                results = client.parseDOM(result, 'li')
                for result in results:
                    found_title = client.parseDOM(result, 'a', ret="title")[0]
                    words = title.split(" ")
                    if self.contains_all_words(found_title, words):
                        link_serial = client.parseDOM(result, 'a', ret='href')[0]
                        serial_content = self.session.get(self.base_link + link_serial, headers=headers).text
                        serial_content = client.parseDOM(serial_content, 'div', attrs={'class': 'episodesLinksWrap'})
                        link_odcinki = client.parseDOM(serial_content, 'a', ret='href')
                        nazwa_odcinki = client.parseDOM(serial_content, 'a')
                        for link_odcinek, nazwa_odcinkek in zip(link_odcinki, nazwa_odcinki):
                            if nazwa_odcinkek.lower() == query.lower():
                                return link_odcinek
        except Exception as e:
            return

    def work(self, link, testDict, headers):
        result = self.session.get(self.base_link + link, headers=headers).text
        link = client.parseDOM(result, 'a', ret='href')[0]
        q = source_utils.check_sd_url(link)
        valid, host = source_utils.is_host_valid(link, testDict)
        if not valid: return 0
        return host, q, link

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):

        return {cleantitle.normalize(cleantitle.getsearch(tvshowtitle)), cleantitle.normalize(cleantitle.getsearch(localtvshowtitle))}

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search(url, season, episode)

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None: return sources
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                       'Referer': self.base_link}
            output = self.session.get(self.base_link + url, headers=headers).text
            output = client.parseDOM(output, 'ul', attrs={'class': 'singleTab'})
            links = client.parseDOM(output, 'a', ret='data-href')
            for link in links:
                try:

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
                        'Accept': '*/*',
                        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Connection': 'keep-alive',
                        'Referer': self.base_link + url,
                        'TE': 'Trailers',
                    }
                    result = self.work(link, hostDict, headers)
                    sources.append({'source': result[0], 'quality': result[1], 'language': 'pl', 'url': result[2],
                                    'info': '', 'direct': False, 'debridonly': False})
                except:
                    continue
            return sources
        except Exception as e:
            return sources

    def resolve(self, url):
        return url
