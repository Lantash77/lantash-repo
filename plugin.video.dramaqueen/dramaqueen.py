# -*- coding: UTF-8 -*-
#####Python3.6
import importlib
import re
import os
import sys

import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import resolveurl

reload(sys)
sys.setdefaultencoding('UTF8')

from common import parseDOM
from resources.libs import source_utils, cache, client
from resources.libs import addon_utils as addon

try:
    import HTMLParser
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')

setting = my_addon.getSetting
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/media/')
korea_background = MEDIA + "Korea.jpg"
japan_background = MEDIA + "Japan.jpg"
china_background = MEDIA + "China.jpg"
base_link = "https://dramaqueen.pl"
setting = xbmcaddon.Addon().getSetting


############################################################################################################
############################################################################################################
#                                                   MEDIA                                                  #
############################################################################################################




############################################################################################################
############################################################################################################
#                                                   MENU                                                   #
############################################################################################################

def CATEGORIES():
    Logowanie()
  
    addon.addDir('Drama Koreanska',
                'https://www.dramaqueen.pl/drama/koreanska/',
                 mode=1, fanart=korea_background)
    addon.addDir('Drama Japonska',
                 'https://www.dramaqueen.pl/drama/japonska/',
                 mode=1, fanart=japan_background)
    addon.addDir('Dramy Inne',
                 'https://www.dramaqueen.pl/drama/pozostale/',
                 mode=1, fanart=china_background)
    addon.addDir('Film Korea',
                 'https://www.dramaqueen.pl/film/koreanski/',
                 mode=2, fanart=korea_background)
    addon.addDir('Film Japonia',
                 'https://www.dramaqueen.pl/film/japonski/',
                 mode=2, fanart=japan_background)
    addon.addDir('Filmy Pozosta\xc5\x82e',
                 'https://www.dramaqueen.pl/film/pozostale/',
                 mode=2, fanart=china_background)
#   addon.addDir("Szukaj po nazwie", '', mode=1, fanart=_default_background)
#   addon.addDir("Filtruj", '', mode=2, fanart=_default_background)
#   addon.addDir("Alfabetycznie", '', mode=10, fanart=_default_background)
#   addon.addDir("Ranking najlepiej ocenianych",
#                'https://link cwiczebny/',
#                mode=3, fanart=_default_background)


############################################################################################################
#=##########################################################################################################
#                                                 FUNCTIONS                                                #
#=##########################################################################################################



def Logowanie():
   
    headers = {
        'authority': 'www.dramaqueen.pl',
        'cache-control': 'max-age=0',
        'origin': 'https://dramaqueen.pl',
        'scheme': 'https',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://www.dramaqueen.pl/login/',
        'accept-language': 'pl-PL,pl;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
                   }
    data = {
        'user_login': setting('user'),
        'login_user_pass': setting('pass'),
        'no_captcha': 'yes',
        'upme-login': 'Log In',
    }
    sess = requests.session()
    GetLogin = sess.post('https://www.dramaqueen.pl/login/', headers=headers, data=data)
    global cookie
    kuki = sess.cookies.items()
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('dramaqueen_cookie', cookie)
    
def ListDramas():

    url = params['url']
    rT = requests.get(url, timeout=15).content
    rT = str.replace(rT, '&#8211;', '-')
    rT = str.replace(rT, '<br />\n', ' ')
    rT = str.replace(rT, '[&#8230;', '[...]')
    rT = str.replace(rT, '&#8217;', '\'')
    rT = str.replace(rT, '&#038;', '&')
    rT = str.replace(rT, u'\u2019', '\'')
    result = parseDOM(rT, 'div', attrs={'id': 'av_section_1'})[0]
    results = re.findall('flex_column av_one_fourth(.+?)</div></div></div>', result)

    Titles = re.findall('><p>(.+?)</p>', result)
    Plot = re.findall('/p>[\s,\S,.]<p>(.+?)</p>', result)
    obrazy = parseDOM(results, 'img', ret='src')
    linki = [item for item in parseDOM(results, 'a', ret='href')]
    
    for item in zip(linki, Titles, obrazy, Plot):
        addon.addDir(str(item[1]), str(item[0]), mode=4, plot=(str(item[3])), fanart=(str(item[2])), isFolder=True, thumb=(str(item[2])))

def ListEpisodes():
    Logowanie()
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'max-age=0',
        'Cookie': cookie,
    }
    name = params['name']
    thumb = img
    url = params['url']
    
    rE = str(requests.get(url, headers=headersget, timeout=15).content)
    if len(re.findall('Witaj, ', rE, re.IGNORECASE)) == 0:
        xbmcgui.Dialog().ok('Blad logowania','Zaloguj')
        pass
    rE = str.replace(rE, '&#8211;', '-')
    result = parseDOM(rE, 'div', attrs={'class': 'container'})[1]
    results = re.findall('av_toggle_section(.+?)<span', result)
    episodes = [parseDOM(item, 'p') for item in results]
    plot = parseDOM(rE, 'em')[0]

    fanartlook = str.replace(rE, 'background-image: url(', 'fanart ')
    fanart = re.findall('fanart (.+?)\)', fanartlook)[1]
    
    episodecounter = 1
    for item in episodes:
        if episodecounter < len(episodes):
            episode = 'Odcinek ' + str(episodecounter)
            addon.addLink(episode, url, mode=5, fanart=(str(fanart)), plot=plot, thumb=(str(thumb)))
            episodecounter = episodecounter + 1
        else:
            episode = 'Odcinek ' + str(episodecounter) + ' Fina\xc5\x82'
            addon.addLink(episode, url, mode=5, fanart=(str(fanart)), plot=plot, thumb=(str(thumb)))
    
def ListMovies():
    Logowanie()
    cookie = cache.cache_get('dramaqueen_cookie')['value']

    headersget = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'max-age=0',
        'Cookie': cookie,
    }
    url = params['url']
    rM = str(requests.get(url, headers=headersget, timeout=15).content)
    if len(re.findall('Witaj, ', rM, re.IGNORECASE)) == 0:
       xbmcgui.Dialog().ok('Blad logowania','Zaloguj')
       pass
    rM = str.replace(rM, '&#8211;', '-')
    rM = str.replace(rM, '<br />\n', ' ')
    rM = str.replace(rM, '&#038;', '&')
    rM = str.replace(rM, '[&#8230;', '[...]')
    rM = str.replace(rM, '&#8217;', '\'')
    rM = str.replace(rM, u'\u2019', '\'')

    result = parseDOM(rM, 'div', attrs={'id': 'av_section_1'})[0]
    results = re.findall('flex_column av_one_fourth(.+?)</div></div></div>', result)

    Titles = re.findall('><p>(.+?)</p>', result)
    Plot = re.findall('/p>[\s,\S,.]<p>(.+?)</p>', result)
    obrazy = parseDOM(results, 'img', ret='src')
    linki = [item for item in parseDOM(results, 'a', ret='href')]

    for item in zip(linki, Titles, obrazy, Plot):
        addon.addLink(str(item[1]), str(item[0]), mode=5, thumb=str(item[2]), fanart=str(item[2]), plot=str(item[3]))

def WyswietlanieLinkow():
    Logowanie()
    from common import PlayFromHost
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'max-age=0',
        'Cookie': cookie,
    }

    url = params.get('url')
    name = params.get('name')
        
    if name.startswith('Odcinek '):
        index = int(re.findall('\d+', name)[0])
        rEL = requests.get(url, headers=headersget, timeout=15).content

        if len(re.findall('Witaj, ', rEL, re.IGNORECASE)) == 0:
             xbmcgui.Dialog().ok("Blad logowania")
             pass
        results = [item for item in parseDOM(rEL, 'section') if 'https://www.dramaqueen.pl/player.html' in item]
        avDlinks = [parseDOM(item, 'a', ret='href')for item in results][index - 1]
        avDplayers = [parseDOM(item, 'button')for item in results][index - 1]
                        
        d = xbmcgui.Dialog()
        item = d.select("Wybór playera", avDplayers)
        if item != -1:
            from common import PlayFromHost
            for item in avDlinks:
                print item
                print 'dupa'
                PlayFromHost(item, 'play')
    else:
        rML = requests.get(url, headers=headersget, timeout=15).content

        if len(re.findall('Witaj, ', rML, re.IGNORECASE)) == 0:
             xbmcgui.Dialog().ok("Blad logowania")
             
             pass
        results2 = [item for item in parseDOM(rML, 'section', attrs={'class': 'av_toggle_section'})]
        avMlinks = [parseDOM(item, 'a', ret='href') for item in results2][0]
        avMplayers = [parseDOM(item, 'button') for item in results2][0]
     
        d = xbmcgui.Dialog()
        item = d.select("Wybór playera", avMplayers)
        if item != -1:
            from common import PlayFromHost
            for item in avMlinks:
                print item
                print 'dupa'
                PlayFromHost(item, 'play')
       




############################################################################################################
# =#########################################################################################################
#                                               GET PARAMS                                                 #
# =#########################################################################################################

params = addon.get_params()
url = params.get('url')
name = params.get('name')
img = params.get('img')
try:
    mode = int(params.get('mode'))
except:
    mode = None
iconimage = params.get('iconimage')

############################################################################################################
############################################################################################################
#                                                   MODES                                                  #
############################################################################################################

if mode == None:
    CATEGORIES()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 1:
    ListDramas()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 2:
    ListMovies()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 3:
    ListDramaTitles()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 4:
    ListEpisodes()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 5:
    WyswietlanieLinkow()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

#elif mode == 6:
#    OdpalanieLinku()

#elif mode == 10:
#    Alfabetycznie()
#    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
#    xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################################################
