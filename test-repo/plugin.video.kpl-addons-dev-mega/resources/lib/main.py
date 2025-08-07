

import sys
from urllib.parse import parse_qsl, urlencode
import xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
#import cdaresolver
from getstream import get_mega_stream
import cache

my_addon = xbmcaddon.Addon()
addonInfo = xbmcaddon.Addon().getAddonInfo
GetSetting = my_addon.getSetting
SetSetting = my_addon.setSetting
dataPath = xbmcvfs.translatePath(addonInfo('profile'))# or r'D:\drop\python_drop'#r'/home/lantash/drop'#
params = dict(parse_qsl(sys.argv[2].replace("?", "")))
#import sys
#sys.path.append("C:\Program Files\JetBrains\PyCharm 2022.2.2\debug-eggs\pydevd-pycharm.egg")
#import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
try:
    addon_handle = int(sys.argv[1])
except IndexError:
    addon_handle = 0

"""
url_list can be updated with new links from mega.nz.
in format to generate more or different test urls:
    [
        ['name1', 'url1'],
        ['name2', 'url2']
    ]
"""
url_list = [
    ['15 min low q', 'https://mega.nz/file/IN0nHa4T#q4AFUWHH8K-BjOxCwv0GJfllUEIDRYF4fQvCwftjkbw'],
    ['1hr 480p - city hunter', 'https://mega.nz/file/4F1FzZ6B#MJWyxU9r8VrM63NE_UVnxX_B-Cc7gb11NCEv8OeG0QY'],
    ['1hr 720p - bride of water god', 'https://mega.nz/file/j3xxwIKT#f2eYEJxEluuKMxn3dIcMA-ve27y3nGkPYY9S2bM-abI'],

    ]

def main_menu():

    for name, url in url_list:
        addItem(name, url, 'play', isFolder=False)


def play():

    #import cdaresolver as CDA
    url = params.get('url')
    title = params.get('name')
    stream_url = get_mega_stream(url)
    port = cache.cache_get('proxyport')['value']
    proxy_url = f"http://localhost:{port}/?url={stream_url.url}&type=mega&mega_data={stream_url.data}"

    li = xbmcgui.ListItem(title, path=proxy_url)
    xbmcplugin.setResolvedUrl(addon_handle, True, li)



def addItem(name, url, action, isFolder=True):
    urlparams = {'url': url, 'name': name, 'action': action}
    u = f'{sys.argv[0]}?{urlencode(urlparams)}'
    liz = xbmcgui.ListItem(name)
    if not isFolder:
        liz.setProperty('IsPlayable', 'true')

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,
                                isFolder=isFolder, totalItems=1)


#main_menu()
#play()

action = params.get('action')
if action == None:
    main_menu()
elif action == 'play':
    play()

xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
