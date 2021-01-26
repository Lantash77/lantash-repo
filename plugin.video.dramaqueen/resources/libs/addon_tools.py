# -*- coding: UTF-8 -*-
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from resources.libs.debug import log_exception
#from common import PlayFromHost

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


def PlayMedia(link, direct=False):
    try:
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Odtwarzanie', 'Odpalanie linku...')
        if 'rtmp' in link:
            url = link
        elif direct:
            url = link
        else:
            import resolveurl
            url = resolveurl.resolve(link)
        if url is False:
            raise ValueError('Nie udało się wyciągnąć linku')
        pDialog.close()
        li = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    except Exception as e:
        pDialog.close()
        xbmcgui.Dialog().ok('Error', 'Błąd otwarcia linku! %s' % e)
        log_exception()

def PlayFromHost(url, mode, title):
        
#    title = addpr('title', '')
    
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
                    li = xbmcgui.ListItem(title, path=stream_url)
                
                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
                elif mode == 'download':
                    import downloader
                    dest = addst("download.path")
                    downloader.download(title, 'image', stream_url, dest)
            except:
                if 'vidloxxx' in url:
                    stream_url = vidlox(url)
                elif 'rapidvideo' in url:
                    stream_url = rapidvideo(url)
                elif 'mp4upload' in url:
                    stream_url = mp4upload(url, page)
                elif 'bitporno.com' in url:
                    stream_url = bitporno(url)
                elif 'cloudvideo' in url:
                    stream_url = cloudvideo(url)
                elif 'sibnet' in url:
                    stream_url = sibnet(url)
                    stream_url = stream_url + "|Referer=https://video.sibnet.ru"
                if mode == 'play':
                    li = xbmcgui.ListItem(title, path=stream_url)
                    li.setInfo(type='video')
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
                elif mode == 'download':
                    import downloader
                    dest = addst("download.path")
                    downloader.download(title, 'image', stream_url, dest)
    except:
        #myNote("Nie udało się niestety :( BUUUUU")
        print 'Brak linku'



def SourceSelect(players, links, title):
    if len(players) > 0:
        d = xbmcgui.Dialog()
        select = d.select('Wybór playera', players)
        if select > -1:
            link = links[select]
            xbmc.log('DramaQueen.pl | Proba z : %s' % players[select] + '   ' + link + '  ', xbmc.LOGNOTICE)
            PlayFromHost(link, mode='play', title=title)

        else:
            exit()
    else:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Brak linków', '')
