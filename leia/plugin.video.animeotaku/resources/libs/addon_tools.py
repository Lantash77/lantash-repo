# -*- coding: UTF-8 -*-
import sys
import urllib

import xbmc
import xbmcgui
import xbmcplugin

#from resources.libs.debug import log_exception
#from common import PlayFromHost

reload(sys)
sys.setdefaultencoding('UTF8')

PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import parse_qs
else:
    from urllib.parse import parse_qs


def addDir(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', 
           clearart='', clearlogo='', genre='',
           year='', rating='', dateadded='', plot='', isFolder=True, total=1, 
           section='', contextmenu=[], page=''):
    u = (sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name='
         + urllib.quote_plus(name) + '&img=' + urllib.quote_plus(thumb)
         + '&section=' + urllib.quote_plus(section) + '&page=' + urllib.quote_plus(page))
    liz = xbmcgui.ListItem(name)
    info = {
        'title': name,
        'genre': genre,
        'year': year,
        'rating': rating,
        'dateadded': dateadded,
        'plot': plot,
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
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)


def addLink(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', 
            clearart='', clearlogo='', genre='',
            year='', rating='', dateadded='', plot='', isFolder=False, total=1, 
            type='video', section='', contextmenu=[], page=''):
    u = (sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
         + '&name=' + urllib.quote_plus(name) + '&img=' + urllib.quote_plus(thumb)
         + '&section=' + urllib.quote_plus(section)+ '&page=' + urllib.quote_plus(page))
    liz = xbmcgui.ListItem(name)

    contextmenu.append(('Informacja', 'XBMC.Action(Info)'), )
    info = {
        'title': name,
        'plot': plot,
        'code': 'Test',
        'studio': 'test studio',
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
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    


def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, vv[0]) for k, vv in parse_qs(paramstring).items())


def endOfDir():
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    

def PlayFromHost(url, mode, title):
       
    if 'google' in url:
        url = url.replace('preview', 'view')
    import resolveurl
    try:
        if ('youtube' in url):
            if mode == 'play':
                li = xbmcgui.ListItem(title, path=url)
                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
            elif mode == 'download':
                import downloader
                dest = addst("download.path")
                downloader.download(title, 'image', url, dest)
        else:
            try:
                stream_url = resolveurl.resolve(url)
                xbmc.log('ANIME TEST | wynik z resolve  : %s' % str(stream_url), xbmc.LOGNOTICE)
                
                if mode == 'play':
                    li = xbmcgui.ListItem(title, path=str(stream_url))
                    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
                elif mode == 'download':
                    import downloader
                    dest = addst("download.path")
                    downloader.download(title, 'image', stream_url, dest)
            except:
                pass
   
    except:
        d = xbmcgui.Dialog()
        d.notification('dramaqueen.pl ', 
                       '[COLOR red]Problem  -  Nie można wyciągnąć linku[/COLOR]', 
                       xbmcgui.NOTIFICATION_INFO, 5000)

    
def SourceSelect(players, links, title):
    if len(players) > 0:
        d = xbmcgui.Dialog()
        select = d.select('Wybór playera', players)
        if select > -1:
            link = links[select]
            if 'api4.shinden.pl' in str(link):
                from hosts.hostanimeshinden import ShindenGetVideoLink
                link = ShindenGetVideoLink(link)
            xbmc.log('Anime Otaku.pl | Proba z : %s' % players[select] + '   ' + link + '  ', xbmc.LOGNOTICE)
            PlayFromHost(link, mode='play', title=title)

        else:
            exit()
    else:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Brak linków', '')
