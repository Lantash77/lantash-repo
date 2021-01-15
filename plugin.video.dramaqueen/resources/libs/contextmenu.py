# -*- coding: utf-8 -*-

### Imports ###
import os
import re
import sys
import xbmc
import xbmcaddon

from addon.common.addon import Addon  # może trzeba więcej
import favourites
#######
_addon = Addon('plugin.video.anime-iptv', sys.argv)
lang = xbmcaddon.Addon().getLocalizedString
###########


def addpr(r, s=''):
    return _addon.queries.get(r, s)


def addst(r, s=''):
    return _addon.get_setting(r)


def tfalse(r, d=False):
    if   (r.lower() == 'true') or (r.lower() == 't') or (r.lower() == 'y') or (r.lower() == '1') or (r.lower() == 'yes'):
        return True
    elif (r.lower() == 'false') or (r.lower() == 'f') or (r.lower() == 'n') or (r.lower() == '0') or (r.lower() == 'no'):
        return False
    else:
        return d


def DoLabs2LB(labs, subfav=''):
    LB = {}
    n = 'title'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'year'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'img'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'fanart'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'plot'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'url'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'country'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'genres'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'todoparams'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'commonid'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'commonid2'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'plot'
    try:
        LB[n] = str(labs[n])
    except:
        LB[n] = ''
    n = 'site'
    try:
        LB[n] = labs[n]
    except:
        try:
            LB[n] = addpr(n, '')
        except:
            LB[n] = ''
    n = 'section'
    try:
        LB[n] = labs[n]
    except:
        try:
            LB[n] = addpr(n, '')
        except:
            LB[n] = ''
    return LB


def filename_filter_out_year(name=''):
    years = re.compile(' \((\d+)\)').findall('__' + name + '__')
    for year in years:
        name = name.replace(' (' + year + ')', '')
    name = name.strip()
    return name


def ContextMenu_Movies(labs={}):
    contextMenuItems = []
    nameonly = filename_filter_out_year(labs['title'])
    try:
        site = labs['site']
    except:
        site = addpr('site', '')
    try:
        section = labs['section']
    except:
        section = addpr('section', '')
    if tfalse(addst("CMI_ShowInfo")) == True:
        contextMenuItems.append(('Movie Info', 'XBMC.Action(Info)'))
    if labs == {}:
        return contextMenuItems
    if (tfalse(addst("CMI_SearchKissAnime")) == True) and (os.path.exists(xbmc.translatePath("special://home/addons/") + 'plugin.video.kissanime')):
        contextMenuItems.append(('Search KissAnime', 'XBMC.Container.Update(%s?mode=%s&pageno=1&pagecount=1&title=%s)' % ('plugin://plugin.video.kissanime/', 'Search', nameonly)))
    if (tfalse(addst("CMI_SearchSolarMovieso")) == True) and (os.path.exists(xbmc.translatePath("special://home/addons/") + 'plugin.video.solarmovie.so')):
        contextMenuItems.append(('Search Solarmovie.so', 'XBMC.Container.Update(%s?mode=%s&section=%s&title=%s)' % ('plugin://plugin.video.solarmovie.so/', 'Search', 'movies', nameonly)))
    if (tfalse(addst("CMI_Search1Channel")) == True) and (os.path.exists(xbmc.translatePath("special://home/addons/") + 'plugin.video.1channel')):
        contextMenuItems.append(('Search 1Channel', 'XBMC.Container.Update(%s?mode=7000&section=%s&query=%s)' % ('plugin://plugin.video.1channel/', 'movies', nameonly)))
    try:
        WRFC = (lang(30001).encode('utf-8'))
        LB = DoLabs2LB(labs)
        LB['mode'] = 'cFavoritesAdd'
        P1 = 'XBMC.RunPlugin(%s)'
        LB['subfav'] = ''
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.1.name'), Pars))
        LB['subfav'] = '2'
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.2.name'), Pars))
        LB['subfav'] = '3'
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.3.name'), Pars))
        LB['subfav'] = '4'
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.4.name'), Pars))
        LB['subfav'] = '5'
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.5.name'), Pars))
        LB['subfav'] = '6'
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.6.name'), Pars))
        LB['subfav'] = '7'
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((WRFC + addst('fav.movies.7.name'), Pars))
    except:
        pass


def ContextMenu_Series(labs={}):
    contextMenuItems = []
    contextMenuItems.append(('Movie info', 'XBMC.Action(Info)'))
    nameonly = filename_filter_out_year(labs['title'])
    try:
        site = labs['site']
    except:
        site = addpr('site','')
    try:
        section = labs['section']
    except:
        section = addpr('section', '')
    if tfalse(addst("CMI_ShowInfo")) == True:
        contextMenuItems.append(('Show Info', 'XBMC.Action(Info)'))
    if labs == {}:
        return contextMenuItems
    try:
        WRFC = (lang(30001).encode('utf-8'))
        WRFCr = (lang(30006).encode('utf-8'))
        LB = DoLabs2LB(labs)
        McFA = 'cFavoritesAdd'
        McFR = 'cFavoritesRemove'
        LB['mode'] = McFA
        P1 = 'XBMC.RunPlugin(%s)'
        LB['subfav'] = '1'
        if favourites.fav__COMMON__check(LB['site'], LB['section'], LB['title'], LB['year'], LB['subfav']) == True:
            LB['mode'] = McFR
            LabelName = WRFCr + WRFC + addst('fav.tv.' + LB['subfav'] + '.name')
        else:
            LB['mode'] = McFA
            LabelName = WRFC + addst('fav.tv.' + LB['subfav'] + '.name')
        LB['subfav'] = ''
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append((LabelName, Pars))
        for nn in ['2', '3', '4']:
            LB['subfav'] = nn
            if favourites.fav__COMMON__check(LB['site'], LB['section'], LB['title'], LB['year'], LB['subfav']) == True:
                LB['mode'] = McFR
                LabelName = WRFCr + WRFC + addst('fav.tv.' + LB['subfav'] + '.name')
            else:
                LB['mode'] = McFA
            LabelName = WRFC + addst('fav.tv.' + LB['subfav'] + '.name')
            Pars = P1 % _addon.build_plugin_url(LB)
            contextMenuItems.append((LabelName, Pars))
    except:
        pass
    LB = DoLabs2LB(labs)
    LB['mode'] = 'addView'
    Pars = 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url(LB)
    contextMenuItems.append(('Set View', Pars))
    return contextMenuItems


def ContextMenu_Episodes(labs={}):
    contextMenuItems = []
    contextMenuItems.append(('Watched/Unwatched', 'XBMC.Action(ToggleWatched)'))
    if labs == {}:
        return contextMenuItems
    return contextMenuItems


def ContextMenu_Favorites(labs={}):
    contextMenuItems = []
    contextMenuItems.append(('Movie info', 'XBMC.Action(Info)'))
    nameonly = filename_filter_out_year(labs['title'])
    try:
        site = labs['site']
    except:
        site = addpr('site', '')
    try:
        section = labs['section']
    except:
        section = addpr('section', '')
    try:
        _subfav = addpr('subfav', '')
    except:
        _subfav = ''
    if tfalse(addst("CMI_ShowInfo")) == True:
        contextMenuItems.append(('Info', 'XBMC.Action(Info)'))
    if labs == {}:
        return contextMenuItems
    try:
        if _subfav == '':
            _sf = '1'
        else:
            _sf = _subfav
        WRFC = (lang(30001).encode('utf-8'))
        LB = DoLabs2LB(labs)
        LB['mode'] = 'cFavoritesAdd'
        P1 = 'XBMC.RunPlugin(%s)'
        if _sf is not '1':
            LB['subfav'] = ''
            Pars = P1 % _addon.build_plugin_url(LB)
            contextMenuItems.append((WRFC + addst('fav.tv.1.name'), Pars))
        if _sf is not '2':
            LB['subfav'] = '2'
            Pars = P1 % _addon.build_plugin_url(LB)
            contextMenuItems.append((WRFC + addst('fav.tv.2.name'), Pars))
        if _sf is not '3':
            LB['subfav'] = '3'
            Pars = P1 % _addon.build_plugin_url(LB)
            contextMenuItems.append((WRFC + addst('fav.tv.3.name'), Pars))
        if _sf is not '4':
            LB['subfav'] = '4'
            Pars = P1 % _addon.build_plugin_url(LB)
            contextMenuItems.append((WRFC + addst('fav.tv.4.name'), Pars))
        LB['mode'] = 'cFavoritesRemove'
        LB['subfav'] = _subfav
        Pars = P1 % _addon.build_plugin_url(LB)
        contextMenuItems.append(((lang(30006).encode('utf-8')) + WRFC + addst('fav.tv.' + _sf + '.name'), Pars))
    except:
        pass
    return contextMenuItems