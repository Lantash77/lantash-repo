import os

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from common import myNote

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
xbmcvfs.mkdir(dataPath)
scraperFile = os.path.join(dataPath, 'scraper.db')


def scraper_check(host, name):
    try:
        db = database.connect(scraperFile)
        db.text_factory = str
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " + host + "(name TEXT unique, image TEXT, plot  TEXT, fanart TEXT)")
        db.commit()
        cur.execute("SELECT * FROM " + host + " WHERE name=?", (name,))
        items = cur.fetchall()
        for row in items:
            favs = row[0]
            image = row[1]
            plot = row[2]
            ItemCount=len(favs)
            if favs:
                return favs, image, plot
            else:
                names = False
                return names
        else:
            return ''
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def scraper_add(host, name, img, plot, fanart):
    try:
        db = database.connect(scraperFile)
        cur = db.cursor()
        cur.execute("SELECT count(*) FROM " + host + " WHERE name = ?", (name,))
        data = cur.fetchone()[0]
        if data == 0:
            print('There is no component named %s'%name)
            cur.execute("INSERT INTO " + host + "(name, image, plot, fanart) VALUES(?,?,?,?)", (name, img, plot, fanart))
            db.commit()
        else:
            print('Component %s found in rows' % (name))
            #cur.execute("SELECT * FROM pluginvideoanimeiptv WHERE name=?", (saved_favs,))
            #items = cur.fetchall()
            #for row in items:
                #favs = eval(row[1])
                #if favs:
                    #for (_name, _year, _img, _fanart, _country, _url, _plot, _Genres, _site, _subfav, _section, _ToDoParams, _commonID, _commonID2) in favs:
                        #if (name == _name) and (year == _year):
                            #if len(year) > 0:
                                #myNote(bFL(section + ':  ' + name.upper() + '  (' + year + ')'), bFL((lang(30005).encode('utf-8'))))
                            #else:
                                #myNote(bFL(section + ':  ' + name.upper()), bFL((lang(30005).encode('utf-8'))))
                            #return
                #favs.append((name, year, img, fanart, Country, Url, plot, Genres, site, subfav, section, ToDoParams, commonID, commonID2))
                #favs = unicode(favs)
                #cur.execute('UPDATE pluginvideoanimeiptv SET data = ? WHERE name = ? ', (favs, saved_favs))
                #db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def getItemTitles(table):
    out = []
    for i in range(len(table)):
        value = table[i]
        out.append(value[0])
    return out


def delete_table():
    lista = [['Anime-Odcinki', 'AnimeOnline'], ['Anime-joy', 'AnimeJoy'], ['AnimeZone', 'AnimeZone'], ['Kreskoweczki', 'Kreskoweczki'], ['animecentrum', 'animecentrum'], ['Senpai', 'Senpai']]
    d = xbmcgui.Dialog()
    item = d.select("Choose host:", getItemTitles(lista))
    if item != -1:
        host = str(lista[item][1])
        try:
            db = database.connect(scraperFile)
            cur = db.cursor()
            cur.execute("drop table if exists " + host)
            myNote(host, 'Thumbnails reseted')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()