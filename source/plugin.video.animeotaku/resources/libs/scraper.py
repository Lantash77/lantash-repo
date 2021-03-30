# -*- coding: UTF-8 -*-

import re
import requests

try:
    import json
except:
    import simplejson as json


def ScrapJikan(title=''):
### Jikan Scraper  ###

    Jikan = 'https://api.jikan.moe/v3/search/anime?q='


    url = Jikan + title
    try:
        result = requests.get(url).text
        result = json.loads(result)['results'][0]
        return result['image_url']
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

    return html

def Scrap(title, type):
### TMDB API SCRAPER ###

    titleENC = String2HTML(title)
    TMDBURL = 'https://api.themoviedb.org/3/{}'
    TMDBAPI = '?api_key=af3a53eb387d57fc935e9128468b1899&query='
    TMDBAPICONF = TMDBURL.format('configuration') + TMDBAPI
    conf = json.loads(requests.get(TMDBAPICONF).text)['images']
    backdrop_base_url = conf['secure_base_url'] + conf['backdrop_sizes'][-1]

    if type == 'serie':
        queryURLPL = TMDBURL.format('search/tv') + TMDBAPI + titleENC + '&language=pl-PL'
        queryURL = TMDBURL.format('search/tv') + TMDBAPI + titleENC
    elif type == 'film':
        queryURLPL = TMDBURL.format('search/movie') + TMDBAPI + titleENC + '&language=pl-PL'
        queryURL = TMDBURL.format('search/movie') + TMDBAPI + titleENC
    r = requests.get(queryURLPL).text

    if json.loads(r)['total_results'] == 0:
        r = requests.get(queryURL).text
        if json.loads(r)['total_results'] == 0:
            backdrop_link = ''
            poster_link = ScrapJikan(title)
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
        poster_link = ScrapJikan(title)

    return(poster_link, backdrop_link)



