# -*- coding: UTF-8 -*-
import sys
import urllib.request, urllib.parse, urllib.error

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

#from common import PlayFromHost

from urllib.parse import parse_qs
my_addon = xbmcaddon.Addon()
Getsetting = my_addon.getSetting

def addDir(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='',
           genre='', year='', rating='', dateadded='', plot='',
           section='', page='', code='', studio='', subdir='', pic='',
           isFolder=True, total=1):
    u = (sys.argv[0] + '?url=' + urllib.parse.quote_plus(url) + '&mode=' + str(mode) + '&name='
         + urllib.parse.quote_plus(name) + '&img=' + urllib.parse.quote_plus(thumb)
         + '&section=' + urllib.parse.quote_plus(section) + '&page=' + urllib.parse.quote_plus(page)
         + '&subdir=' + urllib.parse.quote_plus(subdir) + '&pic=' + urllib.parse.quote_plus(fanart))
    liz = xbmcgui.ListItem(name)
    contextmenu = []
    contextmenu.append(('Informacja', 'Action(Info)'), )    
    info = {
        'title': name,
        'genre': genre,
        'year': year,
        'rating': rating,
        'dateadded': dateadded,
        'plot': plot,
        'code': code,
        'studio': studio
    }
    liz.setInfo(type='video', infoLabels=info)
    liz.setArt({
        'thumb': thumb,
        'icon': icon,
        'fanart': fanart,
        'poster': poster,
        'banner': banner,
        'clearart': clearart,
        'clearlogo': clearlogo,
    })
    liz.addContextMenuItems(contextmenu)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,
                                isFolder=isFolder, totalItems=total)

def addLink(name, url, mode='', icon='', thumb='', fanart='', poster='',
            banner='', clearart='', clearlogo='', genre='', year='',
            rating='', dateadded='', plot='', code='', studio='', pic='',
            isFolder=False, total=1,
            type='video', section='', page='', subdir=''):
            
    u = (sys.argv[0] + '?url=' + urllib.parse.quote_plus(url) + '&mode=' + str(mode)
         + '&name=' + urllib.parse.quote_plus(name) + '&img=' + urllib.parse.quote_plus(thumb)
         + '&section=' + urllib.parse.quote_plus(section) + '&page=' + urllib.parse.quote_plus(page)
         + '&subdir=' + urllib.parse.quote_plus(subdir) + '&pic=' + urllib.parse.quote_plus(fanart))
    liz = xbmcgui.ListItem(name)
    contextmenu = []
    contextmenu.append(('Informacja', 'Action(Info)'), )
    info = {
        'title': name,
        'plot': plot,
        'code': code,
        'studio': studio,
        'genre': genre,
        'rating': rating,
        'year': year,
        'dateadded': dateadded,
    }
    liz.setProperty('IsPlayable', 'true')
    liz.setInfo(type, infoLabels=info)
    liz.setArt({
        'thumb': thumb,
        'icon': icon,
        'fanart': fanart,
        'poster': poster,
        'banner': banner,
        'clearart': clearart,
        'clearlogo': clearlogo
    })

    liz.addContextMenuItems(contextmenu)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,
                                isFolder=isFolder, totalItems=total)

def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, vv[0]) for k, vv in parse_qs(paramstring).items())

def endOfDir():
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def PlayFromHost(url, mode, title, subdir):
       
    if 'google' in url:
        url = url.replace('preview', 'view')
    import resolveurl
    try:
        if ('youtube' in url):
            if mode == 'play':
                li = xbmcgui.ListItem(title, path=url)
                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
            elif mode == 'download':
                from resources.libs import downloader
                dest = Getsetting("download.path")
                downloader.download(title, 'image', url, dest, subdir)
        else:
            try:
                stream_url = resolveurl.resolve(url)
                xbmc.log('ANIME OTAKU | wynik z resolve  : %s' % str(stream_url), xbmc.LOGINFO)
                xbmc.log('Anime Otaku | wynik mode: %s' % mode, xbmc.LOGINFO)
                if mode == 'play':
                    li = xbmcgui.ListItem(title, path=str(stream_url))
                    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
                elif mode == 'download':
                
                    from resources.libs import downloader
                    dest = Getsetting("download.path")
                    downloader.download(title, 'image', stream_url, dest, subdir)
            except:
                pass
    except:
        d = xbmcgui.Dialog()
        d.notification('Anime Otaku ', 
                       '[COLOR red]Problem  -  Nie można wyciągnąć linku[/COLOR]', 
                       xbmcgui.NOTIFICATION_INFO, 5000)
    
def SourceSelect(players, links, title, subdir):
#Anime Otaku modification

    xbmc.log('Anime Otaku | wynik subdir: %s' % subdir, xbmc.LOGINFO)
    if len(players) > 0:
        d = xbmcgui.Dialog()
        select = d.select('Wybór playera', players)
        if select > -1:
            link = links[select]
            if 'api4.shinden.pl' in str(link):
                from hosts.hostanimeshinden import ShindenGetVideoLink
                link = ShindenGetVideoLink(link)
            elif 'strefadb.pl/videoredirect' in str(link):
                from hosts.hostdragon import GetDragonVideolink
                link = GetDragonVideolink(link)
            xbmc.log('Anime Otaku.pl | Proba z : %s' % players[select] + '   ' + link + '  ', xbmc.LOGINFO)
            if Getsetting('download.opt') == 'true':
                ret = d.yesno('Downloader', 'Select option', 'Watch', 'Download')
                if ret:
                    mode = 'download'
                else:
                    mode = 'play'
            else:
                mode = 'play'
                
            PlayFromHost(link, mode=mode, title=title, subdir=subdir)

        else:
            exit()
    else:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Brak linków')
