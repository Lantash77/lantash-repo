# -*- coding: utf-8 -*-
###############################################################################
###############################################################################
# Anime-Shinden
###############################################################################
###############################################################################
### Imports ###

import re
import os
import xbmc
import xbmcaddon
import xbmcgui
import sys
import xbmcplugin
import time
import requests
try:
    import json
except:
    import simplejson as json
from resources.libs.CommonFunctions import parseDOM
#from CommonFunctions import parseDOM
from resources.libs import addon_tools as addon
from resources.libs import cache

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/resources/media/')
LETTERS = xbmc.translatePath('special://home/addons/' + my_addon_id + '/resources/media/letters/')
Getsetting = my_addon.getSetting
mainLink = 'https://shinden.pl/'
params = addon.get_params()

#media#
default_background = MEDIA + "fanart.jpg"
custom_background = MEDIA + "sunset.jpg"
fanart = MEDIA + 'fanart.jpg'
nexticon = MEDIA + 'next.png'
searchicon = MEDIA + 'search.png'
fanartAshinden = MEDIA + 'animeshinden.jpg'
host = 'AnimeShinden'

Alfabet = list(map(chr, range(65, 91)))
Alfabet.append('#')
Letters = [(LETTERS + item + '.png') for item in Alfabet]
Letter = dict(zip(Alfabet, Letters))

#HTML HEADER
headersget = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'Trailers',     
    }

### ##########################################################################
### ##########################################################################

def PageAnimeShinden():

   addon.addDir("[Anime] Alfabetycznie", mainLink + 'series',
                mode='SHAlfabetycznie', fanart=default_background, section='Alfabetycznie')
   addon.addDir("[Anime] Wszystkie", mainLink + 'series',
                mode='SHListTitles', fanart=default_background, section='All')
   addon.addDir("Wyszukiwarka", mainLink + 'series?search=', mode='SHSearch',
                fanart=default_background, section='search',
                thumb=searchicon)
   addon.addDir("Gatunki", mainLink + 'series?', mode='SHGatunki',
                fanart=default_background, section='gatunki',
                thumb=searchicon)
   addon.addDir("[Anime] Emitowane", mainLink + 'series?series_status[0]=Currently+Airing',
                mode='SHListTitles', fanart=default_background, section='Aired')

def Logowanie():

    headers = {
        'authority': 'shinden.pl',
        'cache-control': 'max-age=0',
        'origin': 'https://shinden.pl',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'referer': 'https://shinden.pl/',
        'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    data = {
        'username': Getsetting('usershinden'),
        'password': Getsetting('passshinden'),
        'login': ''
    }

    cookie = requests.post('https://shinden.pl/main/0/login', headers=headers, data=data)
    kuki = cookie.cookies.items()
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('shinden_cookie', cookie)

def Alfabetyczna():

#    name = params['name']
    url = params['url']

    html = requests.get(url, timeout=15).text
    html = CleanHTML(html)
    result = parseDOM(html, 'ul', attrs={'class': 'letter-list' + r'.+?'})[0]
    letterlink = [str(item).replace('r307=1&', '') for item in parseDOM(result, 'a', ret='href')]
    letter = parseDOM(result, 'a')

    for i in zip(letter, letterlink):
    
        addon.addDir(str(i[0]) , url + str(i[1]), mode='SHListTitles', section=str(i[0]),
                         thumb=str(Letter[str(i[0])]), fanart=custom_background)

def ListTitles(url=''):
   
#    name = params['name']
    if url == '':
        url = params['url']
    section = params['section']
    
    html = requests.get(url, timeout=15).text
    result = str(parseDOM(html, 'section', attrs={'class': 'anime-list box'})[0])
    results = [item for item in parseDOM(result, 'ul', attrs={'class': 'div-row'}) if 'h3' in item]
        
    for item in results:
        link = mainLink + re.sub('/series/', 'series/' ,parseDOM(item, 'a' , ret='href')[1])
        obraz = mainLink + re.sub('/res/', 'res/', parseDOM(item, 'a' , ret='href')[0])
        title = parseDOM(item, 'a')[1]
        title = title.replace('<em>', '')
        title = title.replace('</em>', '')
        try:
            datasite = requests.get(link, timeout=10).text
            plotdata = parseDOM(datasite, 'div', attrs={'id':'description'})[0]
            plot = CleanHTML(parseDOM(plotdata, 'p')[0])
        except:
            plot = '' 
        try:
            genredata = [item for item in parseDOM(datasite, 'tr') if 'Gatunki' in item][0]
            genre = ', ' .join(parseDOM(genredata, 'a'))
        except:
            genre = ''
        try:
            yeardata = parseDOM(datasite, 'section', attrs={'class': 'title-small-info'})[0]
            year = re.findall(r'[1-2][0-9]{3}', yeardata)[0]
        except:
            year = ''

        addon.addDir(str(title) , link, mode='SHListEpisodes', section='episodes',
                     thumb=str(obraz), fanart=custom_background, subdir=str(title),
                     plot=str(plot), genre=str(genre), year=str(year))
    
    try:
        next = parseDOM(html, 'a' , attrs={'rel' : 'next'}, ret='href')[0]
        if len(next) > 0:

            nextpage = mainLink + re.sub('/', '', next)
            nextpage = CleanHTML(nextpage)
            if '&r307=1' in nextpage:
                nextpage = str(nextpage).replace('&r307=1', '')
            elif 'r307=1' in nextpage:
                nextpage = str(nextpage).replace('r307=1', '')
            addon.addDir('[I]następna strona[/I]' , str(nextpage), mode='SHListTitles', 
                         section='nextpage', thumb=str(nexticon), fanart=custom_background,)               
    except:
        pass
     
def Search():

    section = params['section']
    name = params['name']
    url = params['url']
    
    if section == 'search':
        keyb = xbmc.Keyboard('', "Wyszukiwarka anime")
        keyb.doModal()

        if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
            search = keyb.getText()
            url = url + '%s' % search.replace(" ", "+")
        else:
            PageAnimeShinden()
            return

    elif section == 'nextpage':
        url = url
    
    ListTitles(url)

    
def ListEpisodes():

    section = params['section']
    url = params['url'] + '/all-episodes'
    
    thumb = params['img']    
    subdir = params['subdir']
    
    Logowanie()
    cookie = cache.cache_get('shinden_cookie')['value']
    headersget.update({'Cookie': cookie})
    headers = headersget    
    
    html = requests.get(url, headers=headers, timeout=15).text    
    
    result = parseDOM(html, 'tbody', attrs={'class': 'list-episode-checkboxes'})[0]
    results = parseDOM(result, 'tr')
    epNo = [parseDOM(item, 'td')[0] for item in results]
    epTitle = [parseDOM(item, 'td', attrs={'class': 'ep-title'})[0] for item in results]
    epstatus = [re.findall('<i class="fa fa-fw fa-(.+?)"></i>', item)[0] for item in results]
    epDate = [parseDOM(item, 'td', attrs={'class': 'ep-date'})[0] for item in results]
    link = [mainLink + re.sub('^/', '', parseDOM(item, 'a', ret='href')[0]) for item in results]

    for ep in zip(epNo, epTitle, epDate, link, epstatus):
        if str(ep[4]) == 'check':
            title = str(ep[0]) + '  : ' + str(ep[1])
            code = '[B][COLOR=blue]%s[/COLOR][/B]' % (str(ep[2]))
            section ='online'
        elif str(ep[4]) == 'times':
            title = str(ep[0]) + '  ' + '[COLOR=red]  offline [/COLOR]'
            section = 'offline'
            code = '[B][COLOR=blue]%s[/COLOR][/B]' % (str(ep[2]))
        else:
            title = str(ep[0]) + '  ' + '[COLOR=red]  offline [/COLOR]'
            section= 'offline'
            code = '[B][COLOR=blue]%s[/COLOR][/B]' % (str(ep[2]))
       
        addon.addLink(title, str(ep[3]), mode='SHListLinks', fanart=str(thumb), thumb=str(thumb),
                      section=section, subdir=subdir, code=code)
 
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                                 label2Mask= '%P')      
                                 
def ListLinks():
            
    name = params['name']
    url = params['url']
    section = params['section']
    subdir = params['subdir']
    
    if section == 'online':
    
        Logowanie()
        cookie = cache.cache_get('shinden_cookie')['value']
        headersget.update({'Cookie': cookie})
        headers = headersget
        
        html = requests.get(url, headers=headers, timeout=15).text
        result = [item for item in parseDOM(html, 'tbody') if 'player' in item]
        results = parseDOM(result, 'tr')

        playerinfo = [re.findall('data-episode=\'(.+?)\' ', item) for item in results]

        code = re.findall("""_Storage\.basic.*=.*'(.*?)'""", html)[0]
        playerdata = [json.loads(item[0]) for item in playerinfo]
        
        playerlink = []
        player = []
        for i in playerdata:
            title = i['player'] + '[COLOR=green]%s[/COLOR]' % ('     ' +  'Audio' + ' ' + i['lang_audio']
                                                               + ('' if (i['lang_subs'] == '') or (i['lang_subs'] == None) 
                                                               else '   SUB  ' + i['lang_subs']))
            player.append(title)
            ID = (i['online_id'])

            link = "https://api4.shinden.pl/xhr/%s/player_load?auth=%s" % (ID, code)
            playerlink.append(link)

        addon.SourceSelect(player, playerlink, name, subdir)
    else:
        return

def Gatunki():
    
    section = params['section']
    url = params['url']

    if section == 'gatunki':
        html = requests.get(url, timeout=10).text
        tagname = [re.sub('<i(.+?)</i>', '', item) for item in parseDOM(html, 'a', attrs={'class' : 'genre-item'})]
        tagcode = ['i' + item for item in parseDOM(html, 'a', attrs={'class' : 'genre-item'} , ret= 'data-id')]
        taglink = []

        d = xbmcgui.Dialog()
        select = d.multiselect('Wybór Gatunku', tagname)
        seltags = []
        if select == None:
            PageAnimeShinden()
            return
        for idx in select:
            seltags.append(tagcode[idx])
        sep = ';'
        url = url + 'genres-type=all&genres=' + sep.join(seltags)

    elif section == 'nextpage':
        url = url
    
    ListTitles(url)

   
def ShindenGetVideoLink(url):

    headers = {
            'Accept': '*/*',
            'Origin': 'https://shinden.pl',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.46 Safari/537.36',
            'DNT': '1',
        }

    if str(url).startswith("//"): url = "https://" + url
    session = requests.session()
    session.get(url, headers=headers, timeout=15)
    time.sleep(5)
    video = session.get(url.replace("player_load", "player_show") + "&width=508", timeout=5).text
    video_url = ''
    try:
        video_url = parseDOM(video, 'iframe', ret='src')[0]
    except:
        pass
    if not video_url:
        try:
            video_url = parseDOM(video, 'a', ret='href')[0]
        except:
            pass
    if not video_url:
        try:
            video_url = re.findall("src=\"(.*?)\"", video)[0]
        except:
            pass
    if str(video_url).startswith("//"): video_url = "http:" + video_url    
    return video_url

#####Helpers#######


def CleanHTML(html):
    if ("&amp;" in html):
        html = html.replace('&amp;', '&')
    if ("&nbsp;" in html):
        html = html.replace('&nbsp;', '')
    if ('[&hellip;]' in html):
        html = html.replace('[&hellip;]', '[…]')
    if ('&#' in html) and (';' in html):
        if ("&#8211;" in html):# -*- coding: utf-8 -*-
###############################################################################
###############################################################################
# Anime-Shinden
###############################################################################
###############################################################################
### Imports ###

import re
import os
import xbmc
import xbmcaddon
import xbmcgui
import sys
import xbmcplugin
import time
import requests
try:
    import json
except:
    import simplejson as json
from resources.libs.CommonFunctions import parseDOM
#from CommonFunctions import parseDOM
from resources.libs import addon_tools as addon
from resources.libs import cache

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/resources/media/')
LETTERS = xbmc.translatePath('special://home/addons/' + my_addon_id + '/resources/media/letters/')
Getsetting = my_addon.getSetting
mainLink = 'https://shinden.pl/'
params = addon.get_params()

#media#
default_background = MEDIA + "fanart.jpg"
custom_background = MEDIA + "sunset.jpg"
fanart = MEDIA + 'fanart.jpg'
nexticon = MEDIA + 'next.png'
searchicon = MEDIA + 'search.png'
fanartAshinden = MEDIA + 'animeshinden.jpg'
host = 'AnimeShinden'

Alfabet = list(map(chr, range(65, 91)))
Alfabet.append('#')
Letters = [(LETTERS + item + '.png') for item in Alfabet]
Letter = dict(zip(Alfabet, Letters))

#HTML HEADER
headersget = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'Trailers',     
    }

### ##########################################################################
### ##########################################################################

def PageAnimeShinden():

   addon.addDir("[Anime] Alfabetycznie", mainLink + 'series',
                mode='SHAlfabetycznie', fanart=default_background, section='Alfabetycznie')
   addon.addDir("[Anime] Wszystkie", mainLink + 'series',
                mode='SHListTitles', fanart=default_background, section='All')
   addon.addDir("Wyszukiwarka", mainLink + 'series?search=', mode='SHSearch',
                fanart=default_background, section='search',
                thumb=searchicon)
   addon.addDir("Gatunki", mainLink + 'series?', mode='SHGatunki',
                fanart=default_background, section='gatunki',
                thumb=searchicon)
   addon.addDir("[Anime] Emitowane", mainLink + 'series?series_status[0]=Currently+Airing',
                mode='SHListTitles', fanart=default_background, section='Aired')

def Logowanie():

    headers = {
        'authority': 'shinden.pl',
        'cache-control': 'max-age=0',
        'origin': 'https://shinden.pl',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'referer': 'https://shinden.pl/',
        'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    data = {
        'username': Getsetting('usershinden'),
        'password': Getsetting('passshinden'),
        'login': ''
    }

    cookie = requests.post('https://shinden.pl/main/0/login', headers=headers, data=data)
    kuki = cookie.cookies.items()
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('shinden_cookie', cookie)

def Alfabetyczna():

#    name = params['name']
    url = params['url']

    html = requests.get(url, timeout=15).text
    html = CleanHTML(html)
    result = parseDOM(html, 'ul', attrs={'class': 'letter-list' + r'.+?'})[0]
    letterlink = [str(item).replace('r307=1&', '') for item in parseDOM(result, 'a', ret='href')]
    letter = parseDOM(result, 'a')

    for i in zip(letter, letterlink):
    
        addon.addDir(str(i[0]) , url + str(i[1]), mode='SHListTitles', section=str(i[0]),
                         thumb=str(Letter[str(i[0])]), fanart=custom_background)

def ListTitles(url=''):
   
#    name = params['name']
    if url == '':
        url = params['url']
    section = params['section']
    
    html = requests.get(url, timeout=15).text
    result = str(parseDOM(html, 'section', attrs={'class': 'anime-list box'})[0])
    results = [item for item in parseDOM(result, 'ul', attrs={'class': 'div-row'}) if 'h3' in item]
        
    for item in results:
        link = mainLink + re.sub('/series/', 'series/' ,parseDOM(item, 'a' , ret='href')[1])
        obraz = mainLink + re.sub('/res/', 'res/', parseDOM(item, 'a' , ret='href')[0])
        title = parseDOM(item, 'a')[1]
        title = title.replace('<em>', '')
        title = title.replace('</em>', '')
        
### Metadane do Tytułów : Opis, Gatunki, Rok
        try:
            datasite = requests.get(link, timeout=10).text
            plotdata = parseDOM(datasite, 'div', attrs={'id':'description'})[0]
            plot = CleanHTML(parseDOM(plotdata, 'p')[0])
        except:
            plot = '' 
        try:
            genredata = [item for item in parseDOM(datasite, 'tr') if 'Gatunki' in item][0]
            genre = ', ' .join(parseDOM(genredata, 'a'))
        except:
            genre = ''
        try:
            yeardata = parseDOM(datasite, 'section', attrs={'class': 'title-small-info'})[0]
            year = re.findall(r'[1-2][0-9]{3}', yeardata)[0]
        except:
            year = ''

        addon.addDir(str(title) , link, mode='SHListEpisodes', section='episodes',
                     thumb=str(obraz), fanart=custom_background, subdir=str(title),
                     plot=str(plot), genre=str(genre), year=str(year))

#Nextpage    
    try:
        next = parseDOM(html, 'a' , attrs={'rel' : 'next'}, ret='href')[0]
        if len(next) > 0:

            nextpage = mainLink + re.sub('/', '', next)
            nextpage = CleanHTML(nextpage)
            if '&r307=1' in nextpage:
                nextpage = str(nextpage).replace('&r307=1', '')
            elif 'r307=1' in nextpage:
                nextpage = str(nextpage).replace('r307=1', '')
            addon.addDir('[I]następna strona[/I]' , str(nextpage), mode='SHListTitles', 
                         section='nextpage', thumb=str(nexticon), fanart=custom_background,)               
    except:
        pass
     
def Search():

    section = params['section']
    name = params['name']
    url = params['url']
    
    if section == 'search':
        keyb = xbmc.Keyboard('', "Wyszukiwarka anime")
        keyb.doModal()

        if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
            search = keyb.getText()
            url = url + '%s' % search.replace(" ", "+")
        else:
            PageAnimeShinden()
            return

    elif section == 'nextpage':
        url = url
    
    ListTitles(url)

    
def ListEpisodes():

    section = params['section']
    url = params['url'] + '/all-episodes'
    
    thumb = params['img']    
    subdir = params['subdir']
    
    Logowanie()
    cookie = cache.cache_get('shinden_cookie')['value']
    headersget.update({'Cookie': cookie})
    headers = headersget    
    
    html = requests.get(url, headers=headers, timeout=15).text    
    
    result = parseDOM(html, 'tbody', attrs={'class': 'list-episode-checkboxes'})[0]
    results = parseDOM(result, 'tr')
    epNo = [parseDOM(item, 'td')[0] for item in results]
    epTitle = [parseDOM(item, 'td', attrs={'class': 'ep-title'})[0] for item in results]
    epstatus = [re.findall('<i class="fa fa-fw fa-(.+?)"></i>', item)[0] for item in results]
    epDate = [parseDOM(item, 'td', attrs={'class': 'ep-date'})[0] for item in results]
    link = [mainLink + re.sub('^/', '', parseDOM(item, 'a', ret='href')[0]) for item in results]

    for ep in zip(epNo, epTitle, epDate, link, epstatus):
        if str(ep[4]) == 'check':
            title = str(ep[0]) + '  : ' + str(ep[1])
            code = '[B][COLOR=blue]%s[/COLOR][/B]' % (str(ep[2]))
            section ='online'
        elif str(ep[4]) == 'times':
            title = str(ep[0]) + '  ' + '[COLOR=red]  offline [/COLOR]'
            section = 'offline'
            code = '[B][COLOR=blue]%s[/COLOR][/B]' % (str(ep[2]))
        else:
            title = str(ep[0]) + '  ' + '[COLOR=red]  offline [/COLOR]'
            section= 'offline'
            code = '[B][COLOR=blue]%s[/COLOR][/B]' % (str(ep[2]))
       
        addon.addLink(title, str(ep[3]), mode='SHListLinks', fanart=str(thumb), thumb=str(thumb),
                      section=section, subdir=subdir, code=code)
 
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                                 label2Mask= '%P')      
                                 
def ListLinks():
            
    name = params['name']
    url = params['url']
    section = params['section']
    subdir = params['subdir']
    
    if section == 'online':
    
        Logowanie()
        cookie = cache.cache_get('shinden_cookie')['value']
        headersget.update({'Cookie': cookie})
        headers = headersget
        
        html = requests.get(url, headers=headers, timeout=15).text
        result = [item for item in parseDOM(html, 'tbody') if 'player' in item]
        results = parseDOM(result, 'tr')

        playerinfo = [re.findall('data-episode=\'(.+?)\' ', item) for item in results]

        code = re.findall("""_Storage\.basic.*=.*'(.*?)'""", html)[0]
        playerdata = [json.loads(item[0]) for item in playerinfo]
        
        playerlink = []
        player = []
        for i in playerdata:
            title = i['player'] + '[COLOR=green]%s[/COLOR]' % ('     ' +  'Audio' + ' ' + i['lang_audio']
                                                               + ('' if (i['lang_subs'] == '') or (i['lang_subs'] == None) 
                                                               else '   SUB  ' + i['lang_subs']))
            player.append(title)
            ID = (i['online_id'])

            link = "https://api4.shinden.pl/xhr/%s/player_load?auth=%s" % (ID, code)
            playerlink.append(link)

        addon.SourceSelect(player, playerlink, name, subdir)
    else:
        return

def Gatunki():
    
    section = params['section']
    url = params['url']

    if section == 'gatunki':
        html = requests.get(url, timeout=10).text
        tagname = [re.sub('<i(.+?)</i>', '', item) for item in parseDOM(html, 'a', attrs={'class' : 'genre-item'})]
        tagcode = ['i' + item for item in parseDOM(html, 'a', attrs={'class' : 'genre-item'} , ret= 'data-id')]
        taglink = []

        d = xbmcgui.Dialog()
        select = d.multiselect('Wybór Gatunku', tagname)
        seltags = []
        if select == None:
            PageAnimeShinden()
            return
        for idx in select:
            seltags.append(tagcode[idx])
        sep = ';'
        url = url + 'genres-type=all&genres=' + sep.join(seltags)

    elif section == 'nextpage':
        url = url
    
    ListTitles(url)

   
def ShindenGetVideoLink(url):

    headers = {
            'Accept': '*/*',
            'Origin': 'https://shinden.pl',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.46 Safari/537.36',
            'DNT': '1',
        }

    if str(url).startswith("//"): url = "https://" + url
    session = requests.session()
    session.get(url, headers=headers, timeout=15)
    time.sleep(5)
    video = session.get(url.replace("player_load", "player_show") + "&width=508", timeout=5).text
    video_url = ''
    try:
        video_url = parseDOM(video, 'iframe', ret='src')[0]
    except:
        pass
    if not video_url:
        try:
            video_url = parseDOM(video, 'a', ret='href')[0]
        except:
            pass
    if not video_url:
        try:
            video_url = re.findall("src=\"(.*?)\"", video)[0]
        except:
            pass
    if str(video_url).startswith("//"): video_url = "http:" + video_url    
    return video_url

#####Helpers#######


def CleanHTML(html):
    if ("&amp;" in html):
        html = html.replace('&amp;', '&')
    if ("&nbsp;" in html):
        html = html.replace('&nbsp;', '')
    if ('[&hellip;]' in html):
        html = html.replace('[&hellip;]', '[…]')
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
        if ('[&hellip;]' in html):
            html = html.replace('[&hellip;]', '[…]')
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')
        if (u'\u2661' in html):
            html = html.replace(u'\u2661', ' ')
        if (u'\u222c' in html):
            html = html.replace(u'\u222c', ' ')

    return html

#xbmc.log('Anime Otaku | Shinden wynik nextpage: %s' % str(nextpage) + '  ', xbmc.LOGINFO)
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
        if ('[&hellip;]' in html):
            html = html.replace('[&hellip;]', '[…]')
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')
        if (u'\u2661' in html):
            html = html.replace(u'\u2661', ' ')
        if (u'\u222c' in html):
            html = html.replace(u'\u222c', ' ')

    return html

#xbmc.log('Anime Otaku | Shinden wynik nextpage: %s' % str(nextpage) + '  ', xbmc.LOGINFO)