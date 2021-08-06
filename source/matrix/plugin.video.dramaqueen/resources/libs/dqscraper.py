# -*- coding: UTF-8 -*-
import os
import time
import threading
import re

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import string
from resources.libs.CommonFunctions import parseDOM
#from CommonFunctions import parseDOM
import requests

from resources.libs import cache

#from resources.libs import cleantitle

try:
    import sqlite3
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmcvfs.translatePath(addonInfo('profile'))
xbmcvfs.mkdir(dataPath)
scraperFile = os.path.join(dataPath, 'scraper.db')

def scraper_check(name, url, poster):

    name = re.sub('[' + string.punctuation + ']', '', name)
#    name = re.sub('[' + string.punctuation + ']', '', name)
    db = database.connect(scraperFile, detect_types=sqlite3.PARSE_DECLTYPES,
                          cached_statements=20000)

    try:

        db.text_factory = str
        cur = db.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute('PRAGMA synchronous = OFF')
        cur.execute('PRAGMA journal_mode = OFF')
        cur.execute("PRAGMA page_size = 16384")
        cur.execute("PRAGMA cache_size = 64000")
        cur.execute("PRAGMA temp_store = MEMORY")
        cur.execute("PRAGMA locking_mode = NORMAL")
        cur.execute("PRAGMA count_changes = OFF")
        cur.execute("PRAGMA optimize")
        cur.execute("CREATE TABLE IF NOT EXISTS DramaQueen (name TEXT unique, poster TEXT, plot  TEXT, banner  TEXT, fanart  TEXT, genre  TEXT, year  TEXT)")
        db.commit()
        cur.execute("SELECT * FROM DramaQueen WHERE name=?", (name,))
        items = cur.fetchall()
        for row in items:
            name = row[0]
            image = row[1]
            plot = row[2]
            banner = row[3]
            fanart = row[4]
            genre = row[5]
            year = row[6]

            if name:
                return name, image, plot, banner, fanart, genre, year, None
            else:
                return '', '', '', '', '', '', '', None
        else:
            t = threading.Thread(target=scraper_add, args=(url, name, poster))
            return '', '', '', '', '', '', '', t
    except:
        return '', '', '', '', '', '', '', None
    finally:
        db.close()

def CleanHTML(html):
    html = str(html)
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
            html = html.replace('&#8230;', '…')
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')
    return html

def scraper_add(url, name, poster):

    db = database.connect(scraperFile)
    cur = db.cursor()
           
    try:        

        data = requests.get(url, timeout=10).text
        fanart = re.findall('background-image: url\((.+?)\);', data)[1]
        banner = parseDOM(data, 'img', attrs={'itemprop': 'thumbnailUrl'}, ret='src')[0]

        plot1 = [item for item in parseDOM(data, 'section', attrs={'class': 'av_textblock_section '}) if '<em>' in item]
        plot2 = [item for item in parseDOM(data, 'section', attrs={'class': 'av_textblock_section '}) if
                 not '<em>' in item]
        if not '<a>' in plot1:
            plot = CleanHTML(parseDOM(plot1, 'em')[0])
        if '<strong>' in plot:
            try:
                plot = CleanHTML(parseDOM(plot2, 'p')[0])
            except:
                pass

        details = GetDataBeetwenMarkers(data, 'Gatunki:', 'Upload:', True)[1]
        gen = [item[1] for item in re.findall('<a href(.+?)">(.+?)</a>',details) if '/gatunek/' in item[0]]
        genre = ', ' .join(gen)
        year = re.findall(r'[1-2][0-9]{3}', details)[0]                
                
        while True:
            time.sleep(1)

            try:
                cur.execute("SELECT count(*) FROM DramaQueen WHERE name = ?", (name,))
                data = cur.fetchone()[0]
                if not data:
                    print('There is no component named %s' % name)
                    cur.execute("INSERT INTO DramaQueen (name, poster, plot, banner, fanart, genre, year) VALUES(?,?,?,?,?,?,?)",
                                (name, poster, plot, banner, fanart, genre, year))
                    db.commit()
                    break
                else:
                    print('Component %s found in rows' % (name))
                    break
            except sqlite3.OperationalError as e:
                print(e)
                continue
    except Exception as e:
        print(e)
        raise e
    finally:
        db.close()

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

def delete_table():

    try:
        db = database.connect(scraperFile)
        cur = db.cursor()
        cur.execute("drop table if exists DramaQueen")
        d = xbmcgui.Dialog()
        d.ok('Scraper', 'Usunięto pomyślnie')

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()