# -*- coding: utf-8 -*-

### Imports ###
import  os
import sys
import xbmc
import xbmcaddon
import xbmcvfs
from addon.common.addon import Addon  # może trzeba więcej
from common import (eod, set_view, addst, cFL, myNote)
import contextmenu
#######
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database
##########
iconFav = xbmcaddon.Addon(id="plugin.video.anime-iptv").getAddonInfo('path') + '/art/favorites.png'
iconSite = xbmcaddon.Addon(id="plugin.video.anime-iptv").getAddonInfo('path') + '/art/icon.png'
fanartSite = xbmcaddon.Addon(id="plugin.video.anime-iptv").getAddonInfo('path') + '/art/japan/fanart.jpg'
_addon = Addon('plugin.video.anime-iptv', sys.argv)
_artIcon = _addon.get_icon()
_artFanart = _addon.get_fanart()
addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
xbmcvfs.mkdir(dataPath)
favouritesFile = os.path.join(dataPath, 'favourites.db')
lang = xbmcaddon.Addon().getLocalizedString
###########


def bFL(t):
    return '[B]' + t + '[/B]'  # For Bold Text ###


def fav__COMMON__list_fetcher(site, section='', subfav=''):
    saved_favs = ('favs_' + site + '__' + section + subfav + '__')
    try:
        db = database.connect(favouritesFile)
        cur = db.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS pluginvideoanimeiptv(name TEXT unique, data TEXT)''')
        db.commit()
        cur.execute("SELECT * FROM pluginvideoanimeiptv WHERE name=?", (saved_favs,))
        items = cur.fetchall()
        for row in items:
            favs = sorted(eval(row[1]), key=lambda fav: (fav[1], fav[0]), reverse=True)
            ItemCount=len(favs)
            if favs:
                return favs
            else:
                return ''
        else:
            return ''
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def fav__COMMON__check(site, section, name, year, subfav=''):
    saved_favs = ('favs_' + site + '__' + section + subfav + '__')
    try:
        db = database.connect(favouritesFile)
        cur = db.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS pluginvideoanimeiptv(name TEXT unique, data TEXT)''')
        db.commit()
        cur.execute("SELECT * FROM pluginvideoanimeiptv WHERE name=?", (saved_favs,))
        items = cur.fetchall()
        for row in items:
            favs = eval(row[1])
            if favs:
                for (_name, _year, _img, _fanart, _country, _url, _plot, _Genres, _site, _subfav, _section, _ToDoParams, _commonID, _commonID2) in favs:
                    if (name == _name):
                        return True
                return False
            else:
                return False
        else:
            return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def fav__COMMON__remove(site, section, name, year, subfav=''):
    saved_favs = ('favs_' + site + '__' + section + subfav + '__')
    tf = False
    try:
        db = database.connect(favouritesFile)
        cur = db.cursor()
        cur.execute("SELECT * FROM pluginvideoanimeiptv WHERE name=?", (saved_favs,))
        items = cur.fetchall()
        for row in items:
            favs = eval(row[1])
            if favs:
                for (_name, _year, _img, _fanart, _country, _url, _plot, _Genres, _site, _subfav, _section, _ToDoParams, _commonID, _commonID2) in favs:
                    if (name == _name):
                        favs.remove((_name, _year, _img, _fanart, _country, _url, _plot, _Genres, _site, _subfav, _section, _ToDoParams, _commonID, _commonID2))
                        favs = unicode(favs)
                        cur.execute('UPDATE pluginvideoanimeiptv SET data = ? WHERE name = ? ', (favs, saved_favs))
                        db.commit()
                        tf = True
                        myNote(bFL(name.upper()), bFL((lang(30003).encode('utf-8'))))
                        xbmc.executebuiltin("XBMC.Container.Refresh")
                if (tf == False):
                    myNote(bFL(name.upper()), bFL((lang(30004).encode('utf-8'))))
            else:
                myNote(bFL(name.upper() + '  (' + year + ')'), bFL((lang(30004).encode('utf-8'))))
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def fav__COMMON__add(site, section, name, year='', img=_artIcon, fanart=_artFanart, subfav='', plot='', commonID='', commonID2='', ToDoParams='', Country='', Genres='', Url=''):
    saved_favs =  ('favs_' + site + '__' + section + subfav + '__')
    favs = []
    favs.append((name, year, img, fanart, Country, Url, plot, Genres, site, subfav, section, ToDoParams, commonID, commonID2))
    favs = unicode(favs)
    try:
        db = database.connect(favouritesFile)
        cur = db.cursor()
        cur.execute("SELECT count(*) FROM pluginvideoanimeiptv WHERE name = ?", (saved_favs,))
        data = cur.fetchone()[0]
        if data == 0:
            print('There is no component named %s'%saved_favs)
            cur.execute('''INSERT INTO pluginvideoanimeiptv(name, data) VALUES(?,?)''', (saved_favs,favs))
            db.commit()
        else:
            print('Component %s found in rows' % (saved_favs))
            cur.execute("SELECT * FROM pluginvideoanimeiptv WHERE name=?", (saved_favs,))
            items = cur.fetchall()
            for row in items:
                favs = eval(row[1])
                if favs:
                    for (_name, _year, _img, _fanart, _country, _url, _plot, _Genres, _site, _subfav, _section, _ToDoParams, _commonID, _commonID2) in favs:
                        if (name == _name) and (year == _year):
                            if len(year) > 0:
                                myNote(bFL(section + ':  ' + name.upper() + '  (' + year + ')'), bFL((lang(30005).encode('utf-8'))))
                            else:
                                myNote(bFL(section + ':  ' + name.upper()), bFL((lang(30005).encode('utf-8'))))
                            return
                favs.append((name, year, img, fanart, Country, Url, plot, Genres, site, subfav, section, ToDoParams, commonID, commonID2))
                favs = unicode(favs)
                cur.execute('UPDATE pluginvideoanimeiptv SET data = ? WHERE name = ? ', (favs, saved_favs))
                db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    if len(year) > 0:
        myNote(bFL(name + '  (' + year + ')'), bFL((lang(30002).encode('utf-8'))))
    else:
        myNote(bFL(name), bFL((lang(30002).encode('utf-8'))))


#def fav__COMMON__empty(site, section, subfav=''):
#    favs = []
#    cache.set('favs_' + site + '__' + section + subfav + '__', str(favs))
#    myNote(bFL('Favorites'), bFL('Your Favorites Have Been Wiped Clean.'))


def Fav_List(site='', section='', subfav=''):
    favs = fav__COMMON__list_fetcher(site=site, section='animezone', subfav=subfav)
    favs2 = fav__COMMON__list_fetcher(site=site, section='senpai', subfav=subfav)
    favs5 = fav__COMMON__list_fetcher(site=site, section='animeon', subfav=subfav)
    favs4 = fav__COMMON__list_fetcher(site=site, section='animeonline', subfav=subfav)
    favs3 = fav__COMMON__list_fetcher(site=site, section='animecentrum', subfav=subfav)
    favs6 = fav__COMMON__list_fetcher(site=site, section='wbijam', subfav=subfav)
    favs7 = fav__COMMON__list_fetcher(site=site, section='kreskoweczki', subfav=subfav)
    ItemCount = len(favs) and len(favs2) and len(favs3) and len(favs4) and len(favs5) and len(favs6) and len(favs7)
    if len(favs) == 0 and len(favs2) == 0 and len(favs3) == 0 and len(favs4) == 0 and len(favs5) == 0 and len(favs6) == 0 and len(favs7) == 0:
        myNote((lang(30001).encode('utf-8')), (lang(30007).encode('utf-8')))
        eod()
        return
    if len(favs) == 0:
            favs = []
    if len(favs2) == 0:
            favs2 = []
    if len(favs3) == 0:
            favs3 = []
    if len(favs4) == 0:
            favs4 = []
    if len(favs5) == 0:
            favs5 = []
    if len(favs6) == 0:
            favs6 = []
    if len(favs7) == 0:
            favs7 = []
    favs += favs2
    favs += favs3
    favs += favs4
    favs += favs5
    favs += favs6
    favs += favs7
    for (_name, _year, _img, _fanart, _Country, _Url, _plot, _Genres, _site, _subfav, _section, _ToDoParams, _commonID, _commonID2) in favs:
        if _img > 0:
            img = _img
        else:
            img = iconSite
        if _fanart > 0:
            fimg = _fanart
        else:
            fimg = fanartSite
        pars = _addon.parse_query(_ToDoParams)
        _section
        _title = _name
        if _section == 'animezone':
            host = cFL(' (A-Z)', 'blueviolet')
            _title = _title + host
        if _section == 'senpai':
            host = cFL(' (Senpai)', 'blue')
            _title = _title + host
        if _section == 'animeon':
            host = cFL(' (A-ON)', 'lime')
            _title = _title + host
        if _section == 'animeonline':
            host = cFL(' (A-O)', 'orange')
            _title = _title + host
        if _section == 'animecentrum':
            host = cFL(' (A-C)', 'red')
            _title = _title + host
        if _section == 'wbijam':
            host = cFL(' (WB)', 'yellow')
            _title = _title + host
        if _section == 'kreskoweczki':
            host = cFL(' (KR)', 'lime')
            _title = _title + host
        if (len(_year) > 0) and (not _year == '0000'):
            _title += cFL('  (' + cFL(_year, 'deeppink') + ')', 'pink')
        if len(_Country) > 0:
            _title += cFL('  [' + cFL(_Country, 'deeppink') + ']', 'pink')
        contextLabs = {'title': _name, 'year': _year, 'img': _img, 'fanart': _fanart, 'country': _Country, 'url': _Url, 'plot': _plot, 'genres': _Genres, 'site': _site, 'subfav': _subfav, 'section': _section, 'todoparams': _ToDoParams, 'commonid': _commonID, 'commonid2': _commonID2}
        contextMenuItems = contextmenu.ContextMenu_Favorites(contextLabs)
        _addon.add_directory(pars, {'title': _title, 'plot': _plot}, is_folder=True, fanart=fimg, img=img, total_items=ItemCount, contextmenu_items=contextMenuItems)
    if 'movie' in section.lower():
        content = 'tvshows'
    else:
        content = 'tvshows'
#    set_view(content, view_mode=int(addst('tvshows-view')))
    eod()