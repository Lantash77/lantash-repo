# -*- coding: utf-8 -*-

import os
import re
import shutil
import unicodedata
import requests
import xbmc
import xbmcvfs
import xbmcaddon

__addon__ = xbmcaddon.Addon()
__version__ = __addon__.getAddonInfo('version')  # Module version
__scriptname__ = __addon__.getAddonInfo('name')
__language__ = __addon__.getLocalizedString
__profile__ = str(xbmc.translatePath(__addon__.getAddonInfo('profile')))
__temp__ = str(xbmc.translatePath(os.path.join(__profile__, 'temp', '')))

regexHelper = re.compile('\W+', re.UNICODE)


def normalizeString(str):
    return unicodedata.normalize(
        'NFKD', str)
    


def log(msg):
    xbmc.log(("### [%s] - %s" % (__scriptname__, msg)), level=xbmc.LOGDEBUG)


def notify(msg_id):
    xbmc.executebuiltin(('Notification(%s,%s)' % (__scriptname__, __language__(msg_id))))


def clean_title(item):
    title = os.path.splitext(os.path.basename(item["title"]))
    tvshow = os.path.splitext(os.path.basename(item["tvshow"]))
    if len(title) > 1:
        if re.match(r'^\.[a-z]{2,4}$', title[1], re.IGNORECASE):
            item["title"] = title[0]
        else:
            item["title"] = ''.join(title)
    else:
        item["title"] = title[0]
    if len(tvshow) > 1:
        if re.match(r'^\.[a-z]{2,4}$', tvshow[1], re.IGNORECASE):
            item["tvshow"] = tvshow[0]
        else:
            item["tvshow"] = ''.join(tvshow)
    else:
        item["tvshow"] = tvshow[0]
    item["title"] = str(item["title"])
    item["tvshow"] = str(item["tvshow"])
    # Removes country identifier at the end
    item["title"] = re.sub(r'\([^\)]+\)\W*$', '', item["title"]).strip()
    item["tvshow"] = re.sub(r'\([^\)]+\)\W*$', '', item["tvshow"]).strip()


def parse_rls_title(item):
    title = regexHelper.sub(' ', item["title"])
    tvshow = regexHelper.sub(' ', item["tvshow"])
    groups = re.findall(r"(.*?) (\d{4})? ?(?:s|season|)(\d{1,2})(?:e|episode|x|\n)(\d{1,2})", title, re.I)
    if len(groups) == 0:
        groups = re.findall(r"(.*?) (\d{4})? ?(?:s|season|)(\d{1,2})(?:e|episode|x|\n)(\d{1,2})", tvshow, re.I)
    if len(groups) > 0 and len(groups[0]) >= 3:
        title, year, season, episode = groups[0]
        item["year"] = str(int(year)) if len(year) == 4 else year
        item["tvshow"] = regexHelper.sub(' ', title).strip()
        item["season"] = str(int(season))
        item["episode"] = str(int(episode))
        log("TV Parsed Item: %s" % (item,))
    else:
        groups = re.findall(r"(.*?)(\d{4})", item["title"], re.I)
        if len(groups) > 0 and len(groups[0]) >= 1:
            title = groups[0][0]
            item["title"] = regexHelper.sub(' ', title).strip()
            item["year"] = groups[0][1] if len(groups[0]) == 2 else item["year"]
            log("MOVIE Parsed Item: %s" % (item,))


class NapisyHelper:

    def get_subtitle_list(self, item):
        search_results = self._search_tvshow(item)
        log("Search results: %s" % search_results)
#        results = self._build_subtitle_list(search_results, item)
        #log("Results: %s" % results)
#        return results
        return search_results

    def _search_tvshow(self, item):

        import re
        results = []
        nazwa = re.split(r'\s\(\w+\)$', item["tvshow"])[0]
        if nazwa == '':
            nazwa = re.split(r'\s\(\w+\)$', item["title"])[0]
        nazwa = nazwa.replace('.', '')
        sezon = 'sezon ' + re.split(r'\s\(\w+\)$', item["season"])[0]
        odcinek = ' ep0' + re.split(r'\s\(\w+\)$', item["episode"])[0]
        log("Szukana nazwa: %s" % (nazwa))
        url = "http://animesub.info/szukaj.php?szukane=%s%s" % (nazwa, odcinek) + '&pTitle=en'
        s = requests.Session()
        r = s.get(url)
        read_data = (r.text)
        listaen = re.compile('<tr class="KNap"><td align="left">(.+?)<\/td>([\S\s]+?)value="(.+?)">([\S\s]+?)value="(.+?)">').findall(read_data)
        ItemCount = len(listaen)
        if ItemCount > 0:
            for item in listaen:
                title = item[0]
                kod = item[2]
                token = item[4]
                cookie = (list(s.cookies.items()))
                cookie = (cookie[0][1])
                results.append({"title": title, "kod": kod, "token": token, "cookie": cookie})
        else :
            url = "http://animesub.info/szukaj.php?szukane=%s%s" % (nazwa, odcinek) + '&pTitle=org'
            s = requests.Session()
            r = s.get(url)
            read_data = (r.text)
            listaorg = re.compile('<tr class="KNap"><td align="left">(.+?)<\/td>([\S\s]+?)value="(.+?)">([\S\s]+?)value="(.+?)">').findall(read_data)
            ItemCount = len(listaorg)
            if ItemCount > 0:
                for item in listaorg:
                    title = item[0]
                    kod = item[2]
                    token = item[4]
                    cookie = (list(s.cookies.items()))
                    cookie = (cookie[0][1])
                    results.append({"title": title, "kod": kod, "token": token, "cookie": cookie})
            else :
                url = "http://animesub.info/szukaj.php?szukane=%s%s" % (nazwa, odcinek) + '&pTitle=en'
                s = requests.Session()
                r = s.get(url)
                read_data = (r.text)
                listapl = re.compile('<tr class="KNap"><td align="left">(.+?)<\/td>([\S\s]+?)value="(.+?)">([\S\s]+?)value="(.+?)">').findall(read_data)
                ItemCount = len(listapl)
                if ItemCount > 0:
                    for item in listapl:
                        title = item[0]
                        kod = item[2]
                        token = item[4]
                        cookie = (list(s.cookies.items()))
                        cookie = (cookie[0][1])
                        results.append({"title": title, "kod": kod, "token": token, "cookie": cookie})
        return results

    def download(self, kod, token, zip_filename, cookie):
        ## Cleanup temp dir, we recomend you download/unzip your subs in temp folder and
        ## pass that to XBMC to copy and activate
        if xbmcvfs.exists(__temp__):
            shutil.rmtree(__temp__)
        xbmcvfs.mkdirs(__temp__)
        cookies = {'ansi_sciagnij': cookie}
        data = [('id', kod), ('sh', token), ('single_file', 'Pobierz napisy')]
        r = requests.post('http://animesub.info/sciagnij.php', cookies=cookies, data=data)
        with open(zip_filename, "wb") as subFile:
            subFile.write(r.content)
        subFile.close()
        xbmc.Monitor().waitForAbort(0.5)
        xbmc.executebuiltin(('Extract("%s","%s")' % (zip_filename, __temp__,)), True)
