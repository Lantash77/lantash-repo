# -*- coding: utf-8 -*-
# Python 3.6
###############################################################################
###############################################################################
# STREFADB.PL
#
# 
###############################################################################
###############################################################################
### Imports ###
import re
import xbmcaddon
import xbmcvfs
import xbmc
import requests
import urllib.request, urllib.parse, urllib.error
from resources.libs import addon_tools as addon

from resources.libs import cache
from resources.libs.CommonFunctions import parseDOM
#from CommonFunctions import parseDOM


try:
    import json
except:
    import simplejson as json


my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmcvfs.translatePath('special://home/addons/' + my_addon_id + '/resources/media/')
LETTERS = xbmcvfs.translatePath('special://home/addons/' + my_addon_id + '/resources/media/letters/')
Getsetting = my_addon.getSetting
mainLink = 'https://strefadb.pl/'
params = addon.get_params()

#media#
default_background = MEDIA + "fanart.jpg"
custom_background = MEDIA + "sunset.jpg"
fanart = MEDIA + 'fanart.jpg'
nexticon = MEDIA + 'next.png'
searchicon = MEDIA + 'search.png'
DBthumb = MEDIA + 'dbposter.jpg'
DBZthumb = MEDIA + 'dbzposter.jpg'
DBKAIthumb = MEDIA + 'dbkaiposter.jpg'
DBGTthumb = MEDIA + 'dbgtposter.jpg'
DBSUPERthumb = MEDIA +  'dbsuperposter.jpg'
DBSUPERHEROthumb = MEDIA + 'dbsuperheroposter.jpg'
DBZABRIDGthumb = MEDIA + 'dbzabridgposter.jpg'
DBMOVIEthumb = MEDIA + 'dbmovieposter.jpg'
DBAllfanart = MEDIA + 'dballfanart.jpg'
DBfanart = MEDIA + 'dbfanart.jpg'
DBZfanart = MEDIA + 'dbzfanart.jpg'
DBKAIfanart = MEDIA + 'dbkaifanart.jpg'
DBGTfanart = MEDIA + 'dbgtfanart.jpg'
DBSUPERfanart = MEDIA + 'dbsuperfanart.jpg'
DBSUPERHEROfanart = MEDIA + 'dbsuperherofanart.jpg'
DBZABRIDGfanart = MEDIA + 'dbzabrifanart.jpg'
host = 'DragonBall'

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

def Logowanie():
    headers = {
        'authority': 'strefadb.pl',
        'cache-control': 'max-age=0',
        'origin': 'https://strefadb.pl/',
        'upgrade-insecure-requests': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://strefadb.pl/',
        'accept-language': 'pl-PL,pl;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
    }
    data = {
        'login': 'bikersoft',  # Getsetting('userdb')
        'password': 'Kl@udia21',  # Getsetting('passdb')
        'signin': ''
    }

    cookie = requests.post('https://strefadb.pl', headers=headers, data=data)
    kuki = list(cookie.cookies.items())
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('db_cookie', cookie)

def Pagedragon():

    addon.addDir("Filmy Kinowe", mainLink + 'filmy-kinowe.html',
                 mode='DBListTitles', fanart=DBAllfanart, section='ListTitles',
                 thumb=DBMOVIEthumb)
    addon.addDir("DragonBall", mainLink + 'odcinki/dragon-ball.html',
                 mode='DBListTitles', fanart=DBfanart, section='ListTitles',
                 thumb=DBthumb)
    addon.addDir("DragonBall Z", mainLink + 'odcinki/dragon-ball-z.html',
                 mode='DBListTitles', fanart=DBZfanart, section='ListTitles',
                 thumb=DBZthumb)
    addon.addDir("DragonBall KAI", mainLink + '/odcinki/dragon-ball-kai.html',
                 mode='DBListTitles', fanart=DBKAIfanart, section='ListTitles',
                 thumb=DBKAIthumb)
    addon.addDir("DragonBall GT", mainLink + '/odcinki/dragon-ball-gt.html',
                 mode='DBListTitles', fanart=DBGTfanart, section='ListTitles',
                 thumb=DBGTthumb)
    addon.addDir("DragonBall Super", mainLink + '/odcinki/dragon-ball-super.html',
                 mode='DBListTitles', fanart=DBSUPERfanart, section='ListTitles',
                 thumb=DBSUPERthumb)
    addon.addDir("DragonBall Super Heroes", mainLink + '/odcinki/dragon-ball-super-heroes.html',
                 mode='DBListTitles', fanart=DBSUPERHEROfanart, section='ListTitles',
                 thumb=DBSUPERHEROthumb)
    addon.addDir("DragonBall Z Abridged", mainLink + '/odcinki/dragon-ball-z-abridged.html',
                 mode='DBListTitles', fanart=DBZABRIDGfanart, section='ListTitles',
                 thumb=DBZABRIDGthumb)

def ListTitles():
   
    url = params['url']
    section = params['section']
    name = params['name']
    thumb = params['img']
    html = requests.get(url, timeout=10).text
    result = parseDOM(html, 'table', attrs={'id':'lista-odcinkow'})[0]
    
    results = [item for item in parseDOM(result, 'tr')]
    
    episodes = [parseDOM(item, 'td') for item in results if 'href' in item]
        
    for title, link, s, r, t in episodes :
        nazwa = parseDOM(link, 'a')[0]
    
        if '<span' in link:
            title = title + '  ' + nazwa + '[COLOR=green]  Filler[/COLOR]'
        else:
            title = title + '  ' + nazwa
        link = mainLink + re.sub('^/', '', parseDOM(link, 'a', ret='href')[0])
    
        addon.addLink(title, link, mode='DBListLinks', fanart=DBAllfanart, thumb=thumb, 
                      section='ListLinks', subdir=name)


def ListLinks():
    Logowanie()
    
    url = params['url']
    section = params['section']
    name = params['name']
    subdir = params['subdir']
         
    cookie = cache.cache_get('db_cookie')['value']
    headersget.update({'Cookie': cookie})
    headers = headersget

    html = requests.get(url, headers=headers, timeout=10).text
    result = parseDOM(html, 'table', attrs={'id':'video-table'})[0]

    results = parseDOM(result, 'tr', attrs={'title':'Kliknij' + r'.+?'})
    playerlink = [mainLink + re.sub('^/', '', parseDOM(item, 'a', ret='href')[0]) for item in results]
    playername = [parseDOM(item, 'a')[0] for item in results]
    player = []

    playerdetails = [parseDOM(item, 'td') for item in results]
    playersubs = [re.sub('<span(.+?)span>', '', parseDOM(item, 'td')[2]) for item in results]
    playeraudio = [parseDOM(item, 'td')[1] for item in results]
    playerquality = [parseDOM(item, 'td')[4] for item in results]

    for item in zip(playername, playersubs, playeraudio, playerquality):
        if 'VIP' in item[0]:
            playertitle = item[0] + '   ' + '[COLOR=red] brak obsługi [/COLOR]' #'[COLOR=green] napisy %s - audio %s - %s [/COLOR]' % (item[1], item[2], item[3])
        else:
            playertitle = item[0] + '   ' + '[COLOR=green] napisy %s - audio %s - %s [/COLOR]' % (item[1], item[2], item[3])
        player.append(playertitle)
        
    addon.SourceSelect(player, playerlink, name, subdir)

def GetDragonVideolink(url):
    
    cookie = cache.cache_get('db_cookie')['value']
    headersget.update({'Cookie': cookie})
    headers = headersget
    videolink = requests.get(url, headers=headers).url
    return videolink

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



def GetDataBeetwenMarkers(data, marker1, marker2, withMarkers=True, caseSensitive=True):
    if caseSensitive:
        idx1 = data.find(marker1)
    else:
        idx1 = data.lower().find(marker1.lower())
    if -1 == idx1:
        return False, ''
    if caseSensitive:
        idx2 = data.find(marker2, idx1 + len(marker1))
    else:
        idx2 = data.lower().find(marker2.lower(), idx1 + len(marker1))
    if -1 == idx2:
        return False, ''
    if withMarkers:
        idx2 = idx2 + len(marker2)
    else:
        idx1 = idx1 + len(marker1)
    return True, data[idx1:idx2]
