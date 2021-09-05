# -*- coding: UTF-8 -*-
import sys

import os
import re
import requests
import shutil
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import zipfile


class ResolveUrlChecker:
    def __init__(self):
        self.addonName = "script.module.resolveurl"
        self.resolveUrlLink = "https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml"
        self.resolveUrlLinkZip = f"https://raw.githubusercontent.com/Gujal00/smrzips/master/zips/{self.addonName}/{self.addonName}-{self.getOfficialResolveUrlVersion()}.zip"
        self.OfficialVersion = self.getOfficialResolveUrlVersion()
        self.LocalVersion = self.getInstalledResolveUrlVersion()

    def getOfficialResolveUrlVersion(self):
        try:
            content = requests.get(self.resolveUrlLink, verify=False, timeout=10).text
            resolveUrlVersion = re.findall(r"ResolveURL\" version=\"(.*?)\"", content)[0]
            return resolveUrlVersion
        except Exception as e:
            xbmc.log("[SCRIPT.MODULE.PTW] Can't get resolveUrl version from official repo", xbmc.LOGERROR)
            xbmc.log(f"[SCRIPT.MODULE.PTW] {e}")
            sys.exit()

    def getInstalledResolveUrlVersion(self):
        try:
            self.setResolveUrl(enabled=True)
            resolveUrlAddon = xbmcaddon.Addon(self.addonName)
            resolveUrlAddonVersion = resolveUrlAddon.getAddonInfo('version')
            return resolveUrlAddonVersion
        except Exception as e:
            xbmc.log("[SCRIPT.MODULE.PTW] Can't get resolveUrl version from kodi installation", xbmc.LOGERROR)
            xbmc.log(f"[SCRIPT.MODULE.PTW] {e}", xbmc.LOGERROR)
            return "0.0.0"

    def checkVersion(self):
        if self.LocalVersion != self.OfficialVersion:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('Niekompatybilna wersja zależności',
                               'Chcesz zaktulizować zależność resolveurl do najnowszej wersji? Będzie to wymagać ponownego uruchomienia Kodi')
            if ret:
                self.removeResolveUrl()
                self.installResolveUrl()
            else:
                sys.exit()
        else:
            sys.exit()

    def installResolveUrl(self):
        unzipPath = xbmcvfs.translatePath('special://home/addons/')
        zipPath = self.download_file(self.resolveUrlLinkZip)
        self.unzip_addon(zipPath, unzipPath)
        self.closeKodi()

    def removeResolveUrl(self):
        addonPath = xbmcvfs.translatePath('special://home/addons/script.module.resolveurl')
        if os.path.isdir(addonPath):
            self.setResolveUrl(enabled=False)
            shutil.rmtree(addonPath, ignore_errors=True)

    def removeZipFile(self):
        zipFilePath = xbmcvfs.translatePath(f'special://home/addons/script.module.resolveurl-{self.OfficialVersion}.zip')
        os.remove(zipFilePath)

    def download_file(self, url):
        try:
            localFileName = url.split('/')[-1]
            addonsDirectory = xbmcvfs.translatePath('special://home/addons/')
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(os.path.join(addonsDirectory, localFileName), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return os.path.join(addonsDirectory, localFileName)
        except Exception as e:
            xbmc.log("[SCRIPT.MODULE.PTW] Downloading addon fails", xbmc.LOGERROR)
            xbmc.log(f"[SCRIPT.MODULE.PTW] {e}", xbmc.LOGERROR)
            sys.exit()

    def unzip_addon(self, path_to_zip_file, directory_to_extract_to):
        try:
            if not os.path.exists(directory_to_extract_to):
                os.makedirs(directory_to_extract_to)
            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                zip_ref.extractall(directory_to_extract_to)
            self.removeZipFile()
        except Exception as e:
            xbmc.log("[SCRIPT.MODULE.PTW] Unpacking addon fails", xbmc.LOGERROR)
            xbmc.log(f"[SCRIPT.MODULE.PTW] {e}", xbmc.LOGERROR)
            sys.exit()

    def closeKodi(self):
        choice = xbmcgui.Dialog().ok('Zamknięcie', 'Teraz Kodi zostanie zamknięte aby zatwierdzić zmiany')
        if choice == 1:
            os._exit(1)
        else:
            xbmc.executebuiltin("Action(Close)")

    def setResolveUrl(self, enabled=True):
        if enabled:
            xbmc.executeJSONRPC(
                f'{{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":7,"params":{{"addonid": "{self.addonName}","enabled":true}}}}')
        else:
            xbmc.executeJSONRPC(
                f'{{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":7,"params":{{"addonid": "{self.addonName}","enabled":false}}}}')


ResolveUrlChecker().checkVersion()

