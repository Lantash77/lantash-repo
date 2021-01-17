# -*- coding: UTF-8 -*-
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from resources.libs.debug import log_exception
from common import PlayFromHost

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
    liz.setArt({
        'thumb': thumb,
        'icon': icon,
        'fanart': fanart,
        'poster': poster,
        'banner': banner,
        'clearart': clearart,
        'clearlogo': clearlogo,
    })
    liz.setInfo('Video', {
         'title': name, 
         'genre': genre, 
         'year': year, 
         'rating': rating, 
         'dateadded': dateadded, 
         'plot': plot
    })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)


def addLink(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='', genre='',
            year='', rating='', dateadded='', plot='', isFolder=False, total=1, type='video'):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name) + '&img=' + urllib.quote_plus(thumb)
    liz = xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'true')
    liz.setInfo(type, {
        'title': name,
        'plot': plot
    })
    liz.setArt({
        'thumb': thumb,
        'icon': icon,
        'fanart': fanart,
        'poster': poster,
        'banner': banner,
        'clearart': clearart,
        'clearlogo': clearlogo
    })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)


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
