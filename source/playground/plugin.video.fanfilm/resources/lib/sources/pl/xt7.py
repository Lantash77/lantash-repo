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

import requests

try:
    import urllib.parse as urllib
except:
    pass

from ptw.libraries import source_utils
from ptw.libraries import cleantitle
from ptw.libraries import client, control, cache
from ptw.debug import log_exception


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['xt7.pl']

        self.base_link = 'https://xt7.pl/'
        self.search_link = 'https://xt7.pl/'  # post
        self.session = requests.Session()
        self.user_name = control.setting('xt7.username')
        self.user_pass = control.setting('xt7.password')

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def login(self):
        url = 'https://xt7.pl/login'

        if self.user_name and self.user_pass:
            self.session.post(url, verify=False, allow_redirects=False, data={'login': self.user_name, 'password': self.user_pass})

    def search(self, title, localtitle, year=''):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))
            self.login()

            results = []

            for title in titles:
                data = {'type': '1', 'search': title + ' ' + year + ' (avi|mkv|mp4)'}

                self.session.post('https://xt7.pl/mojekonto/szukaj', data=data).text

                headers = {'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Origin': 'https://xt7.pl', 'Upgrade-Insecure-Requests': '1', 'DNT': '1', 'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.66 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 'Referer': 'https://xt7.pl/mojekonto/szukaj/1',
                    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7', }

                data = {'sort': 'size'}

                self.session.post('https://xt7.pl/mojekonto/szukaj/1', headers=headers, data=data)
                r = self.session.post('https://xt7.pl/mojekonto/szukaj/1', headers=headers, data=data).text

                rows = client.parseDOM(r, 'tr')

                if rows:
                    cookies = self.session.cookies
                    cookies = "; ".join([str(x) + "=" + str(y) for x, y in cookies.items()])
                    cache.cache_insert('xt7_cookie', cookies)
                    results += rows
            return results
        except Exception as e:
            log_exception()
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year)

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return (tvshowtitle, localtvshowtitle), year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        anime = source_utils.is_anime('show', 'tvdb', tvdb)
        self.year = int(url[1])
        self.anime = anime
        if anime:
            epNo = " " + source_utils.absoluteNumber(tvdb, episode, season)
        else:
            epNo = ' s' + season.zfill(2) + 'e' + episode.zfill(2)
        return self.search(url[0][0] + epNo, url[0][1] + epNo)

    def sources(self, rows, hostDict, hostprDict):
        sources = []
        try:
            if type(rows) == tuple:
                quality = source_utils.check_sd_url(rows[0])
                info = self.get_lang_by_type(rows[0])
                sources.append({'source': 'xt7', 'quality': quality, 'language': info[0], 'url': rows[0], 'info': 'Moje Pliki', 'direct': True, 'debridonly': False})
                return sources
            for row in rows:
                try:
                    nazwa = client.parseDOM(row, 'label')[0]
                    if not '.mkv' and '.avi' and '.mp4' in nazwa:
                        continue
                    link = client.parseDOM(row, 'input', ret='value')[0]
                    size = client.parseDOM(row, 'td')[3]
                    if any(size in s['info'] for s in sources):
                        continue
                    quality = source_utils.check_sd_url(nazwa)
                    info = self.get_lang_by_type(nazwa)
                    if not info[1]:
                        info2 = ''
                    else:
                        info2 = info[1]

                    sources.append({'source': 'xt7', 'quality': quality, 'language': info[0], 'url': link, 'info': size + ' ' + info2, 'direct': True, 'debridonly': False})
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
        elif 'lektor pl' in lang_type.lower():
            return 'pl', 'Lektor'
        elif '.dual' in lang_type.lower():
            return 'pl', ''
        elif '.pldub' in lang_type.lower():
            return 'pl', 'Dubbing'
        elif '.pl.' in lang_type.lower():
            return 'pl', ''
        elif '.sub' in lang_type.lower():
            return 'pl', 'Napisy'
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
        cookies = cache.cache_get('xt7_cookie')['value']
        headers = {'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.53 Safari/537.36', 'DNT': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7', 'Cookie': cookies}

        mojekonto = "https://xt7.pl/mojekonto/pliki"
        result = self.session.get(mojekonto, headers=headers).text
        result = client.parseDOM(result, 'table', attrs={'class': "list"})
        result = client.parseDOM(result, 'input', ret='value')
        for item in result:
            link = item
            item = item.split("/")[-1]
            if item in url:
                return str(link + "|User-Agent=vlc/3.0.0-git libvlc/3.0.0-git&verifypeer=false")

        autoxt7 = control.setting('autoxt7')
        if autoxt7 == 'false':
            limit = self.session.get(self.base_link, headers=headers).text
            limit = client.parseDOM(limit, 'div', attrs={'class': "textPremium"})
            limit = str(client.parseDOM(limit, 'b')[-1])

            import xbmcgui
            ret = xbmcgui.Dialog().yesno('xt7', 'Chcesz wykorzystać transfer ze swojego konta xt7 aby odtworzyć tę pozycję?\n Aktualnie posiadasz: [B]%s[/B] transferu' % limit)
            if not ret:
                return

        data = {'step': '1', 'content': url}

        self.session.post('https://xt7.pl/mojekonto/sciagaj', data=data, headers=headers)

        data = {'0': 'on', 'step': '2'}

        content = self.session.post('https://xt7.pl/mojekonto/sciagaj', data=data, headers=headers).text

        result = client.parseDOM(content, 'div', attrs={'class': 'download'})
        link = client.parseDOM(result, 'a', ret='href')[1]

        return str(link + "|User-Agent=vlc/3.0.0-git libvlc/3.0.0-git&verifypeer=false")
