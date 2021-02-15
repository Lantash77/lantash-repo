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

base_link = "https://dramaqueen.pl/"
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
default_background = MEDIA + 'search.jpg'

############################################################################################################
############################################################################################################
#                                                   MENU                                                   #
############################################################################################################

def CATEGORIES(login):

    addon.addDir('[COLOR=%s]Gatunki[/COLOR]' % 'yellow',
                 base_link + '#gatunki/',
                 mode=6, fanart=korea_background)  
    addon.addDir(str(DKorea),
                 base_link + 'drama/koreanska/',
                 mode=1, fanart=korea_background, thumb=korea_thumb)
    addon.addDir(str(DJapan),
                 base_link + 'drama/japonska/',
                 mode=1, fanart=japan_background, thumb=japan_thumb)
    addon.addDir('Dramy Inne',
                 base_link + 'drama/pozostale/',
                 mode=1, fanart=china_background, thumb=inne_thumb)
    addon.addDir('Film Korea',
                 base_link + 'film/koreanski/',
                 mode=2, fanart=korea_background, thumb=korea_thumb)
    addon.addDir('Film Japonia',
                 base_link + 'film/japonski/',
                 mode=2, fanart=japan_background, thumb=japan_thumb)
    addon.addDir('Filmy Pozosta\xc5\x82e',
                 base_link + 'film/pozostale/',
                 mode=2, fanart=china_background, thumb=inne_thumb)
    addon.addDir("Wyszukiwanie", 'https://www.dramaqueen.pl/?s=',
                 mode=8, fanart=default_background)
    if login == True:
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
    GetLogin = sess.post(base_link + 'login/', headers=headers, data=data)
    response = GetLogin.status_code
    GetLogin = GetLogin.content
    kuki = sess.cookies.items()
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('dramaqueen_cookie', cookie)

###LoginCheck - server error handling    
    if response == 200:
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
    else:
        d = xbmcgui.Dialog()
        d.notification('dramaqueen.pl ',
                       '[COLOR red]%s[/COLOR]' % ('Problem  -  Błąd serwera -' + str(response)),
                       xbmcgui.NOTIFICATION_INFO, 5000)
        exit()
       

def LoginCheck(url):

    if len(re.findall('Witaj,', url, re.IGNORECASE)) == 0:
        xbmcgui.Dialog().ok('Blad logowania', 'Zaloguj się')
        exit()
    
def Kategorie():

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']
    rG = requests.get(url, headers=headersget, timeout=15).content

#    LoginCheck(url=rG)
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
    rG = CleanHTML(rG)

#    LoginCheck(url=rG)

    result = parseDOM(rG, 'div', attrs={'class': 'avia-content-slider-inner'})[0]
    label = [parseDOM(i, 'a', ret= 'title')[0] for i in parseDOM(result, 'h3')]
    obraz = parseDOM(result, 'img', ret= 'src')
    links = [parseDOM(i, 'a', ret='href')[0] for i in parseDOM(result, 'h3')]

    for item in zip(label, links, obraz):
       if str(item[1]).__contains__('/drama/'):
           addon.addDir(str(item[0]) + '   ' +'[COLOR %s]Drama[/COLOR]' % 'green', str(item[1]), 
           mode=4, fanart=str(item[2]), thumb=str(item[2]))
           
       elif str(item[1]).__contains__('/film/'):
           addon.addLink(str(item[0]) + '   ' +'[COLOR %s]Film[/COLOR]' % 'green', str(item[1]), 
           mode=5, fanart=str(item[2]), thumb=str(item[2]))

def ListDramas():

    url = params['url']
    rT = requests.get(url, timeout=15).content
    
    rT = CleanHTML(rT)

    result = parseDOM(rT, 'div', attrs={'id': 'av_section_1'})[0]
    results = re.findall('flex_column av_one_fourth(.+?)</div></div></div>', result)

    Titles = re.findall('><p>(.+?)</p>', result)
    Plot = re.findall('/p>[\s,\S,.]<p>(.+?)</p>', result)
    obrazy = parseDOM(results, 'img', ret='src')
    linki = [item for item in parseDOM(results, 'a', ret='href')]
    
    for item in zip(linki, Titles, obrazy, Plot):
        addon.addDir(str(item[1]), str(item[0]), mode=4, plot=(str(item[3])), 
            fanart=(str(item[2])), isFolder=True, thumb=(str(item[2])), section='')
    
    
        
def ListEpisodes():

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})    
    
    name = params['name']
    thumb = params['img']
    url = params['url']
    

    rE = str(requests.get(url, headers=headersget, timeout=15).content)
    LoginCheck(rE)
    
    rE = str.replace(rE, '&#8211;', '-')
    rE = rE.replace('&nbsp;', ' ')
    result = parseDOM(rE, 'div', attrs={'class': 'container'})[1]
    results = re.findall('av_toggle_section(.+?)<span', result)
    episodes = [item for item in parseDOM(results, 'p')]
    
    plot = parseDOM(rE, 'em')[0]
    plot = CleanHTML(plot)

    fanart = re.findall('background-image: url\((.+?)\);', rE)[1]
    
    inprogress = '[COLOR=red][I]  w tłumaczeniu[/COLOR][/I]'


    for item in episodes:
        if 'tłumaczenie' in item:
            addon.addLink(str(inprogress), url, mode=5, fanart=(str(fanart)), plot=(str(plot)), thumb=(str(fanart)))
        else:
            addon.addLink(str(item), url, mode=5, fanart=(str(fanart)), plot=(str(plot)), thumb=(str(fanart)))

    
def ListMovies():

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})
    
    url = params['url']
    rM = str(requests.get(url, headers=headersget, timeout=15).content)
    rM = CleanHTML(rM)    


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
    
    
    url = params['url']
    name = params['name']

    if name.startswith('Odcinek '):
        index = int(re.findall('\d+', name)[0])
        rEL = requests.get(url, headers=headersget, timeout=15).content
        LoginCheck(rEL)
        
        results = [item for item in parseDOM(rEL, 'section') if 'https://www.dramaqueen.pl/player.html' in item]
        avDlinks = [parseDOM(item, 'a', ret='href')for item in results][index - 1]
        avDplayers = [parseDOM(item, 'button')for item in results][index - 1]
        
        addon.SourceSelect(players=avDplayers, links=avDlinks, title=name)        
    elif 'tłumaczeni' in name:
        pass
    else:
        rML = requests.get(url, headers=headersget, timeout=15).content
        LoginCheck(rML)
        
        results2 = [item for item in parseDOM(rML, 'section', attrs={'class': 'av_toggle_section'})]
        avMlinks = [parseDOM(item, 'a', ret='href') for item in results2][0]
        avMplayers = [parseDOM(item, 'button') for item in results2][0]
        
        addon.SourceSelect(players=avMplayers, links=avMlinks, title=name)  


def Szukaj():

    url = params['url']




    keyb = xbmc.Keyboard('', "Wyszukiwarka")
    keyb.doModal()

    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
        search = keyb.getText()
        url = url + '%s' % search.replace(" ", "+")
    else:
        
        CATEGORIES(False)

        

    html = requests.get(url, timeout=15).content
    result = str(parseDOM(html, 'main', attrs={'role': 'main'})[0])
    results = [CleanHTML(item) for item in parseDOM(result, 'h2')]
    for item in results:

        if 'Japońsk'  in item:
            continue
        elif 'Koreańsk' in item:
            continue
        elif '/drama/' in item:
           title = parseDOM(item, 'a')[0]
           link = parseDOM(item, 'a', ret='href')[0]
           addon.addDir(str(title) + '[COLOR=green]   drama[/COLOR]', str(link), mode=4, 
                        fanart=default_background, thumb=korea_thumb)
        elif '/film/' in item:
            title = parseDOM(item, 'a')[0]
            link = parseDOM(item, 'a', ret='href')[0]
            addon.addDir(str(title) + '[COLOR=green]   film[/COLOR]', link, mode=5, 
                         fanart=default_background, thumb=korea_thumb)


        else:
            continue




###Tekstowe###
     
def CleanHTML(html):
    if ("&amp;" in html):
        html = html.replace('&amp;', '&')
    if ("&nbsp;" in html):
        html = html.replace('&nbsp;', '')
    if ('&#' in html) and (';' in html):
        if ("&#8211;" in html):
            html = html.replace("&#8211;", "-")
        if ("&#8216;" in html):
            html = html.replace("&#8216;", "'")
        if ("&#8217;" in html):
            html = html.replace("&#8217;", "'")
        if ("&#8220;" in html):
            html = html.replace('&#8220;', '"')
        if ("&#8221;" in html):
            html = html.replace('&#8221;', '"')
        if ("&#0421;" in html):
            html = html.replace('&#0421;', "")
        if (u'\u2019' in html):
            html = html.replace(u'\u2019', '\'')
        if ("&#038;" in html):
            html = html.replace('&#038;', "&")
        if ('&#8230;' in html):
            html = html.replace('&#8230;', '[…]')
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')
    return html

############################################################################################################
# =#########################################################################################################
#                                               GET PARAMS                                                 #
# =#########################################################################################################

params = addon.get_params()

url = params.get('url')
name = params.get('name')
img = params.get('img')
section = params.get('section')

try:
    mode = int(params.get('mode'))
except:
    mode = None


############################################################################################################
############################################################################################################
#                                                   MODES                                                  #
############################################################################################################

if mode == None:
    CATEGORIES(True)
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

elif mode == 8:
    Szukaj()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
#elif mode == 10:
#    Alfabetycznie()
#    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
#    xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################################################

