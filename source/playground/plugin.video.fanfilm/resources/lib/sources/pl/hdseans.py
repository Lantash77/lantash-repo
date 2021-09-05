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

import json
import re
try:
    import urllib.parse as urllib
except:
    pass

import urllib.parse as urlparse

import requests
from ptw.libraries import source_utils, client, cleantitle, control, cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['hdseans.pl']
        self.user_name = control.setting('hdseans.username')
        self.user_pass = control.setting('hdseans.password')
        self.base_link = 'https://hdseans.pl'
        self.search_link = '/autocomplete?query=%s'
        self.session = requests.Session()
        self.useragent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.40 Mobile Safari/537.36"

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        str_to_check2 = (cleantitle.normalize(cleantitle.getsearch(str_to_check)))
        for word in words:
            if not self.contains_word(str_to_check, word) and not self.contains_word(str_to_check2, word):
                return False
        return True

    def login(self):
        s = requests.session()
        cookies = ''

        result = s.get("https://hdseans.pl/login", headers={'Cookie': cookies}).text
        if 'wyloguj' in result.lower() and not self.user_pass and not self.user_pass:
            return
        token = re.findall('_token".value="(.*?)"', result)[0]

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                   'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://hdseans.pl', 'Connection': 'keep-alive', 'Referer': 'https://hdseans.pl/login', 'Upgrade-Insecure-Requests': '1', 'TE': 'Trailers', }

        login = self.user_name
        password = self.user_pass

        if not login or not password:
            login = "sexij28284@mailart.top"
            password = "kodik123"

        data = {'_token': token, 'previous': 'https://hdseans.pl/filmy', 'email': login, 'password': password, 'remember': 'on'}

        result = s.post('https://hdseans.pl/login-s', headers=headers, data=data)
        cookies = '; '.join(['%s=%s' % (i.name, i.value) for i in result.cookies])
        cache.cache_insert('hdseans_cookie', cookies)

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year)

    def search(self, title, localtitle, year):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))
            for title in titles:
                try:
                    query = self.search_link % urllib.quote_plus(title)
                    url = urlparse.urljoin(self.base_link, query)
                    result = client.request(url)
                    results = json.loads(result)
                except:
                    continue
                for result in results:
                    try:
                        segosurl = result['video_url']
                        segostitle = result['title']
                        rok = result['release_year']
                    except:
                        continue
                    try:
                        simply_name = title.replace("  ", " ")
                        words = simply_name.split(" ")
                        if self.contains_all_words(cleantitle.normalize(cleantitle.getsearch(segostitle)), words) and year == rok:
                            return segosurl
                        continue
                    except:
                        continue
        except Exception as e:
            print(str(e))
            return

    def fix_game_of_thrones(self, title, year):
        if title == "Gra o tron":
            return "2011"
        else:
            return year

    def search_ep(self, titles, season, episode):
        try:
            for title in titles[0]:
                year = self.fix_game_of_thrones(title, titles[1])
                if not title:
                    continue
                title = cleantitle.normalize(cleantitle.getsearch(title))
                try:
                    query = self.search_link % urllib.quote_plus(title)
                    url = urlparse.urljoin(self.base_link, query)
                    result = client.request(url)
                    results = json.loads(result)
                except:
                    continue
                for result in results:
                    try:
                        segosurl = result[u'video_url']
                        segostitle = result[u'title']
                        rok = result[u'release_year']
                    except:
                        continue
                    try:
                        simply_name = title.replace("  ", " ")
                        words = simply_name.split(" ")
                        if self.contains_all_words(cleantitle.normalize(cleantitle.getsearch(segostitle)), words) and year == rok:
                            query = "/S%01d-E%01d" % (int(season), int(episode))
                            return segosurl + query
                        continue
                    except:
                        continue
        except Exception as e:
            print(str(e))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return (tvshowtitle, localtvshowtitle), year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search_ep(url, season, episode)

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            self.login()
            try:
                cookies = cache.cache_get('hdseans_cookie')['value']
            except:
                cookies = ''
            headers = {'Cookie': cookies}
            result = requests.get(url, headers=headers)
            grid = client.parseDOM(result.text, 'div', attrs={'class': 'watch-table__column'})
            video_links = client.parseDOM(result.text, 'div', attrs={'class': 'watch-table__column'}, ret="data-link")
            for item, link in zip(grid, video_links):
                try:
                    if not link:
                        continue
                    video_result = client.parseDOM(result.text, 'div', attrs={'class': "watch-table__row watch-table__row--small"})
                    language = video_result[3]
                    lang, info = self.get_lang_by_type(language)
                    quality = video_result[4]
                    quality = source_utils.check_sd_url(quality)
                    valid, host = source_utils.is_host_valid(link, hostDict)
                    sources.append({'source': host, 'quality': quality, 'language': lang, 'url': link, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    continue
            return sources
        except Exception as e:
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
        if 'Cookie' in url:
            headers = requests.utils.default_headers()
            return url + "&User-Agent=" + headers['User-Agent']
        else:
            return url
