# -*- coding: UTF-8 -*-
#####Python 3.0 #######


import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.libs import addon_tools as addon

my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')

setting = my_addon.getSetting
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmc.translatePath('special://home/addons/' + my_addon_id + '/resources/media/')
default_background = MEDIA + "fanart.jpg"

iconSite = PATH + 'icon.png'
iconWbijam = MEDIA + 'wbijam.jpg'
iconOdcinki = MEDIA + 'animeodcinki.jpg'
iconShinden = MEDIA + 'animeshinden.jpg'
iconAnimezone = MEDIA + 'animezone.jpg'
iconstrefadb = MEDIA + 'strefadb.jpg'
iconsettings = MEDIA + 'settings.png'

Odcinkifanart = MEDIA + 'aodcfanart.jpg'
DBfanart = MEDIA + 'dbfanart.jpg'

base_link = ''

global cookie


def MainMenu():
###Wbijam.pl###

    
    addon.addDir('[COLOR=%s]Wbijam.pl[/COLOR]' % 'blue', 
                 'https://inne.wbijam.pl/', mode='Pagewbijam',
                 fanart=default_background, thumb=iconWbijam, isFolder=True)
###Anime Odcinki###
    
    addon.addDir('[COLOR=%s]Anime Odcinki[/COLOR]' % 'blue', 
                 'https://anime-odcinki.pl/', mode='AnimeOdcinki',
                 fanart=Odcinkifanart, thumb=iconOdcinki, isFolder=True)
###Shinden.pl###
    
    addon.addDir('[COLOR=%s]Shinden.pl[/COLOR]' % 'blue', 
                 'https://shinden.pl/series', mode='Shinden',
                 fanart=default_background, thumb=iconShinden, isFolder=True)
###StrefaDB.pl###
    addon.addDir('[COLOR=%s]StrefaDB.pl[/COLOR]' % 'blue', 
                 'https://strefadb.pl/', mode='Dragonball',
                 fanart=DBfanart, thumb=iconstrefadb, isFolder=True)                    
###Ustawienia###
    addon.addDir('Ustawienia', '', 'Settings',
                 fanart=default_background, thumb=iconsettings, isFolder=True)

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
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "Browse_Titles":
        hostwbijam.Browse_Titles()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "Browse_Seasons":
        hostwbijam.Browse_Seasons()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "List_Episodes":
        hostwbijam.List_Episodes()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
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
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "AOAlfabetycznie":
        url = params['url']
        hostanimeodcinki.Alfabetyczna(url)
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "AOListTitles":
        hostanimeodcinki.ListTitles()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "AOSearch":
        hostanimeodcinki.Search()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "AOGatunki":
        hostanimeodcinki.Gatunki()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')        
        addon.endOfDir()
    elif mode == "AOListEpisodes":
        hostanimeodcinki.ListEpisodes()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
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
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "SHAlfabetycznie":
        hostanimeshinden.Alfabetyczna()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "SHListTitles":
        hostanimeshinden.ListTitles()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "SHSearch":
        hostanimeshinden.Search()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "SHGatunki":
        hostanimeshinden.Gatunki()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')        
        addon.endOfDir()
    elif mode == "SHListEpisodes":
        hostanimeshinden.ListEpisodes()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    elif mode == "SHListLinks":
        hostanimeshinden.ListLinks()
    elif mode == "SHLogowanie":
        hostanimeshinden.Logowanie()
    else:    
        return

def DragonBall(mode, url):
    from hosts import hostdragon
    if mode == "Dragonball":
        hostdragon.Pagedragon()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir()
    if mode == "DBListTitles":
        hostdragon.ListTitles()
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        addon.endOfDir() 
    if mode == "DBListLinks":
        hostdragon.ListLinks()
            
    else:
        return

def PathCheck():
    if setting('download.path') == '':
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Błąd Ustawień - Download', 
                           'Włączone pobieranie, ale nie ustawiono ścieżki pobierania \nWprowadź scieżkę pobierania w ustawieniach' ,
                           'Wyjdź', 'Ustawienia')
        if ret:
            my_addon.openSettings()
            xbmc.executebuiltin('Container.Refresh')
        else:
            exit()
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


try:
    mode = params['mode']
except:
    mode = None

###############################################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#

def mode_check(mode='', url=''):

    if setting('download.opt') == 'true':
        PathCheck()
        
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

# STREFA-DB
    elif (mode == 'Dragonball'):
        DragonBall(mode=mode, url=url)
    elif (mode == 'DBListTitles'):
        DragonBall(mode=mode, url=url)
    elif (mode == 'DBListLinks'):
        DragonBall(mode=mode, url=url)
        
        
# OTHER
    elif (mode == 'delete_table'):
        from resources.libs.scraper import delete_table
        delete_table()
mode_check(mode, url)
    
        