# -*- coding: UTF-8 -*-
#####Python2.7
import importlib
import re
import os
import sys
import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from CommonFunctions import parseDOM
from resources.libs import cache
from resources.libs import addon_tools as addon

reload(sys)
sys.setdefaultencoding('UTF8')


my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')

setting = my_addon.getSetting
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/media/')

base_link = "https://dramaqueen.pl"
setting = xbmcaddon.Addon().getSetting

headersget = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'max-age=0',

}

DKorea = u'Drama Koreańska'
DJapan = u'Drama Japońska'

############################################################################################################
############################################################################################################
#                                                   MEDIA                                                  #
############################################################################################################
korea_background = MEDIA + 'Korea.jpg'
japan_background = MEDIA + 'Japan.jpg'
china_background = MEDIA + 'China.jpg'
korea_thumb = MEDIA + 'koreathumb.png'
japan_thumb = MEDIA + 'japoniathumb.png'
inne_thumb = MEDIA + 'innethumb.png'


############################################################################################################
############################################################################################################
#                                                   MENU                                                   #
############################################################################################################

def CATEGORIES():

    addon.addDir('[COLOR=%s]Gatunki[/COLOR]' % 'yellow',
                 'https://www.dramaqueen.pl/#gatunki/',
                 mode=6, fanart=korea_background)  
    addon.addDir(str(DKorea),
                'https://www.dramaqueen.pl/drama/koreanska/',
                 mode=1, fanart=korea_background, thumb=korea_thumb)
    addon.addDir(str(DJapan),
                 'https://www.dramaqueen.pl/drama/japonska/',
                 mode=1, fanart=japan_background, thumb=japan_thumb)
    addon.addDir('Dramy Inne',
                 'https://www.dramaqueen.pl/drama/pozostale/',
                 mode=1, fanart=china_background, thumb=inne_thumb)
    addon.addDir('Film Korea',
                 'https://www.dramaqueen.pl/film/koreanski/',
                 mode=2, fanart=korea_background, thumb=korea_thumb)
    addon.addDir('Film Japonia',
                 'https://www.dramaqueen.pl/film/japonski/',
                 mode=2, fanart=japan_background, thumb=japan_thumb)
    addon.addDir('Filmy Pozosta\xc5\x82e',
                 'https://www.dramaqueen.pl/film/pozostale/',
                 mode=2, fanart=china_background, thumb=inne_thumb)
#   addon.addDir("Szukaj po nazwie", '', mode=1, fanart=_default_background)

    Logowanie()
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
    GetLogin = GetLogin.content
    kuki = sess.cookies.items()
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('dramaqueen_cookie', cookie)
    
    if len(re.findall('Witaj, ', GetLogin, re.IGNORECASE)) == 1:
        dialog = xbmcgui.Dialog()
        dialog.notification('dramaqueen.pl ', 'Zalogowano pomyślnie.', xbmcgui.NOTIFICATION_INFO, 5000)
    
    else:
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Nie jesteś zalogowany', 'Zarejestruj się na dramaqueen.pl ',
                       'Wprowadź dane logowania w ustawieniach', 'Otworzyć ustawienia wtyczki?')
        if ret:
            my_addon.openSettings()
            xbmc.executebuiltin('Container.Refresh')
        

def LoginCheck(url):

    if len(re.findall('Witaj, ', url, re.IGNORECASE)) == 0:
        xbmcgui.Dialog().ok('Blad logowania', 'Zaloguj się')
        exit()
    
def Kategorie():

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']
    rG = requests.get(url, headers=headersget, timeout=15).content

    LoginCheck(url=rG)
    result = parseDOM(rG, 'div', attrs={'class': 'tagcloud'})[0]
    links = parseDOM(result, 'a', ret='href')
    label = parseDOM(result, 'a')

    count = [re.findall('\d+', i)[0] for i in parseDOM(result, 'a', ret='aria-label')]

    for item in zip(label, links, count):
 
        addon.addDir(str(item[0]) + '   ' +'[COLOR %s]%s[/COLOR]' % ('green', str(item[2]) + ' pozycji'), str(item[1]), mode=7,
              fanart='', plot='', thumb='')


def KategorieLista():

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']
    rG = requests.get(url, headers=headersget, timeout=15).content
    rG = str.replace(rG, '&#8211;', '-')
    rG = str.replace(rG, '<br />\n', ' ')
    rG = str.replace(rG, '&#038;', '&')
    rG = str.replace(rG, '[&#8230;', '[...]')
    rG = str.replace(rG, '&#8217;', '\'')
    rG = str.replace(rG, u'\u2019', '\'')

    LoginCheck(url=rG)

    result = parseDOM(rG, 'div', attrs={'class': 'avia-content-slider-inner'})[0]
    label = [parseDOM(i, 'a', ret= 'title')[0] for i in parseDOM(result, 'h3')]
    obraz = parseDOM(result, 'img', ret= 'src')
    links = [parseDOM(i, 'a', ret='href')[0] for i in parseDOM(result, 'h3')]

    for item in zip(label, links, obraz):
       if str(item[1]).__contains__('/drama/'):
           addon.addDir(str(item[0]) + '   ' +'[COLOR %s]Drama[/COLOR]' % 'green', str(item[1]), mode=4, fanart=str(item[2]), thumb=str(item[2]))
           
       elif str(item[1]).__contains__('/film/'):
           addon.addLink(str(item[0]) + '   ' +'[COLOR %s]Film[/COLOR]' % 'green', str(item[1]), mode=5, fanart=str(item[2]), thumb=str(item[2]))

def ListDramas():

    url = params['url']
    rT = requests.get(url, timeout=15).content
    rT = str.replace(rT, '&#8211;', '-')
    rT = str.replace(rT, '<br />\n', ' ')
    rT = str.replace(rT, '&#8230;', '…')
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

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})    
    
    name = params['name']
    thumb = img
    url = params['url']
    
    rE = str(requests.get(url, headers=headersget, timeout=15).content)
    LoginCheck(rE)
    
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

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})
    
    url = params['url']
    rM = str(requests.get(url, headers=headersget, timeout=15).content)
    LoginCheck(rM)
    
    rM = str.replace(rM, '&#8211;', '-')
    rM = str.replace(rM, '<br />\n', ' ')
    rM = str.replace(rM, '&#038;', '&')
    rM = str.replace(rM, '&#8230;', '…')  
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
  
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})    
    
    url = params.get('url')
    name = params.get('name')

    if name.startswith('Odcinek '):
        index = int(re.findall('\d+', name)[0])
        rEL = requests.get(url, headers=headersget, timeout=15).content
        LoginCheck(rEL)
        
        results = [item for item in parseDOM(rEL, 'section') if 'https://www.dramaqueen.pl/player.html' in item]
        avDlinks = [parseDOM(item, 'a', ret='href')for item in results][index - 1]
        avDplayers = [parseDOM(item, 'button')for item in results][index - 1]
        
        addon.SourceSelect(players=avDplayers, links=avDlinks, title=name)        

    else:
        rML = requests.get(url, headers=headersget, timeout=15).content
        LoginCheck(rML)
        
        results2 = [item for item in parseDOM(rML, 'section', attrs={'class': 'av_toggle_section'})]
        avMlinks = [parseDOM(item, 'a', ret='href') for item in results2][0]
        avMplayers = [parseDOM(item, 'button') for item in results2][0]
        
        addon.SourceSelect(players=avMplayers, links=avMlinks, title=name)  
     


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

elif mode == 6:
    Kategorie()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode == 7:
    KategorieLista()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

#elif mode == 10:
#    Alfabetycznie()
#    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
#    xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################################################

