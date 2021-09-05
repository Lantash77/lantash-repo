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

import json
import re
import urllib

try:
    import urllib.parse as urllib
except:
    pass

from ptw.libraries import source_utils
from ptw.libraries import cleantitle
from ptw.libraries import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['dudeplayer.com']

        self.base_link = 'https://dudeplayer.com/'
        self.search_link = 'https://dudeplayer.com/?s=%s'
        self.anime = False
        self.year = 0

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

    def search(self, title, localtitle, year, is_movie_search):
        try:
            titles = [cleantitle.normalize(cleantitle.getsearch(title)), cleantitle.normalize(cleantitle.getsearch(localtitle))]
            linki = []

            for title in titles:
                try:
                    url = self.search_link % urllib.quote(str(title).replace(" ", "+"))
                    result = client.request(url)
                    result = client.parseDOM(result, 'div', attrs={'class': 'result-item'})
                except:
                    continue
                for item in result:
                    try:
                        link = client.parseDOM(item, 'a', ret='href')[0]
                        nazwa = client.parseDOM(item, 'img', ret='alt')[0]
                        rok = client.parseDOM(item, 'span', attrs={'class': 'year'})[0]
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in rok:
                            return link
                    except:
                        continue
            return linki
        except Exception as e:
            print(e)
            return

    def search_ep(self, titles, season, episode):
        try:
            for title in titles[0]:
                year = titles[1]
                try:
                    url = self.search_link % urllib.quote(str(title).replace(" ", "+"))
                    result = client.request(url)
                    result = client.parseDOM(result, 'div', attrs={'class': 'result-item'})
                except:
                    continue
                for item in result:
                    try:
                        link = client.parseDOM(item, 'a', ret='href')[0]
                        nazwa = client.parseDOM(item, 'img', ret='alt')[0]
                        rok = client.parseDOM(item, 'span', attrs={'class': 'year'})[0]
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in rok:
                            result2 = client.request(link)
                            result2 = client.parseDOM(result2, 'ul', attrs={'class': 'episodios'})
                            link = [x for x in client.parseDOM(result2, 'a', ret='href') if "s%se%s" % (str(season).zfill(2), str(episode).zfill(2)) in x.lower()][0]
                            return link
                    except:
                        continue
            return None
        except Exception as e:
            print(e)
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return (tvshowtitle, localtvshowtitle), year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search_ep(url, season, episode)

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, True)

    def sources(self, url: str, hostDict, hostprDict):
        sources = []
        try:
            result = client.request(url)
            result = client.parseDOM(result, 'ul', attrs={'id': 'playeroptionsul'})
            options = client.parseDOM(result, 'li')
            for c, option in enumerate(options):
                try:
                    quality = client.parseDOM(option, 'span', attrs={'class': 'title'})[0]
                    lang, opis = self.get_lang_by_type(quality)
                    quality = source_utils.check_sd_url(quality)
                    data_post = client.parseDOM(result, 'li', ret="data-post")[c]
                    data_type = client.parseDOM(result, 'li', ret="data-type")[c]
                    data_nume = client.parseDOM(result, 'li', ret="data-nume")[c]
                    href = 'https://dudeplayer.com/wp-json/dooplayer/v1/post/%s?type=%s&source=%s' % (str(data_post), str(data_type), str(data_nume))
                    embed_url = json.loads(client.request(href))['embed_url']
                    video_link = decode_DoodTo(embed_url, url)
                    sources.append({
                        'source': "GOVOD",
                        'quality': quality,
                        'language': lang,
                        'url': video_link,
                        'info': opis,
                        'direct': True,
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
        return 'pl', None

    def resolve(self, url):
        return url


def decode_DoodTo(stream_url, url):
    import math
    import random
    import time

    t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    def dood_decode(data):
        return data + ''.join([t[int(math.floor(random.random() * 62))] for _ in range(10)])

    headersx = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': url,
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers', }
    html = client.request(stream_url, headers=headersx)
    matchx = re.findall("""['"](/pass_md5/.+?)['"]""", html)
    if matchx:
        url = 'https://dood.watch' + matchx[0]
    else:
        return ''
    match = re.search(r'''function\s*makePlay.+?return[^?]+([^"]+)[^/]+([^']+)''', html)

    token = match.group(1)

    headersx.update({'Referer': stream_url})

    html = client.request(url, headers=headersx)

    hea = '&'.join(['%s=%s' % (name, value) for (name, value) in headersx.items()])
    url = dood_decode(html) + token + str(int(time.time() * 1000)) + '|' + hea
    return url
