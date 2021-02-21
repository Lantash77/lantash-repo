# -*- coding: UTF-8 -*-
#####Python 2.7 #######


import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.libs import addon_tools as addon


reload(sys)
sys.setdefaultencoding('UTF8')

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')

setting = my_addon.getSetting
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/art/japan/')
default_background = MEDIA + "fanart.jpg"

iconSite = PATH + 'icon.png'
iconWbijam = MEDIA + 'wbijam.jpg'
iconOdcinki = MEDIA + 'animeodcinki.jpg'
iconShinden = MEDIA + 'animeshinden.jpg'
iconAnimezone = MEDIA + 'animezone.jpg'
iconstrefadb = MEDIA + 'strefadb.jpg'


icnoAnimecentrum = MEDIA + 'animecentrum.jpg'
iconAnime4fun = MEDIA + 'anime4fun.jpg'
iconDiff = MEDIA + 'diffanime.jpg'
iconstrefadb = MEDIA + 'strefadb.jpg'
iconstrefadballs = MEDIA + 'Dragon_Balls_.png'
iconkresk = MEDIA + 'kreskoweczki.jpg'

iconAnimejoy = MEDIA + 'animejoy.jpg'
iconkresk = MEDIA + 'kreskoweczki.jpg'
iconsenpai = MEDIA + 'senpai.jpg'
iconFavs = MEDIA + 'ulubione.jpg'
fanartSite = MEDIA + 'fanart.jpg'
fanartIPTV = MEDIA + 'fanart.jpg'
fanartAnime4fun = MEDIA + 'fanart.jpg'
fanartAol = MEDIA + 'fanart.jpg'
fanartdragon = MEDIA + 'dragon.jpg'
#nexticon = MEDIA + '/art/next.png'
base_link = ''

global cookie
#Odkomentować przed wrzuceniem
setting = xbmcaddon.Addon().getSetting
SiteName = 'AnimeIPTV'
SiteTag = 'AnimeIPTV'
mainSite1 = 'http://www.inne.wbijam.pl/'
mainSite2 = 'https://anime-odcinki.pl/'
mainSite3 = 'https://shinden.pl/'
mainSite4 = 'https://www.animezone.pl/'
mainSite5 = 'https://strefadb.pl/'
mainSite6 = 'https://animeon.pl/'
mainSite7 = 'http://www.kreskoweczki.pl'



def MainMenu():
###Wbijam.pl###
    if setting('Wbijam') == 'true':
        addon.addDir('[COLOR=%s]Wbijam.pl[/COLOR]' % 'blue', 
                     'https://inne.wbijam.pl/', mode='Pagewbijam',
                     fanart=default_background, thumb=iconWbijam, isFolder=True)
###Anime Odcinki###
    if setting('AnimeOdcinki') == 'true':
        addon.addDir('[COLOR=%s]Anime Odcinki[/COLOR]' % 'blue', 
                     'https://anime-odcinki.pl/', mode='AnimeOdcinki',
                     fanart=default_background, thumb=iconOdcinki, isFolder=True)
###Shinden.pl###
    if setting('Shinden') == 'true':
        addon.addDir('[COLOR=%s]Shinden.pl[/COLOR]' % 'blue', 
                    'https://shinden.pl/series', mode='Shinden',
                    fanart=default_background, thumb=iconShinden, isFolder=True)
###AnimeZone.pl###
    if setting('AnimeZone') == 'true':
        addon.addDir('[COLOR=%s]Animezone.pl[/COLOR]' % 'blue', 
                   'https://www.animezone.pl/', mode='AnimeZone',
                    fanart=default_background, thumb=iconAnimezone, isFolder=True)
###StrefaDB.pl###
    if setting('Dragonball') == 'true':
        addon.addDir('[COLOR=%s]StrefaDB.pl[/COLOR]' % 'blue', 
                     'https://strefadb.pl/', mode='Dragonball',
                     fanart=default_background, thumb=iconstrefadb, isFolder=True)
###AnimeOn.pl###
    if setting('AnimeOn') == 'true':
        addon.addDir('[COLOR=%s]Animeon.pl[/COLOR]' % 'blue', 
                     'https://animeon.pl/', mode='Animeon',
                     fanart=default_background, thumb=iconstrefadb, isFolder=True)
###Kreskoweczki.pl###
    if setting('Kreskoweczki') == 'true':
        addon.addDir('[COLOR=%s]Kreskóweczki[/COLOR]' % 'blue', 
                     'http://www.kreskoweczki.pl', mode='Animeon',
                     fanart=default_background, thumb=iconkresk, isFolder=True)
###Ustawienia###
    addon.addDir('Ustawienia', '', 'Settings',fanart=default_background, isFolder=True)

###############################################################################
###############################################################################
# Wbijam.pl
###############################################################################
###############################################################################

def Wbijam(mode, url):
    from hosts import hostwbijam
    if mode == "Pagewbijam":
        url = params['url']
        hostwbijam.Pagewbijam(url)
        addon.endOfDir()
    elif mode == "Browse_Titles":
        hostwbijam.Browse_Titles()
        addon.endOfDir()
    elif mode == "Browse_Seasons":
        hostwbijam.Browse_Seasons()
        addon.endOfDir()
    elif mode == "List_Episodes":
        hostwbijam.List_Episodes()
        addon.endOfDir()
    elif mode == "List_Links":
        hostwbijam.List_Links()
    else:
        return


###############################################################################
###############################################################################
# Anime Odcinki
###############################################################################
###############################################################################
def AnimeOdcinki(mode, url):
    from hosts import hostanimeodcinki
    if mode == "AnimeOdcinki":
        url = params['url']
        hostanimeodcinki.PageAnimeOdcinki(url)
        addon.endOfDir()
    elif mode == "AOAlfabetycznie":
        url = params['url']
        hostanimeodcinki.Alfabetyczna(url)
        addon.endOfDir()
    elif mode == "AOListTitles":
        hostanimeodcinki.ListTitles()
        addon.endOfDir()
    elif mode == "AOSearch":
        hostanimeodcinki.Search()
        addon.endOfDir()
    elif mode == "AOGatunki":
        hostanimeodcinki.Gatunki()    
        addon.endOfDir()
    elif mode == "AOListEpisodes":
        hostanimeodcinki.ListEpisodes()
        addon.endOfDir()
    elif mode == "AOListLinks":
        hostanimeodcinki.ListLinks()
    else:    
        return


###############################################################################
###############################################################################
# Anime Shinden
###############################################################################
###############################################################################

def AnimeShinden(mode, url):
    from hosts import hostanimeshinden
    if mode == "Shinden":
        
        hostanimeshinden.PageAnimeShinden()
        addon.endOfDir()
    elif mode == "SHAlfabetycznie":
        hostanimeshinden.Alfabetyczna()
        addon.endOfDir()
    elif mode == "SHListTitles":
        hostanimeshinden.ListTitles()
        addon.endOfDir()
    elif mode == "SHSearch":
        hostanimeshinden.Search()
        addon.endOfDir()
    elif mode == "SHGatunki":
        hostanimeshinden.Gatunki()    
        addon.endOfDir()
    elif mode == "SHListEpisodes":
        hostanimeshinden.ListEpisodes()
        addon.endOfDir()
    elif mode == "SHListLinks":
        hostanimeshinden.ListLinks()
    elif mode == "SHLogowanie":
        hostanimeshinden.Logowanie()
    else:    
        return


############################################################################################################
#=########################################################################################################=#
#                                               GET PARAMS                                                 #
#=########################################################################################################=#

params = addon.get_params()
url = params.get('url')
name = params.get('name')
img = params.get('img')
section = params.get('section')
#iconimage = params.get('iconimage')

try:
    mode = params['mode']
except:
    mode = None





###############################################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#

def mode_check(mode='', url=''):
    if (mode == 'SectionMenu'):
        MainMenu()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif (mode == '') or (mode == None) or (mode == 'MainMenu'):
        MainMenu()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == 'Settings':
        my_addon.openSettings()
        xbmc.executebuiltin('XBMC.Container.Refresh()')
#    elif (mode == 'SubMenu'):
#        SubMenu()
#    elif (mode == 'SubSubMenu'):
#        SubSubMenu()

# WBIJAM.PL
    elif (mode == 'Pagewbijam'):
        Wbijam(mode=mode, url=url)
    elif (mode == 'Browse_Titles'):
        Wbijam(mode, url)
    elif (mode == 'Browse_Seasons'):
        Wbijam(mode, url)
    elif (mode == 'List_Episodes'):
        Wbijam(mode, url)
    elif (mode == 'List_Links'):
        Wbijam(mode, url)



# ANIME-ODCINKI
    elif (mode == 'AnimeOdcinki'):
        AnimeOdcinki(mode=mode, url=url)
    elif (mode == 'AOAlfabetycznie'):
        AnimeOdcinki(mode, url)
    elif (mode == 'AOListTitles'):
        AnimeOdcinki(mode, url)  
    elif (mode == 'AOSearch'):        
        AnimeOdcinki(mode, url)
    elif (mode == 'AOGatunki'):        
        AnimeOdcinki(mode, url)           
    elif (mode == 'AOListEpisodes'):        
        AnimeOdcinki(mode, url)    
    elif (mode == 'AOListLinks'):        
        AnimeOdcinki(mode, url)   

# ANIME-SHINDEN
        
    elif (mode == 'Shinden'):
        AnimeShinden(mode=mode, url=url)
    elif (mode == 'SHAlfabetycznie'):
        AnimeShinden(mode, url)
    elif (mode == 'SHListTitles'):
        AnimeShinden(mode, url)  
    elif (mode == 'SHSearch'):        
        AnimeShinden(mode, url)
    elif (mode == 'SHGatunki'):        
        AnimeShinden(mode, url)           
    elif (mode == 'SHListEpisodes'):        
        AnimeShinden(mode, url)    
    elif (mode == 'SHListLinks'):        
        AnimeShinden(mode, url)   
    elif (mode == 'SHLogowanie'):        
        AnimeShinden(mode, url)  

mode_check(mode, url)