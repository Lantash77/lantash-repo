# -*- coding: utf-8 -*-

### Imports ###
import re
import os
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
#from resources.libs.addon_comm import Addon

#from addon.common.addon import Addon  # może trzeba więcej
#from addon.common.net import Net  # może trzeba więcej
try:
    import json
except:
    import simplejson as json
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

##########
my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')

PATH = my_addon.getAddonInfo('path')
skinPath = xbmc.translatePath('special://skin/')
dataPath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))


iconFav = ''

#_addon = Addon(my_addon_id, sys.argv)
_artIcon = my_addon.getAddonInfo('icon')
_artFanart = my_addon.getAddonInfo('fanart')
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
sys.path.append(os.path.join(PATH, 'resources/libs'))
skinPath = xbmc.translatePath('special://skin/')
dataPath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8')


######code from lambda's Exodus addon######
def addView(content):
    try:
        xml = os.path.join(skinPath, 'addon.xml')
        file = xbmcvfs.File(xml)
        read = file.read().replace('\n', '')
        file.close()
        try:
            src = re.compile('defaultresolution="(.+?)"').findall(read)[0]
        except:
            src = re.compile('<res.+?folder="(.+?)"').findall(read)[0]
        src = os.path.join(skinPath, src)
        src = os.path.join(src, 'MyVideoNav.xml')
        file = xbmcvfs.File(src)
        read = file.read().replace('\n', '')
        file.close()
        views = re.compile('<views>(.+?)</views>').findall(read)[0]
        views = [int(x) for x in views.split(',')]
        for view in views:
            label = xbmc.getInfoLabel('Control.GetLabel(%s)' % (view))
            if not (label == '' or label == None):
                break
        record = (xbmc.getSkinDir(), content, str(view))
        xbmcvfs.mkdir(dataPath)
        dbcon = database.connect(os.path.join(dataPath, 'views.db'))
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS views (""skin TEXT, ""view_type TEXT, ""view_id TEXT, ""UNIQUE(skin, view_type)"");")
        dbcur.execute("DELETE FROM views WHERE skin = '%s' AND view_type = '%s'" % (record[0], record[1]))
        dbcur.execute("INSERT INTO views Values (?, ?, ?)", record)
        dbcon.commit()
        viewName = xbmc.getInfoLabel('Container.Viewmode')
        myNote('Ustawiono widok: %s' % viewName)
    except:
        return


def set_view(content='none', view_mode=50, do_sort=False):
    h = int(sys.argv[1])
    if (content is not 'none'):
        xbmcplugin.setContent(h, content)
    if (tfalse(addst("auto-view")) == True):
            try:
                record = (xbmc.getSkinDir(), content)
                dbcon = database.connect(os.path.join(dataPath, 'views.db'))
                dbcur = dbcon.cursor()
                dbcur.execute("SELECT * FROM views WHERE skin = '%s' AND view_type = '%s'" % (record[0], record[1]))
                view = dbcur.fetchone()
                view = view[2]
                if view == None:
                    raise Exception()
                xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
            except:
                return
######


def byteify(input):
    if isinstance(input, dict):
        return dict([(byteify(key), byteify(value)) for key, value in input.iteritems()])
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def addpr(r, s=''):
    return my_addon.getSetting(r, s)


def addst(r, s=''):

    return my_addon.getSetting(r)

#loginGoogle = addst('username3', '')
#passwordGoogle = addst('password3', '')


def tfalse(r, d=False):
    if   (r.lower() == 'true') or (r.lower() == 't') or (r.lower() == 'y') or (r.lower() == '1') or (r.lower() == 'yes'):
        return True
    elif (r.lower() == 'false') or (r.lower() == 'f') or (r.lower() == 'n') or (r.lower() == '0') or (r.lower() == 'no'):
        return False
    else:
        return d


def iFL(t):
    return '[I]' + t + '[/I]'  # For Italic Text ###


def bFL(t):
    return '[B]' + t + '[/B]'  # For Bold Text ###


def cFL(t, c='cornflowerblue'):
    return '[COLOR ' + c + ']' + t + '[/COLOR]'  # For Coloring Text ###


def cFL_(t, c='cornflowerblue'):
    return '[COLOR ' + c + ']' + t[0:1] + '[/COLOR]' + t[1:]  # For Coloring Text (First Letter-Only) ###





def myNote(header='', msg='', delay=5000, image=iconFav):
    xbmc.executebuiltin('XBMC.Notification("%s","%s",%d,"%s")' %
                        (header, msg, delay, image))

def eod():
    xbmcplugin.endOfDirectory(int(sys.argv[1]))



# tekstowe

def CleanHTML(html):
    if ("&amp;" in html):
        html = html.replace('&amp;', '&')
    if ("&nbsp;" in html):
        html = html.replace('&nbsp;', '')
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
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')


    return html


def ParseDescription(plot):
    if ("&amp;" in plot):
        plot = plot.replace('&amp;', '&')
    if ("&nbsp;" in plot):
        plot = plot.replace('&nbsp;', '')
    if ('&#' in plot) and (';' in plot):
        if ("&#8211;" in plot):
            plot = plot.replace("&#8211;", "-")
        if ("&#8216;" in plot):
            plot = plot.replace("&#8216;", "'")
        if ("&#8217;" in plot):
            plot = plot.replace("&#8217;", "'")
        if ("&#8220;" in plot):
            plot = plot.replace('&#8220;', '"')
        if ("&#8221;" in plot):
            plot = plot.replace('&#8221;', '"')
        if ("&#215;" in plot):
            plot = plot.replace('&#215;', 'x')
        if ("&#x27;" in plot):
            plot = plot.replace('&#x27;', "'")
        if ("&#xF4;" in plot):
            plot = plot.replace('&#xF4;', "o")
        if ("&#xb7;" in plot):
            plot = plot.replace('&#xb7;', "-")
        if ("&#xFB;" in plot):
            plot = plot.replace('&#xFB;', "u")
        if ("&#xE0;" in plot):
            plot = plot.replace('&#xE0;', "a")
        if ("&#0421;" in plot):
            plot = plot.replace('&#0421;', "")
        if ("&#xE9;" in plot):
            plot = plot.replace('&#xE9;', "e")
        if ("&#xE2;" in plot):
            plot = plot.replace('&#xE2;', "a")
        if ("&#038;" in plot):
            plot = plot.replace('&#038;', "&")
        if ('&#' in plot) and (';' in plot):
            try:
                matches = re.compile('&#(.+?);').findall(plot)
            except:
                matches = ''
            if (matches is not ''):
                for match in matches:
                    if (match is not '') and (match is not ' ') and ("&#" + match + ";" in plot):
                        try:
                            plot = plot.replace("&#" + match + ";", "")
                        except:
                            pass
    for i in xrange(127, 256):
        try:
            plot = plot.replace(chr(i), "")
        except:
            pass
    return plot


def messupText(t):
    return t



def clean_html(html):
    """Clean an HTML snippet into a readable string"""
    if type(html) == type(u''):
        strType = 'unicode'
    elif type(html) == type(''):
        strType = 'utf-8'
        html = html.decode("utf-8")
    # Newline vs <br />
    html = html.replace('\n', ' ')
    html = re.sub(r'\s*<\s*br\s*/?\s*>\s*', '\n', html)
    html = re.sub(r'<\s*/\s*p\s*>\s*<\s*p[^>]*>', '\n', html)
    # Strip html tags
    html = re.sub('<.*?>', '', html)
    if strType == 'utf-8':
        html = html.encode("utf-8")
    return html.strip()


def PlayFromHost(url, mode, page=''):
    infoLabels = {"Studio": addpr('studio', ''), "ShowTitle": addpr('showtitle', ''), "Title": addpr('title', '')}
    title = addpr('title', '')
    if mode == 'download'and (addst("download.path") == ''):
            dialog = xbmcgui.Dialog()
            dialog.notification('Download', 'Download patch is empty', xbmcgui.NOTIFICATION_INFO, 5000)
            return
    if 'google' in url:
        url = url.replace('preview', 'view')
    import resolveurl
    #infoLabels = {"Studio": addpr('studio', ''), "ShowTitle": addpr('showtitle', ''), "Title": addpr('title', '')}
    try:
        if ('youtube' in url):
            if mode == 'play':
                li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=url)
                li.setInfo(type='video', infoLabels=infoLabels)
                li.setProperty('IsPlayable', 'true')
                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
            elif mode == 'download':
                import downloader
                dest = addst("download.path")
                downloader.download(title, 'image', url, dest)
        elif 'anime-centrum' in url:
            stream_url = url + "|Referer=http://anime-centrum.pl/"
            li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=stream_url)
            li.setInfo(type='video', infoLabels=infoLabels)
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
        else:
            try:
                stream_url = resolveurl.resolve(url)
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
                if 'vidlox' in url:
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
                    li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=stream_url)
                    li.setInfo(type='video', infoLabels=infoLabels)
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
                elif mode == 'download':
                    import downloader
                    dest = addst("download.path")
                    downloader.download(title, 'image', stream_url, dest)
    except:
        #myNote("Nie udało się niestety :( BUUUUU")
        print 'Nie udało się niestety :( BUUUUU'


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


# This function raises a keyboard for user input
def getUserInput(title=u"Input", default=u"", hidden=False):
    result = None
    # Fix for when this functions is called with default=None
    if not default:
        default = u""
    keyboard = xbmc.Keyboard(default, title)
    keyboard.setHiddenInput(hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        result = keyboard.getText()
    return result
