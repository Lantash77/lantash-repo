# -*- coding: UTF-8 -*-
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin


reload(sys)
sys.setdefaultencoding('UTF8')

PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import parse_qs
else:
    from urllib.parse import parse_qs


def addDir(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='', genre='',
           year='', rating='', dateadded='', plot='', isFolder=True, total=1):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name) + '&img=' + urllib.quote_plus(thumb)
    liz = xbmcgui.ListItem(name)
    info = {
        'title': name, 
         'genre': genre, 
         'year': year, 
         'rating': rating, 
         'dateadded': dateadded, 
         'plot': plot,
    }
    liz.setInfo( type='video', infoLabels = info)
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


def addLink(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='', genre='',
            year='', rating='', dateadded='', plot='', isFolder=False, total=1, type='video'):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name) + '&img=' + urllib.quote_plus(thumb)
    liz = xbmcgui.ListItem(name)
    contextmenu = []
    contextmenu.append(('Informacja', 'XBMC.Action(Info)'),)
    info = {
        'title': name,
        'plot': plot,
        'code': 'Test',
        'studio': 'test studio',
    }
    liz.setProperty('IsPlayable', 'true')
    liz.setInfo( type, infoLabels = info)
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
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, vv[0]) for k, vv in parse_qs(paramstring).items())

def PlayFromHost(url, mode, title):

    
    if 'google' in url:
        url = url.replace('preview', 'view')
    import resolveurl
    try:
        if ('youtube' in url):
            if mode == 'play':
                li = xbmcgui.ListItem(title, path=url)
                li.setInfo(type='video')
                li.setProperty('IsPlayable', 'true')
                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
            elif mode == 'download':
                import downloader
                dest = addst("download.path")
                downloader.download(title, 'image', url, dest)
        else:
            try:
                stream_url = resolveurl.resolve(url)
                xbmc.log('DramaQueen.pl | wynik z resolve  : %s' % stream_url, xbmc.LOGNOTICE)
                
                if mode == 'play':
                    li = xbmcgui.ListItem(title, path=str(stream_url))
                
                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
                elif mode == 'download':
                    import downloader
                    dest = addst("download.path")
                    downloader.download(title, 'image', stream_url, dest)
            except:
                if 'sibnet' in url:
                    stream_url = sibnet(url)
                    stream_url = stream_url + "|Referer=https://video.sibnet.ru"
                if mode == 'play':
                    li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=stream_url)
                    li.setInfo(type='video', infoLabels=infoLabels)
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
                elif mode == 'download':
                    import downloader
                    dest = addst("download.path")
                    downloader.download(title, 'image', stream_url, dest)
    except:
        print 'Brak linku'

def SourceSelect(players, links, title):
    if len(players) > 0:
        d = xbmcgui.Dialog()
        select = d.select('Wybór playera', players)
        if select > -1:
            link = str(links[select])
            xbmc.log('DramaQueen.pl | Proba z : %s' % players[select] + '   ' + link + '  ', xbmc.LOGNOTICE)
            PlayFromHost(link, mode='play', title=title)

        else:
            exit()
    else:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Brak linków', '')
