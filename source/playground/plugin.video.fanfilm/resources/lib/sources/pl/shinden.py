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
from ptw.libraries import client, control


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['shinden.pl']

        self.base_link = 'https://shinden.pl'
        self.search_link = 'https://shinden.pl/titles?search=%s'
        self.user_name = control.setting('shinden.username')
        self.user_pass = control.setting('shinden.password')
        self.session = requests.Session()
        self.cookies = ''

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
            cookies = client.request("https://shinden.pl/", output='cookie')
            headers = {'authority': 'shinden.pl', 'cache-control': 'max-age=0', 'origin': 'https://shinden.pl', 'upgrade-insecure-requests': '1', 'dnt': '1', 'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.27 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 'referer': 'https://shinden.pl/', 'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7', }
            headers.update({'Cookie': cookies})
            data = {'username': self.user_name, 'password': self.user_pass, 'login': ''}

            cookie = requests.post('https://shinden.pl/main/0/login', headers=headers, data=data)
            kuki = cookie.cookies.items()
            self.cookies = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
            if not cookie:
                self.cookies = cookies

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache', 'TE': 'Trailers', 'Cookie': self.cookies}
            odcinek = source_utils.absoluteNumber(tvdb, episode, season)
            for title in titles:
                title = cleantitle.normalize(cleantitle.getsearch(title)).replace(" ", "+").replace("shippuden", "shippuuden")
                filtr = "&series_type%5B0%5D=TV&series_status%5B0%5D=Currently+Airing&series_status%5B1%5D=Finished+Airing&one_online=true"
                r = self.session.get(self.search_link % title + filtr, headers=headers).text
                result = [item for item in client.parseDOM(r, 'li', attrs={'class': 'desc-col'}) if str(item).startswith("<h3>")]

                linki = [item for item in client.parseDOM(result, 'a', ret='href') if str(item).startswith("/titles") or str(item).startswith("/series")]
                nazwy = [item for item in result if re.search("<a href.*?>(.*?)<\/a>", item) is not None]
                for row in zip(linki, nazwy):
                    try:
                        tytul = str(re.findall("<a href.*?>(.*?)<\/a>", row[1])[0]).replace("<em>", "").replace("</em>", "")
                    except:
                        continue
                    tytul = cleantitle.normalize(cleantitle.getsearch(tytul)).replace("  ", " ")
                    words = tytul.split(" ")
                    if self.contains_all_words(title, words):
                        link = self.base_link + row[0] + "/all-episodes"
                        result = self.session.get(link, headers=headers).text
                        result = client.parseDOM(result, 'tbody', attrs={'class': 'list-episode-checkboxes'})
                        result = client.parseDOM(result, 'tr')
                        for item in result:
                            item2 = client.parseDOM(item, 'td')[0]
                            if odcinek == str(item2):
                                return self.base_link + client.parseDOM(item, 'a', ret='href')[0]
        except Exception as e:
            print(e)
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache', 'TE': 'Trailers', 'Cookie': self.cookies}

            content = requests.get(url, headers=headers).text

            results = client.parseDOM(content, 'section', attrs={'class': 'box episode-player-list'})
            results = client.parseDOM(results, 'tr')
            for item in results:
                try:
                    item = client.parseDOM(item, 'td')
                    host = item[0]
                    if 'vidoza' in item[0].lower():
                        host = 'VIDOZA'
                    quality = source_utils.check_sd_url(item[1])
                    audio = client.parseDOM(item[2], 'span', attrs={'class': 'mobile-hidden'})[0]
                    if 'Polski' in audio:
                        jezyk = 'pl'
                    else:
                        jezyk = 'en'
                    try:
                        napisy = client.parseDOM(item[3], 'span', attrs={'class': 'mobile-hidden'})[0]
                        if 'Polski' in napisy: jezyk = 'pl'
                    except:
                        napisy = ''
                    if napisy:
                        napisy = "Napisy " + napisy
                    id = re.findall('''data_(.*?)\"''', str(item[5]))[0]
                    code = re.findall("""_Storage\.basic.*=.*'(.*?)'""", content)[0]
                    video_link = "https://api4.shinden.pl/xhr/%s/player_load?auth=%s" % (id, code)
                    if 'Polski' in audio:
                        sources.append({'source': host, 'quality': quality, 'language': jezyk, 'url': video_link, 'info': 'Polskie Audio', 'direct': False, 'debridonly': False})
                    else:
                        sources.append({'source': host, 'quality': quality, 'language': jezyk, 'url': video_link, 'info': napisy, 'direct': False, 'debridonly': False})
                    continue
                except Exception as e:
                    print(str(e))
                    continue
            return sources
        except Exception as e:
            print(str(e))
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
        import time

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'DNT': '1',
            'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'Cache-Control': 'max-age=0', 'TE': 'Trailers', }
        if str(url).startswith("//"): url = "http://" + url
        init = client.request(url, headers=headers, output='extended')
        headers.update({'Cookie': init[4]})
        time.sleep(5)
        video = client.request(url.replace("player_load", "player_show") + "&width=508", headers=headers)
        try:
            video = client.parseDOM(video, 'iframe', ret='src')[0]
        except:
            video = client.parseDOM(video, 'a', ret='href')[0]
        if str(video).startswith("//"): video = "http:" + video
        return str(video)
