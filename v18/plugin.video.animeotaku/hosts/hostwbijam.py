# -*- coding: utf-8 -*-
###############################################################################
###############################################################################
# Wbijam.pl
###############################################################################
###############################################################################
### Imports ###
import re
import xbmcaddon
import xbmc
import requests
import urllib
from resources.libs import addon_tools as addon
from CommonFunctions import parseDOM

#from common import GetDataBeetwenMarkers


my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/art/japan/')

params = addon.get_params()
mainLink = 'https://inne.wbijam.pl/'
#media#
default_background = MEDIA + "fanart.jpg"
fanart = MEDIA + 'fanart.jpg'
nexticon = MEDIA + 'next.png'
fanartAol = MEDIA + 'wbijam.jpg'
host = 'Wbijam'


def Pagewbijam(url):

    result = requests.get(url, timeout=15).content
    
    if (len(url) == 0):
        return
    result = re.sub('>Menu główne', '', result)
    result = re.sub('>Reklama', '', result)
    data = [item for item in parseDOM(result, 'div', attrs={'class' : 'pmenu_naglowek_' + r'.'}) 
            if len(item)>0 ]
            
    if len(data) > 0:
        for item in data:
            name = item
                       
            addon.addDir(str(name), url, mode='Browse_Titles', thumb=fanartAol, fanart=default_background)
            
    

def Browse_Titles():

    url = params['url']
    name = params['name']
    html = requests.get(url, timeout=15).content
    if name in html:
        mark1 = '>' + name + '</div>'
        mark2 = '</ul>'

    data = GetDataBeetwenMarkers(html, mark1, mark2, False)[1]
    data = re.findall('<a href="(.+?)"(.+?)">(.+?)</a></li>', data)
    data.sort()
#####Polecane #######
    if len(data) > 0:  
        for item in data:
            link = item[0]
            title = item[2]
            if 'inne.wbijam' in str(item[0]).lower():
                continue
            addon.addDir(title, link, mode='Browse_Seasons', thumb=fanartAol, fanart=default_background, section='polecane', page=str(url))
#####Pozostałe###
    elif len(data) == 0:
            data2 = GetDataBeetwenMarkers(html, mark1, mark2, False)[1]
            data2 = re.findall('<a href="(.+?)">(.+?)</a></li>', data2)
            data2.sort()
            for item in data2:
                link = url + item[0]
                set = requests.get(link, timeout=15).content
                image = parseDOM([i for i in parseDOM(set,'center') if 'img' in i][0], 'img', ret='src')[0]
                title = item[1]
                addon.addDir(title, link, mode='Browse_Seasons', thumb=url + str(image), 
                             fanart=default_background, section='other', page=str(url))
    

def Browse_Seasons():

    url = params['url']
    section = params['section']
    page = params['page']
    img = params['img']
    
    if section == 'polecane':
        html = requests.get(url, timeout=15).content
        result = parseDOM(html, 'ul', attrs={'class': 'pmenu'})[1]
        
        result = parseDOM(result, 'li')
        for item in result:
            link = parseDOM(item, 'a', ret='href')[0]
            nazwa = parseDOM(item, 'a')[0]
            if "Kolejno" in str(nazwa):
                continue
            addon.addDir(str(nazwa), url + str(link), mode='List_Episodes', isFolder= True,
                        thumb=fanartAol, fanart=default_background, page=str(url), section='polecane')
    elif section == 'other':
        html = requests.get(url, timeout=15).content
        result = parseDOM(html, 'h1', attrs={'class': 'pod_naglowek'})
        if len(result) > 1:
            for item in result:
               addon.addDir(str(item), url, mode='List_Episodes', isFolder= True, 
                        thumb=str(img), fanart=default_background, page=str(item), section='multi')
        elif len(result) <= 1:
           
            List_Episodes()
    

def List_Episodes():

    url = params['url']
    section = params['section']
    page = params['page']
    img = params['img']
   
   
    ###   Listowanie Polecanych
    if section == 'polecane':
        result = requests.get(url).content
        result = parseDOM(result, 'table', attrs={'class': 'lista'})[0]
        result = parseDOM(result, 'tr', attrs={'class': 'lista_hover'})
        link = [page + parseDOM(item, 'a', ret='href')[0] for item in result]
        tytul = [str(parseDOM(item, 'img')[0]).split("</a>")[0] for item in result]
        data = [parseDOM(item, 'td', attrs={'class' : 'center'})[1] for item in result]
        for item in zip(link, tytul, data):
    
            addon.addLink(str(item[1]) + '  ' + str(item[2]), str(item[0]), mode='List_Links', 
                         thumb=fanartAol, fanart=default_background, page=str(page),
                         section='polecane')
            
    ####  Listowanie pozostalych z wieloma sezonami
    elif section == 'multi':
        result = requests.get(url).content
        slice = GetDataBeetwenMarkers(result, '<h1 class="pod_naglowek">' + page, '</table>', False)[1]
        results = parseDOM(slice, 'tr', attrs={'class': 'lista_hover'})
        tytul = [str(parseDOM(item, 'img')[0]).split('</td>')[0] for item in results]
        link = mainLink
        for item in tytul:
    
            addon.addLink(str(item), str(url), mode='List_Links', thumb=str(img),
                         fanart=default_background, page=str(page), section='multi',)
    ####  Listowanie pozostalych pojedynczych
    else:
        result = requests.get(url).content
        result = parseDOM(result, 'tr', attrs={'class': 'lista_hover'})
        tytul = [str(parseDOM(item, 'img')[0]).split('</td>')[0] for item in result]
        for item in tytul:
            addon.addLink(str(item), str(url), mode='List_Links', thumb=str(img),
                         fanart=default_background, page=str(page), section='other')
    
    
def List_Links():

    url = params['url']
    section = urllib.unquote_plus(params['section'])
    page = urllib.unquote_plus(params['page'])
    title = params['name']

    
    
    if section == 'polecane':
        result = requests.get(url).content
        result = parseDOM(result, 'table', attrs={'class': 'lista'})
        result = parseDOM(result, 'tr', attrs={'class': 'lista_hover'})

        status = [parseDOM(item, 'td', attrs={'class': 'center'})[1] for item in result]
        player = [parseDOM(item, 'td', attrs={'class': 'center'})[2] for item in result]
        tlumacz = [parseDOM(item, 'td', attrs={'class': 'center'})[3] for item in result]
        Player = []
        for item in zip(player, tlumacz):
            test = item[0] + '   ' + '[COLOR %s]%s[/COLOR]' % ('green', item[1])
            Player.append(test)
        kodlinku = [page + 'odtwarzacz-' + parseDOM(item, 'span', attrs={'class': 'odtwarzacz_link'}, ret='rel')[0] 
                    + '.html' for item in result]
        link = []
        for item in kodlinku:
            try:
                temp = requests.get(item).content
                if 'vk.com' in temp:
                    print 'vk'
                    l1 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='rel')[0]
                    l2 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='id')[0]
                    temp = 'https://vk.com/video' + l1 + '_' + l2
                else:
                    temp = parseDOM(temp, 'iframe', ret='src')[0]
                link.append(temp)
            except:
                continue
        addon.SourceSelect(Player, link, title)
        
    elif section == 'multi':
        result = requests.get(url).content
        slice = GetDataBeetwenMarkers(result, '<h1 class="pod_naglowek">' + page, '</table>', False)[1]
        results = [item for item in parseDOM(slice, 'tr', attrs={'class': 'lista_hover'}) if title in item]
        kodlinku = parseDOM(results, 'span', attrs={'class': 'odtwarzacz_link'}, ret='rel')

        link = []
        player = []
        for item in kodlinku:
            try:
                item = mainLink + 'odtwarzacz-' + item + '.html'
                temp = requests.get(item).content
                if 'vk.com' in temp:
                    print 'vk'
                    l1 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='rel')[0]
                    l2 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='id')[0]
                    temp = 'https://vk.com/video' + l1 + '_' + l2
                else:
                    temp = parseDOM(temp, 'iframe', ret='src')[0]
                link.append(temp)
                player.append('Oglądaj')
            except:
                continue
        addon.SourceSelect(players=player, links=link, title=title)
        
    elif section == 'other':
        result = requests.get(url).content
        results = [item for item in parseDOM(result, 'tr', attrs={'class': 'lista_hover'}) if title in item]
        kodlinku = parseDOM(results, 'span', attrs={'class': 'odtwarzacz_link'}, ret='rel')

        link = []
        player = []
        for item in kodlinku:
            try:
                item = mainLink + 'odtwarzacz-' + item + '.html'
                temp = requests.get(item).content
                if 'vk.com' in temp:
                    print 'vk'
                    l1 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='rel')[0]
                    l2 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='id')[0]
                    temp = 'https://vk.com/video' + l1 + '_' + l2
                else:
                    temp = parseDOM(temp, 'iframe', ret='src')[0]
                link.append(temp)
                player.append('Oglądaj')
            except:
                continue
        
        addon.SourceSelect(players=player, links=link, title=title)  


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
