# -*- coding: utf-8 -*-

'''
    Covenant Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import datetime
import json
import os
import re
import sys
import urllib

import requests

try:
    import urllib.parse as urllib
except:
    pass
from resources.lib.indexers import navigator
from ptw.libraries import cache
from ptw.libraries import cleangenre
from ptw.libraries import cleantitle
from ptw.libraries import client
from ptw.libraries import control
from ptw.libraries import metacache
from ptw.libraries import playcount
from ptw.libraries import trakt
from ptw.libraries import utils
from ptw.libraries import views
from ptw.libraries.utils import convert

params = dict(urllib.parse_qsl(sys.argv[2].replace('?', ''))) if len(sys.argv) > 1 else dict()

action = params.get('action')

tvshowssort = control.setting('tvshows.sort')
listscount = control.setting('lists.count')

if tvshowssort == '0':
    tvshowssort = 'moviessort,asc'
elif tvshowssort == '1':
    tvshowssort = 'year,desc'


class tvshows:
    def __init__(self):
        self.list = []

        self.tvdb_jwt_token = None
        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api.trakt.tv'
        self.tvmaze_link = 'http://www.tvmaze.com'
        self.logo_link = 'https://i.imgur.com/'
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours=5))
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.fanart_tv_user = control.setting('fanart.tv.user')
        self.user = control.setting('fanart.tv.user') + str('')
        self.lang = control.apiLanguage()['tvdb']

        self.search_link = 'http://api.trakt.tv/search/show?limit=20&page=1&query='
        self.tvmaze_info_link = 'http://api.tvmaze.com/shows/%s'
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key, '%s', self.lang)
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'

        self.persons_link = 'https://www.imdb.com/search/name?count=100&name='
        self.personlist_link = 'https://www.imdb.com/search/name?count=100&gender=male,female'
        self.popular_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&release_date=,date[0]&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.airing_link = 'https://www.imdb.com/search/title?title_type=tv_episode&release_date=date[1],date[0]&sort=moviemeter,asc&count=' + listscount + '&start=1'
        self.active_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=10,&production_status=active&sort=moviemeter,asc&count=' + listscount + '&start=1'
        # self.premiere_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=10,&release_date=date[60],date[0]&sort=moviemeter,asc&count=' + listscount + '&start=1'
        self.premiere_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=10,&release_date=date[60],date[0]&sort=release_date,desc&count=' + listscount + '&start=1'
        self.rating_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=5000,&release_date=,date[0]&sort=user_rating,desc&count=' + listscount + '&start=1'
        self.views_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&release_date=,date[0]&sort=num_votes,desc&count=' + listscount + '&start=1'
        self.person_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&role=%s&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.genre_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=%s&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.keyword_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&keywords=%s&sort=moviemeter,asc&count=' + listscount + '&start=1'
        self.language_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&production_status=released&primary_language=%s&' + tvshowssort + '&count=' + listscount + '&start=1'
        self.certification_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&certificates=us:%s&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.trending_link = 'http://api.trakt.tv/shows/trending?limit=40&page=1'

        #       self.year_link = 'TEST'
        self.action_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=action&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.adventure_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=adventure&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.animation_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=animation&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.anime_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&keywords=anime&sort=moviemeter,asc&count=' + listscount + '&start=1'
        self.biography_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=biography&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.comedy_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=comedy&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.crime_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=crime&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.drama_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=drama&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.family_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=family&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.fantasy_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=fantasy&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.game_show_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=game_show&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.history_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=history&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.horror_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=horror&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.music_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=music&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.musical_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=musical&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.mystery_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=mystery&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.news_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=news&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.reality_tv_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=reality_tv&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.romance_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=romance&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.sci_fi_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=sci_fi&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.sport_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=sport&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.talk_show_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=talk_show&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.thriller_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=thriller&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.war_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=war&sort=' + tvshowssort + '&count=' + listscount + '&start=1'
        self.western_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=western&sort=' + tvshowssort + '&count=' + listscount + '&start=1'

        self.traktlists_link = 'http://api.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api.trakt.tv/users/me/collection/shows'
        self.traktwatchlist_link = 'http://api.trakt.tv/users/me/watchlist/shows'
        self.traktfeatured_link = 'http://api.trakt.tv/recommendations/shows?limit=40'
        self.imdblists_link = 'https://www.imdb.com/user/ur%s/lists?tab=all&sort=mdfd&order=desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'https://www.imdb.com/list/%s/?view=detail&sort=alpha,asc&title_type=tvSeries,miniSeries&start=1'
        self.imdblist2_link = 'https://www.imdb.com/list/%s/?view=detail&sort=date_added,desc&title_type=tvSeries,miniSeries&start=1'
        self.imdbwatchlist_link = 'https://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
        self.imdbwatchlist2_link = 'https://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user
        self.imdbUserLists_link = 'https://www.imdb.com/list/%s/?view=detail&sort=alpha,asc&title_type=tvSeries,miniSeries&count=' + listscount + '&start=1'

        self.y50_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=1950-01-01,1959-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y60_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=1960-01-01,1969-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y70_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=1970-01-01,1979-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y80_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=1980-01-01,1989-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y90_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=1990-01-01,1999-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y2000_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=2000-01-01,2009-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y2010_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=2010-01-01,2019-12-31&sort=moviessort,asc&count=' + listscount + '&start=1'
        self.y2020_link = 'https://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=2020-01-01,date[90]&sort=moviessort,asc&count=' + listscount + '&start=1'


    def tvdb_login(self, username_tvdb, user_key_tvdb, api_key_tvdb):
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            data = '{\n  "apikey": "%s",\n  "userkey": "%s",\n  "username": "%s"\n}' % (
                api_key_tvdb, user_key_tvdb, username_tvdb)
            token = json.loads(requests.post("https://api.thetvdb.com/login", headers=headers, data=data, timeout=10).text)
            if token['token']:
                self.tvdb_jwt_token = token['token']
            else:
                self.tvdb_jwt_token = None
        except:
            self.tvdb_jwt_token = None

    def get(self, url, idx=True, create_directory=True):
        try:
            api_key_tvdb = control.setting('TVDb_ApiKey')
            user_key_tvdb = control.setting('TVDb_UserKey')
            username_tvdb = control.setting('TVDb_Username')
            if api_key_tvdb and username_tvdb and user_key_tvdb:
                self.tvdb_login(username_tvdb, user_key_tvdb, api_key_tvdb)
            try:
                url = getattr(self, url + '_link')
            except:
                pass

            try:
                u = urllib.urlparse(url).netloc.lower()
            except:
                pass

            if u in self.trakt_link and '/users/' in url:
                try:
                    if not '/users/me/' in url: raise Exception()
                    if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user): raise Exception()
                    self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
                except:
                    self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)

                if '/users/me/' in url and '/collection/' in url:
                    self.list = sorted(self.list, key=lambda k: utils.title_key(k['title']))

                if idx == True: self.worker()

            elif u in self.trakt_link and self.search_link in url:
                self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
                if idx == True: self.worker(level=0)

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True: self.worker()


            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_list, 0, url)
                if idx == True: self.worker()

            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 24, url)
                if idx == True: self.worker()


            elif u in self.tvmaze_link:
                self.list = cache.get(self.tvmaze_list, 168, url)
                if idx == True: self.worker()

            if idx == True and create_directory == True: self.tvshowDirectory(self.list)
            return self.list
        except:
            pass

    def search(self):

        navigator.navigator().addDirectoryItem(32603, 'tvSearchnew', 'search.png', 'DefaultTVShows.png')

        from sqlite3 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()

        try:
            dbcur.executescript("CREATE TABLE IF NOT EXISTS tvshow (ID Integer PRIMARY KEY AUTOINCREMENT, term);")
        except:
            pass

        dbcur.execute("SELECT * FROM tvshow ORDER BY ID DESC")

        lst = []

        delete_option = False
        for (id, term) in dbcur.fetchall():
            if term not in str(lst):
                delete_option = True
                navigator.navigator().addDirectoryItem(term, 'tvSearchterm&name=%s' % term, 'search.png',
                                                       'DefaultTVShows.png')
                lst += [(term)]
        dbcur.close()

        if delete_option:
            navigator.navigator().addDirectoryItem(32605, 'clearCacheSearch', 'tools.png', 'DefaultAddonProgram.png')

        navigator.navigator().endDirectory()

    def search_new(self):
        control.idle()

        t = control.lang(32010).encode('utf-8')
        k = control.keyboard('', t)
        k.doModal()
        q = k.getText() if k.isConfirmed() else None

        if (q == None or q == ''): return

        q = cleantitle.normalize(q)  # for polish characters

        from sqlite3 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO tvshow VALUES (?,?)", (None, q))
        dbcon.commit()
        dbcur.close()
        url = self.search_link + urllib.quote_plus(q)
        url = '%s?action=tvshowPage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
        tvshows.get(self, self.search_link + q)

    def search_term(self, name):
        control.idle()

        url = self.search_link + urllib.quote_plus(name)
        url = '%s?action=tvshowPage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
        tvshows.get(self, self.search_link + urllib.quote_plus(name))

    def person(self):
        try:
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t)
            k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            q = cleantitle.normalize(q)  # for polish characters

            url = self.persons_link + urllib.quote_plus(q)
            url = '%s?action=tvPersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            tvshows.persons(self, self.persons_link + q)
        except Exception as e:
            print(e)
            return

    def genres(self):
        genres = [
            ('Action', 'action', True),
            ('Adventure', 'adventure', True),
            ('Animation', 'animation', True),
            ('Anime', 'anime', False),
            ('Biography', 'biography', True),
            ('Comedy', 'comedy', True),
            ('Crime', 'crime', True),
            ('Drama', 'drama', True),
            ('Family', 'family', True),
            ('Fantasy', 'fantasy', True),
            ('Game-Show', 'game_show', True),
            ('History', 'history', True),
            ('Horror', 'horror', True),
            ('Music ', 'music', True),
            ('Musical', 'musical', True),
            ('Mystery', 'mystery', True),
            ('News', 'news', True),
            ('Reality-TV', 'reality_tv', True),
            ('Romance', 'romance', True),
            ('Science Fiction', 'sci_fi', True),
            ('Sport', 'sport', True),
            ('Talk-Show', 'talk_show', True),
            ('Thriller', 'thriller', True),
            ('War', 'war', True),
            ('Western', 'western', True)
        ]

        for i in genres: self.list.append(
            {
                'name': cleangenre.lang(i[0], self.lang),
                'url': self.genre_link % i[1] if i[2] else self.keyword_link % i[1],
                'image': 'tvGenres.jpg',
                'action': 'tvshows'
            })

        self.addDirectory(self.list)
        return self.list

    def years_top(self):
        self.list.append({'name': '[I]Lata 50[/I] - [B]1950 - 1959[/B]', 'url': 'y50', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 60[/I] - [B]1960 - 1969[/B]', 'url': 'y60', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 70[/I] - [B]1970 - 1979[/B]', 'url': 'y70', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 80[/I] - [B]1980 - 1989[/B]', 'url': 'y80', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 90[/I] - [B]1990 - 1999[/B]', 'url': 'y90', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 2000[/I] - [B]2000 - 2009[/B]', 'url': 'y2000', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 2010[/I] - [B]2010 - 2019[/B]', 'url': 'y2010', 'image': 'years.png', 'action': 'tvshows'})
        self.list.append({'name': '[I]Lata 2020[/I] - [B]2020 - dziś[/B]', 'url': 'y2010', 'image': 'years.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def my_imdbUserLists(self):
        tvlist1 = control.setting('imdb.tvlist_name1')
        tvlist1_link = control.setting('imdb.tvlist_id1')
        if tvlist1:
            self.list.append({'name': tvlist1, 'url': self.imdbUserLists_link % tvlist1_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist2 = control.setting('imdb.tvlist_name2')
        tvlist2_link = control.setting('imdb.tvlist_id2')
        if tvlist2:
            self.list.append({'name': tvlist2, 'url': self.imdbUserLists_link % tvlist2_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist3 = control.setting('imdb.tvlist_name3')
        tvlist3_link = control.setting('imdb.tvlist_id3')
        if tvlist3:
            self.list.append({'name': tvlist3, 'url': self.imdbUserLists_link % tvlist3_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist4 = control.setting('imdb.tvlist_name4')
        tvlist4_link = control.setting('imdb.tvlist_id4')
        if tvlist4:
            self.list.append({'name': tvlist4, 'url': self.imdbUserLists_link % tvlist4_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist5 = control.setting('imdb.tvlist_name5')
        tvlist5_link = control.setting('imdb.tvlist_id5')
        if tvlist5:
            self.list.append({'name': tvlist5, 'url': self.imdbUserLists_link % tvlist5_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist6 = control.setting('imdb.tvlist_name6')
        tvlist6_link = control.setting('imdb.tvlist_id6')
        if tvlist6:
            self.list.append({'name': tvlist6, 'url': self.imdbUserLists_link % tvlist6_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist7 = control.setting('imdb.tvlist_name7')
        tvlist7_link = control.setting('imdb.tvlist_id7')
        if tvlist7:
            self.list.append({'name': tvlist7, 'url': self.imdbUserLists_link % tvlist7_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist8 = control.setting('imdb.tvlist_name8')
        tvlist8_link = control.setting('imdb.tvlist_id8')
        if tvlist8:
            self.list.append({'name': tvlist8, 'url': self.imdbUserLists_link % tvlist8_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist9 = control.setting('imdb.tvlist_name9')
        tvlist9_link = control.setting('imdb.tvlist_id9')
        if tvlist9:
            self.list.append({'name': tvlist9, 'url': self.imdbUserLists_link % tvlist9_link, 'image': 'imdb.png', 'action': 'tvshows'})
        tvlist10 = control.setting('imdb.tvlist_name10')
        tvlist10_link = control.setting('imdb.tvlist_id10')
        if tvlist10:
            self.list.append({'name': tvlist10, 'url': self.imdbUserLists_link % tvlist10_link, 'image': 'imdb.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def networks(self):
        networks = [
            ('A&E', '/networks/29/ae', 'https://i.imgur.com/xLDfHjH.png'),
            ('ABC', '/networks/3/abc', 'https://i.imgur.com/qePLxos.png'),
            ('AMC', '/networks/20/amc', 'https://i.imgur.com/ndorJxi.png'),
            ('AT-X', '/networks/167/at-x', 'https://i.imgur.com/JshJYGN.png'),
            ('Adult Swim', '/networks/10/adult-swim', 'https://i.imgur.com/jCqbRcS.png'),
            ('Amazon', '/webchannels/3/amazon', 'https://i.imgur.com/ru9DDlL.png'),
            ('Animal Planet', '/networks/92/animal-planet', 'https://i.imgur.com/olKc4RP.png'),
            ('Audience', '/networks/31/audience-network', 'https://i.imgur.com/5Q3mo5A.png'),
            ('BBC America', '/networks/15/bbc-america', 'https://i.imgur.com/TUHDjfl.png'),
            ('BBC Four', '/networks/51/bbc-four', 'https://i.imgur.com/PNDalgw.png'),
            ('BBC One', '/networks/12/bbc-one', 'https://i.imgur.com/u8x26te.png'),
            ('BBC Three', '/webchannels/71/bbc-three', 'https://i.imgur.com/SDLeLcn.png'),
            ('BBC Two', '/networks/37/bbc-two', 'https://i.imgur.com/SKeGH1a.png'),
            ('BET', '/networks/56/bet', 'https://i.imgur.com/ZpGJ5UQ.png'),
            ('Bravo', '/networks/52/bravo', 'https://i.imgur.com/TmEO3Tn.png'),
            ('CBC', '/networks/36/cbc', 'https://i.imgur.com/unQ7WCZ.png'),
            ('CBS', '/networks/2/cbs', 'https://i.imgur.com/8OT8igR.png'),
            ('CTV', '/networks/48/ctv', 'https://i.imgur.com/qUlyVHz.png'),
            ('CW', '/networks/5/the-cw', 'https://i.imgur.com/Q8tooeM.png'),
            ('CW Seed', '/webchannels/13/cw-seed', 'https://i.imgur.com/nOdKoEy.png'),
            ('Cartoon Network', '/networks/11/cartoon-network', 'https://i.imgur.com/zmOLbbI.png'),
            ('Channel 4', '/networks/45/channel-4', 'https://i.imgur.com/6ZA9UHR.png'),
            ('Channel 5', '/networks/135/channel-5', 'https://i.imgur.com/5ubnvOh.png'),
            ('Cinemax', '/networks/19/cinemax', 'https://i.imgur.com/zWypFNI.png'),
            ('Comedy Central', '/networks/23/comedy-central', 'https://i.imgur.com/ko6XN77.png'),
            ('Crackle', '/webchannels/4/crackle', 'https://i.imgur.com/53kqZSY.png'),
            ('Discovery Channel', '/networks/66/discovery-channel', 'https://i.imgur.com/8UrXnAB.png'),
            ('Discovery ID', '/networks/89/investigation-discovery', 'https://i.imgur.com/07w7BER.png'),
            ('Disney Channel', '/networks/78/disney-channel', 'https://i.imgur.com/ZCgEkp6.png'),
            ('Disney XD', '/networks/25/disney-xd', 'https://i.imgur.com/PAJJoqQ.png'),
            ('E! Entertainment', '/networks/43/e', 'https://i.imgur.com/3Delf9f.png'),
            ('E4', '/networks/41/e4', 'https://i.imgur.com/frpunK8.png'),
            ('FOX', '/networks/4/fox', 'https://i.imgur.com/6vc0Iov.png'),
            ('FX', '/networks/13/fx', 'https://i.imgur.com/aQc1AIZ.png'),
            ('Freeform', '/networks/26/freeform', 'https://i.imgur.com/f9AqoHE.png'),
            ('HBO', '/networks/8/hbo', 'https://i.imgur.com/Hyu8ZGq.png'),
            ('HGTV', '/networks/192/hgtv', 'https://i.imgur.com/INnmgLT.png'),
            ('Hallmark', '/networks/50/hallmark-channel', 'https://i.imgur.com/zXS64I8.png'),
            ('History Channel', '/networks/53/history', 'https://i.imgur.com/LEMgy6n.png'),
            ('ITV', '/networks/35/itv', 'https://i.imgur.com/5Hxp5eA.png'),
            ('Lifetime', '/networks/18/lifetime', 'https://i.imgur.com/tvYbhen.png'),
            ('MTV', '/networks/22/mtv', 'https://i.imgur.com/QM6DpNW.png'),
            ('NBC', '/networks/1/nbc', 'https://i.imgur.com/yPRirQZ.png'),
            ('National Geographic', '/networks/42/national-geographic-channel', 'https://i.imgur.com/XCGNKVQ.png'),
            ('Netflix', '/webchannels/1/netflix', 'https://i.imgur.com/jI5c3bw.png'),
            ('Nickelodeon', '/networks/27/nickelodeon', 'https://i.imgur.com/OUVoqYc.png'),
            ('PBS', '/networks/85/pbs', 'https://i.imgur.com/r9qeDJY.png'),
            ('Polsat', '/networks/335/polsat', 'https://i.imgur.com/knnmJG5.png'),
            ('Showtime', '/networks/9/showtime', 'https://i.imgur.com/SawAYkO.png'),
            ('Sky1', '/networks/63/sky-1', 'https://i.imgur.com/xbgzhPU.png'),
            ('Starz', '/networks/17/starz', 'https://i.imgur.com/Z0ep2Ru.png'),
            ('Sundance', '/networks/33/sundance-tv', 'https://i.imgur.com/qldG5p2.png'),
            ('Syfy', '/networks/16/syfy', 'https://i.imgur.com/9yCq37i.png'),
            ('TBS', '/networks/32/tbs', 'https://i.imgur.com/RVCtt4Z.png'),
            ('TLC', '/networks/80/tlc', 'https://i.imgur.com/c24MxaB.png'),
            ('TNT', '/networks/14/tnt', 'https://i.imgur.com/WnzpAGj.png'),
            ('TVN', '/networks/334/tvn', 'https://i.imgur.com/yA8TJ4o.png'),
            ('TVP1', '/networks/57/tvland', 'https://i.imgur.com/as4ipbu.png'),
            ('TVP2', '/networks/333/tvp2', 'https://i.imgur.com/qj1Ta1Q.png'),
            ('TV Land', '/networks/57/tvland', 'https://i.imgur.com/1nIeDA5.png'),
            ('Travel Channel', '/networks/82/travel-channel', 'https://i.imgur.com/mWXv7SF.png'),
            ('TruTV', '/networks/84/trutv', 'https://i.imgur.com/HnB3zfc.png'),
            ('USA', '/networks/30/usa-network', 'https://i.imgur.com/Doccw9E.png'),
            ('VH1', '/networks/55/vh1', 'https://i.imgur.com/IUtHYzA.png'),
            ('WGN', '/networks/28/wgn-america', 'https://i.imgur.com/TL6MzgO.png')
        ]

        for i in networks: self.list.append(
            {'name': i[0], 'url': self.tvmaze_link + i[1], 'image': i[2], 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def languages(self):
        languages = [
            ('Arabic', 'ar'),
            ('Bosnian', 'bs'),
            ('Bulgarian', 'bg'),
            ('Chinese', 'zh'),
            ('Croatian', 'hr'),
            ('Dutch', 'nl'),
            ('English', 'en'),
            ('Finnish', 'fi'),
            ('French', 'fr'),
            ('German', 'de'),
            ('Greek', 'el'),
            ('Hebrew', 'he'),
            ('Hindi ', 'hi'),
            ('Hungarian', 'hu'),
            ('Icelandic', 'is'),
            ('Italian', 'it'),
            ('Japanese', 'ja'),
            ('Korean', 'ko'),
            ('Norwegian', 'no'),
            ('Persian', 'fa'),
            ('Polish', 'pl'),
            ('Portuguese', 'pt'),
            ('Punjabi', 'pa'),
            ('Romanian', 'ro'),
            ('Russian', 'ru'),
            ('Serbian', 'sr'),
            ('Spanish', 'es'),
            ('Swedish', 'sv'),
            ('Turkish', 'tr'),
            ('Ukrainian', 'uk')
        ]

        for i in languages: self.list.append(
            {'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def certifications(self):
        certificates = ['TV-G', 'TV-PG', 'TV-14', 'TV-MA']

    def genres(self):
        self.list.append({'name': 'Akcja', 'url': 'action', 'image': 'action.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Przygodowe', 'url': 'adventure', 'image': 'adventure.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Animacja', 'url': 'animation', 'image': 'animation.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Anime', 'url': 'anime', 'image': 'anime.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Biograficzny', 'url': 'biography', 'image': 'biography.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Komedia', 'url': 'comedy', 'image': 'comedy.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Kryminalny', 'url': 'crime', 'image': 'crime.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Dramat', 'url': 'drama', 'image': 'drama.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Familijny', 'url': 'family', 'image': 'family.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Fantasy', 'url': 'fantasy', 'image': 'fantasy.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Game-Show', 'url': 'game_show', 'image': 'gameshow.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Historyczny', 'url': 'history', 'image': 'history.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Horror', 'url': 'horror', 'image': 'horror.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Muzyczny', 'url': 'music', 'image': 'music.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Musical', 'url': 'musical', 'image': 'musical.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Tajemnica', 'url': 'mystery', 'image': 'mystery.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'News', 'url': 'news', 'image': 'news.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Reality-TV', 'url': 'reality_tv', 'image': 'reality.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Romans', 'url': 'romance', 'image': 'romance.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Science Fiction', 'url': 'sci_fi', 'image': 'scifi.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Sport', 'url': 'sport', 'image': 'sport.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Talk-Show', 'url': 'talk_show', 'image': 'talkshow.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Thriller', 'url': 'thriller', 'image': 'thriller.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Wojenny', 'url': 'war', 'image': 'war.jpg', 'action': 'tvshows'})
        self.list.append({'name': 'Western', 'url': 'western', 'image': 'western.jpg', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

        for i in certificates: self.list.append(
            {'name': str(i), 'url': self.certification_link % str(i).replace('-', '_').lower(),
             'image': 'certificates.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def persons(self, url):
        if url == None:
            self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
        else:
            self.list = cache.get(self.imdb_person_list, 1, url)

        for i in range(0, len(self.list)): self.list[i].update({'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def userlists(self):
        try:
            userlists = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            activity = trakt.getActivity()
        except:
            pass

        try:
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlists_link,
                                            self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
        except:
            pass
        try:
            self.list = []
            if not self.imdb_user: raise Exception()
            userlists += cache.get(self.imdb_user_list, 0, self.imdblists_link)
        except:
            pass
        try:
            self.list = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link,
                                            self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlikedlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
        except:
            pass

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def trakt_list(self, url, user):
        try:
            dupes = []

            q = dict(urllib.parse_qsl(urllib.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urllib.urlparse(url).query, '') + '?' + q

            result = trakt.getTraktAsJson(u)
            result = convert(result)

            items = []
            for i in result:
                try:
                    items.append(i['show'])
                except:
                    pass
            if len(items) == 0:
                items = result
        except:
            return

        try:
            q = dict(urllib.parse_qsl(urllib.urlsplit(url).query))
            if not int(q['limit']) == len(items): raise Exception()
            q.update({'page': str(int(q['page']) + 1)})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            next = url.replace('?' + urllib.urlparse(url).query, '') + '?' + q
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = item['title']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)

                year = item['year']
                year = re.sub('[^0-9]', '', str(year))

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '':
                    imdb = '0'
                else:
                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                tvdb = item['ids']['tvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))

                if tvdb == None or tvdb == '' or tvdb in dupes: raise Exception()
                dupes.append(tvdb)

                try:
                    premiered = item['first_aired']
                except:
                    premiered = '0'
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'

                try:
                    studio = item['network']
                except:
                    studio = '0'
                if studio == None: studio = '0'

                try:
                    genre = item['genres']
                except:
                    genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)

                try:
                    duration = str(item['runtime'])
                except:
                    duration = '0'
                if duration == None: duration = '0'

                try:
                    rating = str(item['rating'])
                except:
                    rating = '0'
                if rating == None or rating == '0.0': rating = '0'

                try:
                    votes = str(item['votes'])
                except:
                    votes = '0'
                try:
                    votes = str(format(int(votes), ',d'))
                except:
                    pass
                if votes == None: votes = '0'

                try:
                    mpaa = item['certification']
                except:
                    mpaa = '0'
                if mpaa == None: mpaa = '0'

                try:
                    plot = item['overview']
                except:
                    plot = '0'
                if plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)

                self.list.append(
                    {'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio,
                     'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot,
                     'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'next': next})
            except:
                pass

        return self.list

    def trakt_user_list(self, url, user):
        try:
            items = trakt.getTraktAsJson(url)
        except:
            pass

        for item in items:
            try:
                try:
                    name = item['list']['name']
                except:
                    name = item['name']
                name = client.replaceHTMLCodes(name)

                try:
                    url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except:
                    url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list

    def imdb_list(self, url):
        try:
            headers = {'Accept-Language': self.lang}
            dupes = []

            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i,
                                  (self.datetime - datetime.timedelta(days=int(i))).strftime('%Y-%m-%d'))

            def imdb_watchlist_id(url):
                return client.parseDOM(client.request(url, headers=headers), 'meta', ret='content',
                                       attrs={'property': 'pageId'})[0]

            if url == self.imdbwatchlist_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url

            elif url == self.imdbwatchlist2_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist2_link % url

            result = client.request(url, headers=headers)

            result = result.replace('\n', ' ')

            items = client.parseDOM(result, 'div', attrs={'class': 'lister-item .+?'})
            items += client.parseDOM(result, 'div', attrs={'class': 'list_item.+?'})
        except:
            return

        try:
            next = client.parseDOM(result, 'a', ret='href', attrs={'class': '.+?ister-page-nex.+?'})

            if len(next) == 0:
                next = client.parseDOM(result, 'div', attrs={'class': 'pagination'})[0]
                next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
                next = [i[0] for i in next if 'Next' in i[1]]

            next = url.replace(urllib.urlparse(url).query, urllib.urlparse(next[0]).query)
            next = client.replaceHTMLCodes(next)
        except:
            next = ''

        for item in items:
            try:
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)

                year = client.parseDOM(item, 'span', attrs={'class': 'lister-item-year.+?'})
                year += client.parseDOM(item, 'span', attrs={'class': 'year_type'})
                year = re.findall('(\d{4})', year[0])[0]

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = re.findall('(tt\d*)', imdb)[0]

                if imdb in dupes: raise Exception()
                dupes.append(imdb)

                try:
                    poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except:
                    poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = client.replaceHTMLCodes(poster)

                rating = '0'
                try:
                    rating = client.parseDOM(item, 'span', attrs={'class': 'rating-rating'})[0]
                except:
                    pass
                try:
                    rating = client.parseDOM(rating, 'span', attrs={'class': 'value'})[0]
                except:
                    rating = '0'
                try:
                    rating = client.parseDOM(item, 'div', ret='data-value', attrs={'class': '.*?imdb-rating'})[0]
                except:
                    pass
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)

                plot = '0'
                try:
                    plot = client.parseDOM(item, 'p', attrs={'class': 'text-muted'})[0]
                except:
                    pass
                try:
                    plot = client.parseDOM(item, 'div', attrs={'class': 'item_description'})[0]
                except:
                    pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                plot = re.sub('<.+?>|</.+?>', '', plot)
                if not plot: plot = '0'
                plot = client.replaceHTMLCodes(plot)

                self.list.append(
                    {'title': title, 'originaltitle': title, 'year': year, 'rating': rating, 'plot': plot, 'imdb': imdb,
                     'tvdb': '0', 'poster': poster, 'next': next})
            except:
                pass

        return self.list

    def imdb_person_list(self, url):
        try:
            result = client.request(url)
            items = client.parseDOM(result, 'div', attrs={'class': '.+?etail'})
        except:
            return

        for item in items:
            try:
                name = client.parseDOM(item, 'img', ret='alt')[0]
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = re.findall('(nm\d*)', url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = client.parseDOM(item, 'img', ret='src')[0]
                # if not ('._SX' in image or '._SY' in image): raise Exception()
                image = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
                image = client.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list

    def imdb_user_list(self, url):
        try:
            result = client.request(url)
            items = client.parseDOM(result, 'li', attrs={'class': 'ipl-zebra-list__item user-list'})
        except:
            pass

        for item in items:
            try:
                name = client.parseDOM(item, 'a')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = url = url.split('/list/', 1)[-1].strip('/')
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list

    def tvmaze_list(self, url):
        try:
            result = client.request(url)
            result = client.parseDOM(result, 'section', attrs={'id': 'this-seasons-shows'})

            items = client.parseDOM(result, 'div', attrs={'class': 'content auto cell'})
            items = [client.parseDOM(i, 'a', ret='href') for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = [re.findall('/(\d+)/', i) for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = items[:50]
        except:
            return

        def items_list(i):
            try:
                url = self.tvmaze_info_link % i

                item = client.request(url)
                item = json.loads(item)

                title = item['name']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['premiered']
                year = re.findall('(\d{4})', year)[0]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['externals']['imdb']
                if imdb == None or imdb == '':
                    imdb = '0'
                else:
                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                tvdb = item['externals']['thetvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                if tvdb == None or tvdb == '': raise Exception()

                try:
                    poster = item['image']['original']
                except:
                    poster = '0'
                if not poster: poster = '0'
                poster = poster.encode('utf-8')

                premiered = item['premiered']
                try:
                    premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except:
                    premiered = '0'
                premiered = premiered.encode('utf-8')

                try:
                    studio = item['network']['name']
                except:
                    studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try:
                    genre = item['genres']
                except:
                    genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')

                try:
                    duration = item['runtime']
                except:
                    duration = '0'
                if duration == None: duration = '0'
                duration = str(duration)
                duration = duration.encode('utf-8')

                try:
                    rating = item['rating']['average']
                except:
                    rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = str(rating)
                rating = rating.encode('utf-8')

                try:
                    plot = item['summary']
                except:
                    plot = '0'
                if plot == None: plot = '0'
                plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                try:
                    content = item['type'].lower()
                except:
                    content = '0'
                if not content: content = '0'
                content = content.encode('utf-8')

                self.list.append(
                    {'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio,
                     'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb,
                     'poster': poster, 'content': content})
            except:
                pass

        try:
            import threading
            threads = []
            for i in items: threads.append(threading.Thread(target=items_list, args=(i,)))
            [i.start() for i in threads]
            [i.join() for i in threads]

            filter = [i for i in self.list if i['content'] == 'scripted']
            filter += [i for i in self.list if not i['content'] == 'scripted']
            self.list = filter

            return self.list
        except:
            return

    def worker(self, level=1):
        self.meta = []
        total = len(self.list)

        self.fanart_tv_headers = {'api-key': control.setting('fanart.tv.dev')}
        if not self.fanart_tv_user == '':
            self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)
        import threading
        self.list = convert(self.list)
        for r in range(0, total, 40):
            threads = []
            for i in range(r, r + 40):
                if i <= total: threads.append(threading.Thread(target=self.super_info, args=(i,)))
            [i.start() for i in threads]
            [i.join() for i in threads]

            if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if not i['tvdb'] == '0']

        if self.fanart_tv_user == '':
            for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})

    def super_info(self, i):
        #if self.list[i]['metacache'] == True: raise Exception()

        imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
        tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'

        if imdb == '0':
            try:
                imdb = trakt.SearchTVShow(urllib.quote_plus(self.list[i]['title']), self.list[i]['year'], full=False)[0]
                imdb = imdb.get('show', '0')
                imdb = imdb.get('ids', {}).get('imdb', '0')
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                if not imdb: imdb = '0'
            except:
                imdb = '0'

        if tvdb == '0' and not imdb == '0':
            url = self.tvdb_by_imdb % imdb

            result = client.request(url, timeout='10')

            try:
                tvdb = client.parseDOM(result, 'seriesid')[0]
            except:
                tvdb = '0'

            try:
                name = client.parseDOM(result, 'SeriesName')[0]
            except:
                name = '0'
            dupe = re.findall('[***]Duplicate (\d*)[***]', name)
            if dupe: tvdb = str(dupe[0])

            if not tvdb: tvdb = '0'

        if tvdb == '0':
            try:
                url = self.tvdb_by_query % (urllib.quote_plus(self.list[i]['title']))

                years = [str(self.list[i]['year']), str(int(self.list[i]['year']) + 1), str(int(self.list[i]['year']) - 1)]

                tvdb = client.request(url, timeout='10')
                tvdb = re.sub(r'[^\x00-\x7F]+', '', tvdb)
                tvdb = client.replaceHTMLCodes(tvdb)
                tvdb = client.parseDOM(tvdb, 'Series')
                tvdb = [(x, client.parseDOM(x, 'SeriesName'), client.parseDOM(x, 'FirstAired')) for x in tvdb]
                tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if len(x[1]) > 0 and len(x[2]) > 0]
                tvdb = [x for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1])]
                tvdb = [x[0][0] for x in tvdb if any(y in x[2] for y in years)][0]
                tvdb = client.parseDOM(tvdb, 'seriesid')[0]

                if not tvdb: tvdb = '0'
            except:
                return
        if not self.tvdb_jwt_token:
            url = self.tvdb_info_link % tvdb
            item = client.request(url, timeout='10')
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0', 'Accept': 'application/json', 'Accept-Language': self.lang, 'Authorization': 'Bearer %s' % self.tvdb_jwt_token, 'Connection': 'keep-alive', 'Referer': 'https://api.thetvdb.com/swagger', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache', 'TE': 'Trailers', }

            url = "https://api.thetvdb.com/series/%s" % tvdb
            item = json.loads(requests.get(url, timeout=10, headers=headers).text)
        if item == None: raise Exception()

        if imdb == '0':
            imdb = ''
            try:
                imdb = item['data']['imdbId']
            except:
                pass
            try:
                imdb = client.parseDOM(item, 'IMDB_ID')[0]
            except:
                pass
            if not imdb: imdb = '0'
            imdb = imdb.encode('utf-8')

        title = ''
        try:
            title = client.parseDOM(item, 'SeriesName')[0]
        except:
            pass
        try:
            title = item['data']['seriesName']
        except:
            pass
        if not title: title = '0'
        title = client.replaceHTMLCodes(title)

        year = ''
        try:
            year = client.parseDOM(item, 'FirstAired')[0]
        except:
            pass
        try:
            year = item['data']['firstAired']
        except:
            pass
        try:
            year = re.compile('(\d{4})').findall(year)[0]
        except:
            year = ''
        if not year: year = '0'

        premiered = ''
        try:
            premiered = client.parseDOM(item, 'FirstAired')[0]
        except:
            pass
        try:
            premiered = item['data']['firstAired']
        except:
            pass
        if not premiered: premiered = '0'
        premiered = client.replaceHTMLCodes(premiered)

        studio = ''
        try:
            studio = item['data']['network']
        except:
            pass
        try:
            studio = client.parseDOM(item, 'Network')[0]
        except:
            pass
        if not studio: studio = '0'
        studio = client.replaceHTMLCodes(studio)

        genre = ''
        try:
            genre = item['data']['genre']
        except:
            pass
        try:
            genre = client.parseDOM(item, 'Genre')[0]
            genre = [x for x in genre.split('|') if not x == '']
        except:
            pass
        genre = ' / '.join(genre)
        if not genre: genre = '0'
        genre = client.replaceHTMLCodes(genre)

        duration = ''
        try:
            duration = item['data']['runtime']
        except:
            pass
        try:
            duration = client.parseDOM(item, 'Runtime')[0]
        except:
            pass
        if not duration: duration = '0'
        duration = client.replaceHTMLCodes(duration)

        rating = ''
        try:
            rating = item['data']['siteRating']
        except:
            pass
        try:
            rating = client.parseDOM(item, 'Rating')[0]
        except:
            pass
        if 'rating' in self.list[i] and not self.list[i]['rating'] == '0':
            rating = self.list[i]['rating']
        if not rating: rating = '0'
        rating = client.replaceHTMLCodes(str(rating))

        votes = ''
        try:
            votes = item['data']['siteRatingCount']
        except:
            pass
        try:
            votes = client.parseDOM(item, 'RatingCount')[0]
        except:
            pass
        if 'votes' in self.list[i] and not self.list[i]['votes'] == '0':
            votes = self.list[i]['votes']
        if not votes: votes = '0'
        votes = client.replaceHTMLCodes(str(votes))

        mpaa = ''
        try:
            mpaa = item['data']['rating']
        except:
            pass
        try:
            mpaa = client.parseDOM(item, 'ContentRating')[0]
        except:
            pass
        if not mpaa: mpaa = '0'
        mpaa = client.replaceHTMLCodes(mpaa)

        try:
            cast = client.parseDOM(item, 'Actors')[0]
        except:
            cast = ''
        cast = [x for x in cast.split('|') if not x == '']
        try:
            cast = [(x.encode('utf-8'), '') for x in cast]
        except:
            cast = []
        if not cast: cast = '0'

        plot = ''
        try:
            plot = item['data']['overview']
        except:
            pass
        try:
            plot = client.parseDOM(item, 'Overview')[0]
        except:
            pass
        if not plot: plot = '0'

        plot = client.replaceHTMLCodes(plot)

        poster = ''
        try:
            poster = item['data']['poster']
        except:
            pass
        try:
            poster = client.parseDOM(item, 'poster')[0]
        except:
            pass
        if not poster == '':
            poster = self.tvdb_image + poster
        else:
            poster = '0'
        if 'poster' in self.list[i] and poster == '0': poster = self.list[i]['poster']
        poster = client.replaceHTMLCodes(poster)

        banner = ''
        try:
            banner = item['data']['banner']
        except:
            pass
        try:
            banner = client.parseDOM(item, 'banner')[0]
        except:
            pass
        if not banner == '':
            banner = self.tvdb_image + banner
        else:
            banner = '0'
        banner = client.replaceHTMLCodes(banner)

        fanart = ''
        try:
            fanart = item['data']['fanart']
        except:
            pass
        try:
            fanart = client.parseDOM(item, 'fanart')[0]
        except:
            pass
        if not fanart == '':
            fanart = self.tvdb_image + fanart
        else:
            fanart = '0'
        fanart = client.replaceHTMLCodes(fanart)

        try:
            artmeta = True
            # if self.fanart_tv_user == '': raise Exception()
            art = client.request(self.fanart_tv_art_link % tvdb, headers=self.fanart_tv_headers, timeout='10', error=True)
            try:
                art = json.loads(art)
            except:
                artmeta = False
        except:
            pass

        try:
            poster2 = art['tvposter']
            poster2 = [x for x in poster2 if x.get('lang') == self.lang][::-1] + [x for x in poster2 if x.get('lang') == 'en'][::-1] + [x for x in poster2 if x.get('lang') in ['00', '']][::-1]
            poster2 = poster2[0]['url'].encode('utf-8')
        except:
            poster2 = '0'

        try:
            fanart2 = art['showbackground']
            fanart2 = [x for x in fanart2 if x.get('lang') == self.lang][::-1] + [x for x in fanart2 if x.get('lang') == 'en'][::-1] + [x for x in fanart2 if x.get('lang') in ['00', '']][::-1]
            fanart2 = fanart2[0]['url'].encode('utf-8')
        except:
            fanart2 = '0'

        try:
            banner2 = art['tvbanner']
            banner2 = [x for x in banner2 if x.get('lang') == self.lang][::-1] + [x for x in banner2 if x.get('lang') == 'en'][::-1] + [x for x in banner2 if x.get('lang') in ['00', '']][::-1]
            banner2 = banner2[0]['url'].encode('utf-8')
        except:
            banner2 = '0'

        try:
            if 'hdtvlogo' in art:
                clearlogo = art['hdtvlogo']
            else:
                clearlogo = art['clearlogo']
            clearlogo = [x for x in clearlogo if x.get('lang') == self.lang][::-1] + [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') in ['00', '']][::-1]
            clearlogo = clearlogo[0]['url'].encode('utf-8')
        except:
            clearlogo = '0'

        try:
            if 'hdclearart' in art:
                clearart = art['hdclearart']
            else:
                clearart = art['clearart']
            clearart = [x for x in clearart if x.get('lang') == self.lang][::-1] + [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') in ['00', '']][::-1]
            clearart = clearart[0]['url'].encode('utf-8')
        except:
            clearart = '0'

        item = {'title': title, 'year': year, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'poster2': poster2, 'banner': banner, 'banner2': banner2, 'fanart': fanart, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': cast, 'plot': plot}
        item = dict((k, v) for k, v in item.items() if not v == '0')
        self.list[i].update(item)

        if artmeta == False: raise Exception()

        meta = {'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}
        self.meta.append(meta)

    def tvshowDirectory(self, items):
        if items == None or len(items) == 0: control.idle(); sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try:
            isOld = False;
            control.item().getArt('type')
        except:
            isOld = True

        indicators = playcount.getTVShowIndicators(
            refresh=True) if action == 'tvshows' else playcount.getTVShowIndicators()

        flatten = True if control.setting('flatten.tvshows') == 'true' else False

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(
            32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(
            32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        nextMenu = control.lang(32053).encode('utf-8')

        playRandom = control.lang(32535).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                label = i['title'].encode().decode("utf-8")
                systitle = sysname = urllib.quote_plus(i['originaltitle'])
                sysimage = urllib.quote_plus(i['poster'])
                imdb, tvdb, year = i['imdb'], i['tvdb'], i['year']

                meta = dict((k, v) for k, v in i.items() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tvdb_id': tvdb})
                meta.update({'mediatype': 'tvshow'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(label))})
                if not 'duration' in i:
                    meta.update({'duration': '60'})
                elif i['duration'] == '0':
                    meta.update({'duration': '60'})
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass
                try:
                    meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except:
                    pass

                try:
                    overlay = int(playcount.getTVShowOverlay(indicators, tvdb))
                    if overlay == 7:
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                if flatten == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (
                        sysaddon, systitle, year, imdb, tvdb)
                else:
                    url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (
                        sysaddon, systitle, year, imdb, tvdb)

                sysurl = urllib.quote_plus(url)

                cm = []
                cm.append(('Znajdź podobne',
                           'ActivateWindow(10025,%s?action=tvshows&url=https://api.trakt.tv/shows/%s/related,return)' % (
                               sysaddon, imdb)))
                cm.append((playRandom,
                           'RunPlugin(%s?action=random&rtype=season&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (
                               sysaddon, urllib.quote_plus(systitle), urllib.quote_plus(year), urllib.quote_plus(imdb),
                               urllib.quote_plus(tvdb))))

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&query=7)' % (
                    sysaddon, systitle, imdb, tvdb)))

                cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&query=6)' % (
                    sysaddon, systitle, imdb, tvdb)))

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (
                        sysaddon, sysname, tvdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))

                cm.append((addToLibrary,
                           'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (
                               sysaddon, systitle, year, imdb, tvdb)))

                item = control.item(label=label)

                art = {}

                if 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
                # elif 'poster2' in i and not i['poster2'] == '0':
                # art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                # elif 'banner2' in i and not i['banner2'] == '0':
                # art.update({'banner': i['banner2']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                # elif settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
                # item.setProperty('Fanart_Image', i['fanart2'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                meta.pop("imdb", None)
                meta.pop("tmdb_id", None)
                meta.pop("imdb_id", None)
                meta.pop("poster", None)
                meta.pop("clearlogo", None)
                meta.pop("clearart", None)
                meta.pop("fanart", None)
                meta.pop("fanart2", None)
                meta.pop("imdb", None)
                meta.pop("tmdb", None)
                meta.pop("metacache", None)
                meta.pop("poster2", None)
                meta.pop("poster3", None)
                meta.pop("banner", None)
                meta.pop("next", None)
                meta.pop("tvdb", None)
                meta.pop("tvdb_id", None)
                meta.pop("banner2", None)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setInfo(type='Video', infoLabels=meta)

                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        try:
            url = items[0]['next']
            if not url: raise Exception()

            icon = control.addonNext()
            url = '%s?action=tvshowPage&url=%s' % (sysaddon, urllib.quote_plus(url))
            sysurl = urllib.quote_plus(url)

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=sysurl, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, 'tvshows')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('tvshows', {'skin.estuary': 55, 'skin.confluence': 500})

    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle(); sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        queueMenu = control.lang(32065).encode('utf-8')

        playRandom = control.lang(32535).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'):
                    thumb = i['image']
                elif not artPath == None:
                    thumb = os.path.join(artPath, i['image'])
                else:
                    thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try:
                    url += '&url=%s' % urllib.quote_plus(i['url'])
                except:
                    pass

                cm = []

                cm.append((playRandom,
                           'RunPlugin(%s?action=random&rtype=show&url=%s)' % (sysaddon, urllib.quote_plus(i['url']))))

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try:
                    cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowsToLibrary&url=%s)' % (
                        sysaddon, urllib.quote_plus(i['context']))))
                except:
                    pass

                item = control.item(label=name)

                item.setArt({'icon': thumb, 'thumb': thumb})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)
