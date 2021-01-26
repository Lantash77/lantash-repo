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
from resources.libs.addon_comm import Addon  # może trzeba więcej

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

addonPath = my_addon.getAddonInfo('path')
iconFav = xbmcaddon.Addon(id="plugin.video.dramaqueen").getAddonInfo('path') + '/art/favorites.png'

_addon = Addon('plugin.video.dramaqueen', sys.argv)
_artIcon = _addon.get_icon()
_artFanart = _addon.get_fanart()
sys.path.append(os.path.join(addonPath, 'resources/libs'))
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
    return _addon.queries.get(r, s)


def addst(r, s=''):
    return _addon.get_setting(r)

loginGoogle = addst('username3', '')
passwordGoogle = addst('password3', '')


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
    _addon.show_small_popup(title=header, msg=msg, delay=delay, image=image)


def eod():
    _addon.end_of_directory()



# tekstowe


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


def messupText(t, _html=False, _ende=False, _a=False, Slashes=False):
    if (_html == True):
        try:
            t = HTMLParser.HTMLParser().unescape(t)
        except:
            t = t
        try:
            t = ParseDescription(t)
        except:
            t = t
    if (_ende == True):
        try:
            t = t.encode('ascii', 'ignore')
            t = t.decode('iso-8859-1')
        except:
            t = t
    if (_a == True):
        try:
            t = _addon.decode(t)
            t = _addon.unescape(t)
        except:
            t = t
    if (Slashes == True):
        try:
            t = t.replace('_', ' ')
        except:
            t = t
    return t


def html_entity_decode_char(m):
        ent = m.group(1)
        if ent.startswith('x'):
            return unichr(int(ent[1:], 16))
        try:
            return unichr(int(ent))
        except:
            if ent in htmlentitydefs.name2codepoint:
                return unichr(htmlentitydefs.name2codepoint[ent])
            else:
                return ent


def html_entity_decode(string):
    string = string.decode('UTF-8')
    s = re.compile("&#?(\w+?);").sub(html_entity_decode_char, string)
    return s.encode('UTF-8')


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


def video_google(url):
    try:
        if (tfalse(addst("googlelog")) == True):
            logged_in = weblogingoogle.doLogin(addonPath, loginGoogle, passwordGoogle)
        url = nURL(url)
        url = re.compile('"fmt_stream_map",(".+?")').findall(url)[0]
        url = json.loads(url)
        url = [i.split('|')[-1] for i in url.split(',')]
        if url == []:
            return
        try:
            url = [i for i in url if not any(x in i for x in ['&itag=43&', '&itag=35&', '&itag=34&', '&itag=5&'])][0]
        except:
            url = url[0]
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def vidfile(url):
    try:
        url = nURL(url)
        print url
        HD = re.compile('<source src="(.+?)" type=""></source>').findall(url)[0]
        if HD == []:
            return
        url = HD
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def mp4upload(url, page):
    import time
    try:
        import requests
        headers = {
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'http://senpai.com.pl/anime/Yuri^!^!^!^%^20on^%^20Ice/12.0',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
}
        s = requests.Session()
        r = s.get('http://senpai.com.pl/anime/Yuri!!!%20on%20Ice/12.0', headers=headers)
        time.sleep(5)
        r = requests.get(url,  headers=headers, cookies=s.cookies )
        data = r.text
        print data
        data = GetDataBeetwenMarkers(data, "</video>", '</script>', False)[1]
        host = GetDataBeetwenMarkers(data, "mp4|", '|www', False)[1]
        token = GetDataBeetwenMarkers(data, "quot||", '|', False)[1]
        url = 'https://' + host + '.mp4upload.com:282/d/' + token + '/video.mp4'
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def sibnet(url):
    try:
        url = nURL(url)
        HD = re.compile(',{src: "(.+?)"').findall(url)[0]
        if HD == []:
            return
        url = 'https://video.sibnet.ru' + HD
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def vk_vk(url):
    try:
        url = nURL(url)
        HD = re.compile('url720=(.+?)&').findall(url)[0]
        if HD == []:
            return
        url = HD
        url = url.replace('https://', 'http://')
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def vshare(url):
    try:
        url = nURL(url)
        HD = re.compile('url":"(.+?).flv').findall(url)[0]
        if HD == []:
            return
        url = HD + '.flv'
        url = url.replace('/', '')
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def dailymotion(url):
    try:
        if not url.startswith('http://www.dailymotion.com/embed/video/'):
            url = 'http://www.dailymotion.com/embed/video/' + url.split('/')[-1][0:7]
        data = nURL(url)
        match = re.compile('"stream_h264.+?url":"(http[^"]+?H264-)([^/]+?)(/[^"]+?)"').findall(data)
        for i in range(len(match)):
            url = match[i][0] + match[i][1] + match[i][2]
            url = url.replace('\/', "/")
            return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def animeuploader(url):
    url = nURL(url)
    try:
        HD = re.compile("{file: '(.+?)',").findall(url)[0]
        if HD == []:
            return
        url = HD
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def animeonline(url):
    url = nURL(url)
    try:
        HD = re.compile('<source src="(.+?)"').findall(url)[0]
        if HD == []:
            return
        url = HD
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def tune(url):
    url = url.replace('http://tune.pk/player/embed_player.php?vid=', '')
    url = 'http://embed.tune.pk/play/%s?autoplay=no&ssl=no' % url
    url = nURL(url)
    try:
        HD = re.compile('file":"(.+?).mp4').findall(url)[0]
        if HD == []:
            return
        url = HD + '.mp4'
        url = url.replace('/', '')
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def vidlox(url):
    url = nURL(url)
    try:
        HD = re.compile(',"https://(.+?).mp4"').findall(url)[0]
        if HD == []:
            return
        url = "https://" + HD + ".mp4"
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def rapidvideo(url):
    url = nURL(url)
    try:
        HD = re.compile('"sources": \[{"file":"https:(.+?).mp4').findall(url)[0]
        if HD == []:
            return
        url = "https://" + HD + ".mp4"
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def bitporno(url):
    url = url.replace('http', 'https')
    url = nURL(url)
    print url
    try:
        HD = re.compile('<source src="(.+?)" type="video/mp4" data-res="720p">').findall(url)[0]
        if HD == []:
            return
        url = HD
        return url
    except:
        myNote("Failed to Resolve Playable URL.")
        return


def cloudvideo(url):
    import requests
    import re
    try:
        r = requests.get(url)
        text = r.text
        HD = re.compile('<source src="(.+?),(.+?),(.+?),(.+?),').findall(text)
        ItemCount = len(HD)
        if ItemCount > 0:
            for item in HD:
                strona = item[0]+item[3]+'/index-v1-a1.m3u8'
        else:
            HD = re.compile('<source src="(.+?),(.+?),(.+?),').findall(text)
            for item in HD:
                strona = item[0]+item[2]+'/index-v1-a1.m3u8'
        return strona
    except:
        myNote("Failed to Resolve Playable URL from cloudvideo")
        return


#def PlayFromHost(url, mode, page=''):
#    infoLabels = {"Studio": addpr('studio', ''), "ShowTitle": addpr('showtitle', ''), "Title": addpr('title', '')}
#    title = addpr('title', '')
#    if mode == 'download'and (addst("download.path") == ''):
#            dialog = xbmcgui.Dialog()
#            dialog.notification('Download', 'Download patch is empty', xbmcgui.NOTIFICATION_INFO, 5000)
#            return
#    if 'google' in url:
#        url = url.replace('preview', 'view')
#    import resolveurl
#    #infoLabels = {"Studio": addpr('studio', ''), "ShowTitle": addpr('showtitle', ''), "Title": addpr('title', '')}
#    try:
#        if ('youtube' in url):
#            if mode == 'play':
#                li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=url)
#                li.setInfo(type='video', infoLabels=infoLabels)
#                li.setProperty('IsPlayable', 'true')
#                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
#            elif mode == 'download':
#                import downloader
#                dest = addst("download.path")
#                downloader.download(title, 'image', url, dest)
#        elif 'anime-centrum' in url:
#            stream_url = url + "|Referer=http://anime-centrum.pl/"
#            li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=stream_url)
#            li.setInfo(type='video', infoLabels=infoLabels)
#            li.setProperty('IsPlayable', 'true')
#            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
#        else:
#            try:
#                stream_url = resolveurl.resolve(url)
#                if mode == 'play':
#                    li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=stream_url)
#                    li.setInfo(type='video', infoLabels=infoLabels)
#                    li.setProperty('IsPlayable', 'true')
#                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
#                elif mode == 'download':
#                    import downloader
#                    dest = addst("download.path")
#                    downloader.download(title, 'image', stream_url, dest)
#            except:
#                if 'vidlox' in url:
#                    stream_url = vidlox(url)
#                elif 'rapidvideo' in url:
#                    stream_url = rapidvideo(url)
#                elif 'mp4upload' in url:
#                    stream_url = mp4upload(url, page)
#                elif 'bitporno.com' in url:
#                    stream_url = bitporno(url)
#                elif 'cloudvideo' in url:
#                    stream_url = cloudvideo(url)
#                elif 'sibnet' in url:
#                    stream_url = sibnet(url)
#                    stream_url = stream_url + "|Referer=https://video.sibnet.ru"
#                if mode == 'play':
#                    li = xbmcgui.ListItem(addpr('title', ''), iconImage=addpr('img', ''), thumbnailImage=addpr('img', ''), path=stream_url)
#                    li.setInfo(type='video', infoLabels=infoLabels)
#                    li.setProperty('IsPlayable', 'true')
#                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
#                elif mode == 'download':
#                    import downloader
#                    dest = addst("download.path")
#                    downloader.download(title, 'image', stream_url, dest)
#    except:
#        #myNote("Nie udało się niestety :( BUUUUU")
#        print 'Brak linku'
#
#
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
                #    li.setInfo(type='video')
                #    li.setProperty('IsPlayable', 'true')
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
