# -*- coding: UTF-8 -*-

import os
import time
import threading
import re
import string

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
#import html
from resources.libs.CommonFunctions import parseDOM

import requests




try:
    import json
except:
    import simplejson as json

try:
    import sqlite3
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database




addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile'))
xbmcvfs.mkdir(dataPath)
scraperFile = os.path.join(dataPath, 'scraper.db')





def scraper_check(name, type):
# akceptowane   type  =  TV, Movie, OVA, Special

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
        cur.execute("CREATE TABLE IF NOT EXISTS AnimeOtaku (name TEXT unique, poster TEXT, plot  TEXT, fanart  TEXT, genre  TEXT, year  TEXT)")
        db.commit()
        cur.execute("SELECT * FROM AnimeOtaku WHERE name=?", (name,))
        items = cur.fetchall()
        for row in items:
            name = row[0]
            image = row[1]
            plot = row[2]
            fanart = row[3]
            genre = row[4]
            year = row[5]

            if name:
                return name, image, plot, fanart, genre, year, None
            else:
                return '', '', '', '', '', '', None
        else:
            t = threading.Thread(target=scraper_add, args=(name, type))
            return '', '', '', '', '', '', t
    except:
        return '', '', '', '', '', '', None
    finally:
        db.close()

def scraper_add(name, type):

    url = 'https://shinden.pl/series?search='
    url = url + '%s' % name.replace(" ", "+") + '&series_type[0]={}'
    url = url.format(type)
    mainLink = 'https://shinden.pl/'
    db = database.connect(scraperFile)
    cur = db.cursor()


    try:

        html = requests.get(url, timeout=15).text
        result = str(parseDOM(html, 'section', attrs={'class': 'anime-list box'})[0])
        results = [item for item in parseDOM(result, 'ul', attrs={'class': 'div-row'}) if 'h3' in item][0]
        link = mainLink + re.sub('/series/', 'series/', parseDOM(results, 'a', ret='href')[1])
        obraz = mainLink + re.sub('/res/', 'res/', parseDOM(results, 'a', ret='href')[0])
        empty = ['placeholders', 'javascript:void']

        
        if any(i in obraz for i in empty):
             poster, fanart = Scrap(name, type, poster=True)
        else:
            fanart = Scrap(name, type, poster=False)
            poster = obraz
                
        try:
            datasite = requests.get(link, timeout=10).text
            plotdata = parseDOM(datasite, 'div', attrs={'id': 'description'})[0]
            plot = CleanHTML(parseDOM(plotdata, 'p')[0])
        except:
            plot = ''
        try:
            genredata = [item for item in parseDOM(datasite, 'tr') if 'Gatunki' in item][0]
            genre = ', '.join(parseDOM(genredata, 'a'))
        except:
            genre = ''
        try:
            yeardata = parseDOM(datasite, 'section', attrs={'class': 'title-small-info'})[0]
            year = re.findall(r'[1-2][0-9]{3}', yeardata)[0]
        except:
            year = ''

        while True:
            time.sleep(1)

            try:
                cur.execute("SELECT count(*) FROM AnimeOtaku WHERE name = ?", (name,))
                data = cur.fetchone()[0]
                if not data:
                    print('There is no component named %s' % name)
                    cur.execute("INSERT INTO AnimeOtaku (name, poster, plot, fanart, genre, year) VALUES(?,?,?,?,?,?)",
                                (name, poster, plot, fanart, genre, year))
                    db.commit()
                    break
                else:
                    print('Component %s found in rows' % (name))
                    break
            except sqlite3.OperationalError as e:
                print(e)
                continue
    except Exception as e:

        raise e
    finally:
        db.close()



def ScrapJikan(title='',type=''):
    
#####   Jikan Scrapper   #####


    Jikan = 'https://api.jikan.moe/v3/search/anime?q='
    if type == 'serie':
        type = 'TV'

    elif type == 'film':
        type = 'Movie'
    elif type == 'OVA':
        type = 'OVA'
    url = Jikan + title
    try:
       result = requests.get(url).text
       result = json.loads(result)['results']
       for r in result:
           if r['type'] == type:
               img = r['image_url']
               GenTitle = r['title']
               break

       return img, GenTitle
    except:
        return ''


def String2HTML(html):

    if ("%" in html):
        html = html.replace('%', '%25')
    if ("'" in html):
        html = html.replace("'", '%27')
    if (',' in html):
        html = html.replace(',', '%2C')
    if (' ' in html):
        html = html.replace(' ', '%20')
    if (':' in html):
        html = html.replace(':', '%3A')

    return html

def Scrap(title, type, poster):
### TMDB API SCRAPER ###

    titleENC = String2HTML(title)
    TMDBURL = 'https://api.themoviedb.org/3/{}'
    TMDBAPI = '?api_key=af3a53eb387d57fc935e9128468b1899&query='
    TMDBAPICONF = TMDBURL.format('configuration') + TMDBAPI
    conf = json.loads(requests.get(TMDBAPICONF).text)['images']
    backdrop_base_url = conf['secure_base_url'] + conf['backdrop_sizes'][-1]


    if type == 'TV':
        queryURLPL = TMDBURL.format('search/tv') + TMDBAPI + titleENC + '&language=pl-PL'
        queryURL = TMDBURL.format('search/tv') + TMDBAPI + titleENC
    elif type == 'Movie':
        queryURLPL = TMDBURL.format('search/movie') + TMDBAPI + titleENC + '&language=pl-PL'
        queryURL = TMDBURL.format('search/movie') + TMDBAPI + titleENC
    r = requests.get(queryURLPL).text

    if json.loads(r)['total_results'] == 0:
        r = requests.get(queryURL).text
        if json.loads(r)['total_results'] == 0:
            backdrop_link = ''
            poster_link = ScrapJikan(title, type)
        else:
            t = json.loads(r)['results'][0]

    else:
        t = json.loads(r)['results'][0]

    try:
        backdrop_link = backdrop_base_url + t['backdrop_path']
    except:
        backdrop_link = ''
    try:
        poster_link = backdrop_base_url + t['poster_path']
    except:
        poster_link = ScrapJikan(title, type)
    if poster == True:
        return(poster_link, backdrop_link)
    else:
        return(backdrop_link)

def delete_table():

    try:
        db = database.connect(scraperFile)
        cur = db.cursor()
        cur.execute("drop table if exists AnimeOtaku")
        d = xbmcgui.Dialog()
        d.ok('Scraper', 'Usunięto pomyślnie')
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
def CleanHTML(html):
    if ("&amp;" in html):
        html = html.replace('&amp;', '&')
    if ("&nbsp;" in html):
        html = html.replace('&nbsp;', '')
    if ('[&hellip;]' in html):
        html = html.replace('[&hellip;]', '[…]')
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
        if ('[&hellip;]' in html):
            html = html.replace('[&hellip;]', '[…]')
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')
        if (u'\u2661' in html):
            html = html.replace(u'\u2661', ' ')
        if (u'\u222c' in html):
            html = html.replace(u'\u222c', ' ')

    return html