# -*- coding: utf-8 -*-
###############################################################################
###############################################################################
# Anime-Odcinki
# Some part of code comes from Anonek
# Link decryption fixed for Python 3
###############################################################################
###############################################################################
### Imports ###
import re
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

import requests
from resources.libs.CommonFunctions import parseDOM
#from CommonFunctions import parseDOM

try:
    import json
except:
    import simplejson as json


from resources.libs import addon_tools as addon
from crypto.keyedHash.evp import EVP_BytesToKey
from crypto.cipher.aes_cbc import AES_CBC
from binascii import a2b_hex, a2b_base64
from hashlib import md5

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmcvfs.translatePath('special://home/addons/' + my_addon_id + '/resources/media/')
LETTERS = xbmcvfs.translatePath('special://home/addons/' + my_addon_id + '/resources/media/letters/')
Getsetting = my_addon.getSetting
params = addon.get_params()

#media#
default_background = MEDIA + "fanart.jpg"
custom_background = MEDIA + "sunset.jpg"
fanart = MEDIA + 'fanart.jpg'
nexticon = MEDIA + 'next.png'
fanartAodc = MEDIA + 'animeodcinki.jpg'
searchicon = MEDIA + 'search.png'

Alfabet = list(map(chr, range(65, 91)))
Alfabet.insert(0, '#')
Letters = [(LETTERS + item + '.png') for item in Alfabet]
Letter = dict(zip(Alfabet, Letters))

### ##########################################################################
### ##########################################################################

mainLink = 'https://anime-odcinki.pl/'

def PageAnimeOdcinki(url):

    addon.addDir("[Anime] Alfabetycznie", mainLink + 'anime', 
                 mode='AOAlfabetycznie', fanart=default_background)
    addon.addDir("[Anime] Emitowane", mainLink + 'anime', 
                 mode='AOListTitles', fanart=default_background, section='Aired')
    addon.addDir("[Anime] Wszystkie", mainLink + 'anime', 
                 mode='AOListTitles', fanart=default_background, section='All')
    addon.addDir("[Filmy] Alfabetycznie", mainLink + 'filmy', 
                 mode='AOAlfabetycznie', fanart=default_background)
    addon.addDir("[Filmy] Wszystkie", mainLink + 'filmy', 
                 mode='ListTitles', fanart=default_background, section='All')
    addon.addDir("Gatunki", mainLink + 'gatunki', mode='AOGatunki', 
                 fanart=default_background, section='gatunki',
                 thumb=searchicon)
    addon.addDir("Wyszukiwarka", mainLink + 'szukaj/', mode='AOSearch', 
                 fanart=default_background, section='search',
                 thumb=searchicon)

def Alfabetyczna(url):

    name = params['name']
    url = params['url']

    result = requests.get(url, timeout=15).text
    result = parseDOM(result, 'div', attrs={'id': 'letter-index'})[0]
    lista = re.findall('data-index.*?">\s(.+?)</a>\s\((.+?)\)\s', result)
    for litera in lista:

        if 'Anime' in name:
            addon.addDir(str(litera[0]), url, mode='AOListTitles', section=str(litera[0])[0:1],
                         thumb=str(Letter[str(litera[0])[0:1]]), fanart=custom_background,
                         code='[B][COLOR %s]%s[/COLOR][/B]' % ('green', str(litera[1]) + ' pozycji'))
        else:

            addon.addDir(str(litera[0]), url, mode='AOListTitles', section=str(litera[0])[0:1],
                         thumb=str(Letter[str(litera[0])[0:1]]), fanart=custom_background,
                         code='[B][COLOR %s]%s[/COLOR][/B]' % ('green', str(litera[1]) + ' pozycji'))
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                             label2Mask= '%P')      

def ListTitles():

    section = params['section']
    name = params['name']
    url = params['url']
           
    result = requests.get(url, timeout=15).text
    result = CleanHTML(result)
    if section == 'All':

        result = parseDOM(result, 'tr', attrs={'class': 'list-item'})
        link = [parseDOM(item, 'a', ret='href')[0] for item in result]
        title = [parseDOM(item, 'a')[0] for item in result]
        
    elif section == 'Aired':

        result = parseDOM(result, 'section', attrs={'id': 'block-views-anime-emitowane-block'})
        link = parseDOM(result, 'a', ret='href')
        title = parseDOM(result, 'a')
        
    else:

        result = parseDOM(result, 'tr', attrs={'data-fl' : str(section).lower()})
        link = [parseDOM(item, 'a', ret='href')[0] for item in result]
        title = [parseDOM(item, 'a')[0] for item in result]

    for i in zip(title, link):
        addon.addDir(str(i[0]), str(i[1]), mode='AOListEpisodes', section=section,
                     thumb=str(fanartAodc), fanart=custom_background, subdir=name)

def ListEpisodes():
    
    section = params['section']
    name = params['name']
    url = params['url']
    subdir = params['subdir']
    
    result = requests.get(url, timeout=15).text
    result = CleanHTML(result)
    results = parseDOM(result, 'section', attrs={'id':'anime-header'})
    poster = parseDOM(results, 'img', ret='src')[0]
    link = parseDOM(results, 'a', ret='href')
    title= parseDOM(results, 'a')
    tags = parseDOM(result, 'div', attrs={'class':'field field-name-field-tags'})
    try:
        plot = re.findall('p><p>(.+?)</p>', result)[0]
        if len(re.findall('<span', plot)) >= 0:
            plot = re.sub('<span(.+?)/span>', '', plot)
    except:
        plot = ''
        pass
    
    for i in zip(title, link):
            
        addon.addLink(str(i[0]), str(i[1]), mode='AOListLinks', section='links',
                    thumb=str(poster), plot=str(plot), fanart=custom_background, subdir=subdir)

def ListLinks():

    section = params['section']
    name = params['name']
    url = params['url']
    subdir = params['subdir']
    
    result = requests.get(url, timeout=15).text
    result = parseDOM(result, 'div', attrs={'id': 'video-player-control'})[0]
    player = [re.sub('<img src(.+?)">','',item) for item in 
              parseDOM(result, 'div', attrs={'class': 'video-player-mode'})]
    link = [encryptPlayerUrl(item) for item in parseDOM(result, 'div',
            attrs={'class': 'video-player-mode'} , ret='data-hash')]

    addon.SourceSelect(players=player, links=link, title=name, subdir=subdir)

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
            PageAnimeOdcinki(mainLink)

    elif section == 'nextpage':
        url = url

    html = requests.get(url, timeout=15).text
    result = parseDOM(html, 'li', attrs={'class': 'search-result'})

    for item in result:
      
        nazwa = CleanHTML(str(parseDOM(item, 'a')[0]))
        link = str(parseDOM(item, 'a', ret='href')[0])
        plot = CleanHTML(str(parseDOM(item, 'p')[0]))

        addon.addDir(nazwa, link, mode='AOListEpisodes', thumb=fanartAodc, plot=plot, 
                     fanart=custom_background, section='search', subdir=name)

    if 'nextpostslink' in html:
        nextpage = parseDOM(html, 'a', attrs={'class':'nextpostslink'}, ret='href')[0]
        addon.addDir('[I]następna strona[/I]', nextpage, mode='AOSearch', thumb=nexticon,
                     fanart=custom_background, section='nextpage')
        
def Gatunki():

    section = params['section']
    name = params['name']
    url = params['url']    
    
    if section == 'gatunki':
    
        result = requests.get(url, timeout=15).text
        result = parseDOM(result, 'div', attrs={'class': 'panel-body'})[0]
        taglist = [item for item in parseDOM(result, 'div', attrs={'class': r'.+?' + 'checkbox'}) if len(item)>0]
        tagname = [CleanHTML(item) for item in parseDOM(taglist, 'label')]

        tagcat = [item for item in parseDOM(taglist, 'input', ret='name') ]
        tagcode = ['=' + i for i in parseDOM(taglist, 'input', ret= 'value')]
        taglink = []
        for item in zip(tagcat, tagcode):

            taglink.append(str(item[0]) + str(item[1]))
                
        d = xbmcgui.Dialog()
        select = d.multiselect('Wybór Gatunku', tagname)
        if select == None:
            PageAnimeOdcinki(mainLink)
            return
        seltags = []
        for idx in select:
            seltags.append(taglink[idx])
        sep = '&'
        url = url + '?' + sep.join(seltags)
    

    elif section == 'nextpage':
        url = url

    html = requests.get(url, timeout=15).text
    result = parseDOM(html, 'li', attrs={'class': 'search-result'})

    for item in result:
      
        nazwa = CleanHTML(str(parseDOM(item, 'a')[0]))
        link = str(parseDOM(item, 'a', ret='href')[0])
        plot = CleanHTML(str(parseDOM(item, 'p')[0]))

        addon.addDir(nazwa, link, mode='AOListEpisodes', thumb=fanartAodc, plot=plot, 
                     fanart=custom_background, section='search', subdir=name)

    if 'nextpostslink' in html:
        nextpage = parseDOM(html, 'a', attrs={'class':'nextpostslink'}, ret='href')[0]
        addon.addDir('[I]następna strona[/I]', nextpage, mode='AOGatunki', thumb=nexticon,
                     fanart=custom_background, section='nextpage')

#####Helpers####

def encryptPlayerUrl(data):

#    print(("_encryptPlayerUrl data[%s]" % data))
    decrypted = ''
    try:
        data = json.loads(data)
        salt = str(a2b_hex(data["v"]).decode('iso-8859-1')).encode('iso-8859-1')
        const = str('s05z9Gpd=syG^7{').encode('iso-8859-1')
        key, iv = EVP_BytesToKey(md5, const, salt, 32, 16, 1)
        bcompare = str(a2b_hex(data['b']).decode('iso-8859-1')).encode('utf-8')
        ivcompare = str(iv).encode('utf-8')
        if ivcompare != bcompare:
            print("_encryptPlayerUrl IV mismatched")
        if 0:
            from crypto.cipher import AES
            aes = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
            input = str(a2b_base64(data["a"]).decode('iso-8859-1')).encode('iso-8859-1')
            decrypted = aes.decrypt(input)
            decrypted = decrypted[0:-ord(decrypted[-1])]
        else:
            kSize = len(key)
            alg = AES_CBC(key, keySize=kSize)
            input = str(a2b_base64(data["a"]).decode('iso-8859-1'))
            decrypted = alg.decrypt(input, iv=iv)
            decrypted = decrypted.split('\x00')[0]
        decrypted = "%s" % json.loads(decrypted)
    except:
       decrypted = ''
    return decrypted

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




