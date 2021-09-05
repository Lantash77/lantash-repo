# -*- coding: utf-8 -*-

"""
    FanFilm Add-on

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
"""
import threading
import re

from ptw.libraries import control
from ptw.libraries import log_utils
from ptw.libraries import cache

control.execute('RunPlugin(plugin://%s)' % control.get_plugin_url({
    'action': 'service'}))


def settingsFileRewrite():
    addon_version = control.addon('plugin.video.fanfilm').getAddonInfo('version')
    settings_addon_version = control.setting("addon.version")
    reset_keys = control.setting("reset.keys")

    if reset_keys == 'true' and addon_version != settings_addon_version:
        with open(control.settingsFile, 'r') as file:
            content = file.read()
        pattern = re.compile(r"(.*TVDb.*|.*fanart.*|.*tm.*)", re.MULTILINE)
        settings = re.findall(pattern, content)
        for setting in settings:
            content = content.replace(setting, "")
        with open(control.settingsFile, 'w') as file:
            file.write(content)


def syncTraktLibrary():
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.fanfilm/?action=tvshowsToLibrarySilent&url=traktcollection')
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.fanfilm/?action=moviesToLibrarySilent&url=traktcollection')


try:
    settingsFileRewrite()
    MediaVersion = control.addon('script.fanfilm.media').getAddonInfo('version')
    AddonVersion = control.addon('plugin.video.fanfilm').getAddonInfo('version')
    control.setSetting("addon.version", AddonVersion)

    log_utils.log('######################### FANFILM ############################', log_utils.LOGINFO)
    log_utils.log('####### CURRENT FANFILM VERSIONS REPORT ######################', log_utils.LOGINFO)
    log_utils.log('### FANFILM PLUGIN VERSION: %s ###' % str(AddonVersion), log_utils.LOGINFO)
    log_utils.log('### FANFILM MEDIA VERSION: %s ###' % str(MediaVersion), log_utils.LOGINFO)
    log_utils.log('###############################################################', log_utils.LOGINFO)
except:
    log_utils.log('######################### FANFILM ############################', log_utils.LOGINFO)
    log_utils.log('####### CURRENT FANFILM VERSIONS REPORT ######################', log_utils.LOGINFO)
    log_utils.log(
        '### ERROR GETTING FANFILM VERSIONS - NO HELP WILL BE GIVEN AS THIS IS NOT AN OFFICIAL FANFILM INSTALL. ###',
        log_utils.LOGINFO)
    log_utils.log('###############################################################', log_utils.LOGINFO)

if control.setting('autoTraktOnStart') == 'true':
    syncTraktLibrary()

if int(control.setting('schedTraktTime')) > 0:
    log_utils.log('###############################################################', log_utils.LOGINFO)
    log_utils.log('#################### STARTING TRAKT SCHEDULING ################', log_utils.LOGINFO)
    log_utils.log(
        '#################### SCHEDULED TIME FRAME ' + control.setting('schedTraktTime') + ' HOURS ################',
        log_utils.LOGINFO)
    timeout = 3600 * int(control.setting('schedTraktTime'))
    schedTrakt = threading.Timer(timeout, syncTraktLibrary)
    schedTrakt.start()

if control.setting('autoCleanCache') == 'true':
    cache.cache_clear_all()
    log_utils.log('######################### FANFILM ############################', log_utils.LOGINFO)
    log_utils.log('######## Wyczyszczono pamięć podręczną #######################', log_utils.LOGINFO)
    log_utils.log('###############################################################', log_utils.LOGINFO)

if int(control.setting('schedCleanCache')) > 0:
    log_utils.log('###############################################################', log_utils.LOGINFO)
    log_utils.log('#################### STARTING CLEAN SCHEDULING ################', log_utils.LOGINFO)
    log_utils.log(
        '#################### SCHEDULED TIME FRAME ' + control.setting('schedCleanCache') + ' HOURS ################',
        log_utils.LOGINFO)
    timeout = 3600 * int(control.setting('schedCleanCache'))
    schedClean = threading.Timer(timeout, cache.cache_clear_all())
    schedClean.start()

try:
    from ptw.libraries import downloader

    downloader.clear_db()
except:
    pass


