# -*- coding: utf-8 -*-
###############################################################################
###############################################################################
# Wbijam.pl
# Some part of code from Huball
###############################################################################
###############################################################################
### Imports ###
import re
import sys
import requests
import urllib.parse
import xbmcaddon
import xbmc
import xbmcvfs
import xbmcplugin
import time
from resources.libs import addon_tools as addon
from resources.libs.CommonFunctions import parseDOM
#from CommonFunctions import parseDOM
from resources.libs import scraper
#from common import GetDataBeetwenMarkers

try:
    import json
except:
    import simplejson as json

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmcvfs.translatePath('special://home/addons/' + my_addon_id + '/resources/media/')

params = addon.get_params()
mainLink = 'https://inne.wbijam.pl/'
#media#
default_background = MEDIA + "fanart.jpg"
fanart = MEDIA + 'fanart.jpg'
nexticon = MEDIA + 'next.png'
fanartWb = MEDIA + 'wbijam.jpg'
host = 'Wbijam'


def Pagewbijam(url):

    result = requests.get(url, timeout=15).text
    
    if (len(url) == 0):
        return
    result = re.sub('>Menu główne', '', result)
    result = re.sub('>Reklama', '', result)
    data = [item for item in parseDOM(result, 'div', attrs={'class' : 'pmenu_naglowek_' + r'.'}) 
            if len(item)>0 ]
            
    if len(data) > 0:
        for item in data:
            name = item
                       
            addon.addDir(str(name), url, mode='Browse_Titles', thumb=fanartWb, fanart=default_background)

def Browse_Titles():

    url = params['url']
    name = params['name']
    html = requests.get(url, timeout=15).text
    if name in html:
        mark1 = '>' + name + '</div>'
        mark2 = '</ul>'

    data = GetDataBeetwenMarkers(html, mark1, mark2, False)[1]
    data = re.findall('<a href="(.+?)"(.+?)">(.+?)</a></li>', data)
    data.sort()
#####Polecane #######
    if len(data) > 0:  
        for item in data:
            if 'Anime online' in str(item[0]).lower():            
                continue
            elif 'inne.wbijam' in str(item[0]).lower():
                continue
            link = item[0]
            title = item[2]
            poster, fanart = scraper.Scrap(title, type='serie')
            if fanart == '':
                fanart = default_background
                      
            addon.addDir(title, link, mode='Browse_Seasons', thumb=str(poster), 
                         fanart=str(fanart), section='polecane', page=str(url), subdir=title)
#####Pozostałe###
    elif len(data) == 0:
            data2 = GetDataBeetwenMarkers(html, mark1, mark2, False)[1]
            data2 = re.findall('<a href="(.+?)">(.+?)</a></li>', data2)
            data2.sort()
            for item in data2:
                link = url + item[0]
                set = requests.get(link, timeout=15).text
                image = parseDOM([i for i in parseDOM(set,'center') if 'img' in i][0], 'img', ret='src')[0]
                title = item[1]
                addon.addDir(title, link, mode='Browse_Seasons', thumb=url + str(image), 
                             fanart=default_background, section='other', page=str(url), subdir=title)
    
def Browse_Seasons():

    url = params['url']
    section = params['section']
    page = params['page']
    img = params['img']
    subdir = params['subdir']
    
    if section == 'polecane':
        html = requests.get(url, timeout=15).text
        result = parseDOM(html, 'ul', attrs={'class': 'pmenu'})[1]
        
        result = parseDOM(result, 'li')
        for item in result:
            link = parseDOM(item, 'a', ret='href')[0]
            nazwa = parseDOM(item, 'a')[0]
            
            if "Kolejno" in str(nazwa):
                continue
            addon.addDir(str(nazwa), url + str(link), mode='List_Episodes', isFolder= True,
                        thumb=str(img), fanart=default_background, page=str(url), 
                        section='polecane', subdir= subdir + ' ' + nazwa)
    elif section == 'other':
        html = requests.get(url, timeout=15).text
        result = parseDOM(html, 'h1', attrs={'class': 'pod_naglowek'})
        if len(result) > 1:
            for item in result:
               
               addon.addDir(str(item), url, mode='List_Episodes', isFolder= True, 
                            thumb=str(img), fanart=default_background, page=str(item), 
                            section='multi', subdir=subdir + ' ' + str(item))
        elif len(result) <= 1:
           
            List_Episodes()
    

def List_Episodes():

    url = params['url']
    section = params['section']
    page = params['page']
    img = params['img']
    subdir = params['subdir']
   
    ###   Listowanie Polecanych
    if section == 'polecane':
        result = requests.get(url).text
        result = parseDOM(result, 'table', attrs={'class': 'lista'})[0]
        result = parseDOM(result, 'tr', attrs={'class': 'lista_hover'})
        link = [page + parseDOM(item, 'a', ret='href')[0] for item in result]
        tytul = [str(parseDOM(item, 'img')[0]).split("</a>")[0] for item in result]
        data = [parseDOM(item, 'td', attrs={'class' : 'center'})[1] for item in result]
        for item in zip(link, tytul, data):
    
            addon.addLink(str(item[1]), str(item[0]), mode='List_Links', 
                         thumb=img, fanart=default_background, page=str(page),
                         section='polecane', subdir=subdir, 
                         code='[B][COLOR=blue]%s[/COLOR][/B]' % str(item[2]))
        xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                                 label2Mask= '%P')    
    ####  Listowanie pozostalych z wieloma sezonami
    elif section == 'multi':
        result = requests.get(url).text
        slice = GetDataBeetwenMarkers(result, '<h1 class="pod_naglowek">' + page, '</table>', False)[1]
        results = parseDOM(slice, 'tr', attrs={'class': 'lista_hover'})
        tytul = [str(parseDOM(item, 'img')[0]).split('</td>')[0] for item in results]
        link = mainLink
        for item in tytul:
    
            addon.addLink(str(item), str(url), mode='List_Links', thumb=str(img),
                         fanart=default_background, page=str(page), section='multi',
                         subdir=subdir)
    ####  Listowanie pozostalych pojedynczych
    else:
        result = requests.get(url).text
        result = parseDOM(result, 'tr', attrs={'class': 'lista_hover'})
        tytul = [str(parseDOM(item, 'img')[0]).split('</td>')[0] for item in result]
        for item in tytul:
            addon.addLink(str(item), str(url), mode='List_Links', thumb=str(img),
                         fanart=default_background, page=str(page), section='other',
                         subdir=subdir)
    
def List_Links():

    url = params['url']
    section = urllib.parse.unquote_plus(params['section'])
    page = urllib.parse.unquote_plus(params['page'])
    title = params['name']
    subdir = urllib.parse.unquote_plus(params['subdir'])

    
    
    if section == 'polecane':
        result = requests.get(url).text
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
                temp = requests.get(item).text
                if 'vk.com' in temp:
                    
                    l1 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='rel')[0]
                    l2 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='id')[0]
                    temp = 'https://vk.com/video' + l1 + '_' + l2
                else:
                    temp = parseDOM(temp, 'iframe', ret='src')[0]
                link.append(temp)
                
            except:
                continue
        addon.SourceSelect(Player, link, title, subdir)
        
    elif section == 'multi':
        result = requests.get(url).text
        slice = GetDataBeetwenMarkers(result, '<h1 class="pod_naglowek">' + page, '</table>', False)[1]
        results = [item for item in parseDOM(slice, 'tr', attrs={'class': 'lista_hover'}) if title in item]
        kodlinku = parseDOM(results, 'span', attrs={'class': 'odtwarzacz_link'}, ret='rel')

        link = []
        player = []
        for item in kodlinku:
            try:
                item = mainLink + 'odtwarzacz-' + item + '.html'
                temp = requests.get(item).text
                if 'vk.com' in temp:

                    l1 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='rel')[0]
                    l2 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='id')[0]
                    temp = 'https://vk.com/video' + l1 + '_' + l2
                else:
                    temp = parseDOM(temp, 'iframe', ret='src')[0]
                link.append(temp)
                player.append('Oglądaj')
            except:
                continue
        addon.SourceSelect(players=player, links=link, title=title, subdir=subdir)
        
    elif section == 'other':
        result = requests.get(url).text
        results = [item for item in parseDOM(result, 'tr', attrs={'class': 'lista_hover'}) if title in item]
        kodlinku = parseDOM(results, 'span', attrs={'class': 'odtwarzacz_link'}, ret='rel')

        link = []
        player = []
        for item in kodlinku:
            try:
                item = mainLink + 'odtwarzacz-' + item + '.html'
                temp = requests.get(item).text
                if 'vk.com' in temp:
                    
                    l1 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='rel')[0]
                    l2 = parseDOM(temp, 'span',attrs={'class': 'odtwarzaj_vk'}, ret='id')[0]
                    temp = 'https://vk.com/video' + l1 + '_' + l2
                else:
                    temp = parseDOM(temp, 'iframe', ret='src')[0]
                link.append(temp)
                player.append('Oglądaj')
            except:
                continue
        
        addon.SourceSelect(players=player, links=link, title=title, subdir=subdir)  


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

