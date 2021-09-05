'''
    Simple XBMC Download Script
    Copyright (C) 2013 Sean Poyser (seanpoyser@gmail.com)

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

import json
import os
import re
import threading
from sqlite3 import dbapi2 as database
from urllib.parse import parse_qsl, urlparse, unquote

import pyxbmct
import requests
import xbmc
import xbmcgui
from ptw.libraries import control, cleantitle


def download(name, image, url):
    name = unquote(name)
    if url == None:
        return

    try:
        headers = dict(parse_qsl(url.rsplit('|', 1)[1]))
    except:
        headers = dict('')

    url = url.split('|')[0]

    content = re.compile('(.+?)\sS(\d*)E\d*$').findall(name)
    transname = re.sub(r'/|:|\*|\?|\"|<|>|\+|,|\.|', '', cleantitle.normalize(name))
    levels = ['../../../..', '../../..', '../..', '..']

    if len(content) == 0:
        dest = control.setting('movie.download.path')
        dest = control.transPath(dest)
        for level in levels:
            try:
                control.makeFile(os.path.abspath(os.path.join(dest, level)))
            except:
                pass
        control.makeFile(dest)
        dest = os.path.join(dest, transname)
        control.makeFile(dest)
    else:
        dest = control.setting('tv.download.path')
        dest = control.transPath(dest)
        for level in levels:
            try:
                control.makeFile(os.path.abspath(os.path.join(dest, level)))
            except:
                pass
        control.makeFile(dest)
        transtvshowtitle = re.sub(r'/|:|\*|\?|\"|<|>|', '',
                                  cleantitle.normalize(content[0][0].encode().decode('utf-8')))
        dest = os.path.join(dest, transtvshowtitle)
        control.makeFile(dest)
        dest = os.path.join(dest, 'Season %01d' % int(content[0][1]))
        control.makeFile(dest)

    ext = os.path.splitext(urlparse(url).path)[1][1:]
    if not ext in ['mp4', 'mkv', 'flv', 'avi', 'mpg']:
        ext = 'mp4'
    dest = os.path.join(dest, transname + '.' + ext)
    doDownload(url, dest, name, image, json.dumps(headers))


def getResponse(url, headers, size):
    try:
        if size > 0:
            size = int(size)
            headers['Range'] = 'bytes=%d-' % size

        return requests.get(url, verify=False, headers=headers, stream=True)
    except:
        return None


def done(title, dest, downloaded):
    playing = xbmc.Player().isPlaying()

    text = xbmcgui.Window(10000).getProperty('GEN-DOWNLOADED')

    if len(text) > 0:
        text += '[CR]'

    if downloaded:
        text += '%s : %s' % (dest.rsplit(os.sep)[-1], '[COLOR forestgreen]Download succeeded[/COLOR]')
    else:
        text += '%s : %s' % (dest.rsplit(os.sep)[-1], '[COLOR red]Download failed[/COLOR]')

    xbmcgui.Window(10000).setProperty('GEN-DOWNLOADED', text)

    if not playing:
        xbmcgui.Dialog().ok(title, text)
        xbmcgui.Window(10000).clearProperty('GEN-DOWNLOADED')


def doDownload(url, dest, title, image, headers):
    prepareDatabase()
    try:
        headers = json.loads(headers)

        file = dest.rsplit(os.sep, 1)[-1]

        resp = getResponse(url, headers, 0)

        if not resp:
            xbmcgui.Dialog().ok(title, dest + '\nDownload failed' + '\nNo response from server')
            return

        try:
            content = int(resp.headers['Content-Length'])
        except:
            content = 0

        try:
            resumable = 'bytes' in resp.headers['Accept-Ranges'].lower()
        except:
            resumable = False

        # print "Download Header"
        # print resp.headers
        if resumable:
            print("Download is resumable")

        if content < 1:
            xbmcgui.Dialog().ok(title, file + "\n" + 'Unknown filesize' + "\n" + 'Unable to download')
            return

        size = 1024 * 1024
        mb = content / (1024 * 1024)

        if content < size:
            size = content

        total = 0
        notify = 0
        errors = 0
        count = 0
        resume = 0
        sleep = 0
        manager = 0

        if not xbmcgui.Dialog().yesno(title + ' - Confirm Download', file + "\n" + 'Complete file is %dMB' % mb +
                                  '\nContinue with download?', yeslabel='Confirm', nolabel='Cancel') == 1:
            return

        print('Download File Size : %dMB %s ' % (mb, dest))

        f = open(dest, mode='wb')

        chunks = []
        control.idle()
        insertIntoDb(title, "0%", '%dMB' % mb, "0")
        for chunk in resp.iter_content(chunk_size=1024):
            downloaded = total
            for c in chunks:
                downloaded += len(c)
            percent = min(100 * downloaded / content, 100)
            if percent >= manager:
                update(title, str(int(percent)) + '%', "%.2f" % (downloaded / 1048576) + " MB", '%dMB' % mb)
                manager += 0.1
            if percent >= notify:
                xbmc.executebuiltin("XBMC.Notification(%s,%s,%i,%s)" % (
                    title + ' - Download Progress - ' + str(int(percent)) + '%', dest, 10000, image))

                print('Download percent : %s %s %dMB downloaded : %sMB File Size : %sMB' % (
                    str(int(percent)) + '%', dest, mb, downloaded / 1048576, content / (1024 * 1024)))

                notify += 10

            error = False

            try:
                if not chunk:
                    if percent < 99:
                        error = True
                    else:
                        while len(chunks) > 0:
                            c = chunks.pop(0)
                            f.write(c)
                            del c

                        f.close()
                        update(title, '100%', "%.2f" % (content / 1048576) + " MB", '%dMB' % mb)
                        print('%s download complete' % (dest))
                        return done(title, dest, True)

            except Exception as e:
                print(str(e))
                error = True
                sleep = 10
                errno = 0

                if hasattr(e, 'errno'):
                    errno = e.errno

                if errno == 10035:  # 'A non-blocking socket operation could not be completed immediately'
                    pass

                if errno == 10054:  # 'An existing connection was forcibly closed by the remote host'
                    errors = 10  # force resume
                    sleep = 30

                if errno == 11001:  # 'getaddrinfo failed'
                    errors = 10  # force resume
                    sleep = 30

            if chunk:
                errors = 0
                chunks.append(chunk)
                if len(chunks) > 5:
                    c = chunks.pop(0)
                    f.write(c)
                    total += len(c)
                    del c

            if error:
                errors += 1
                count += 1
                print('%d Error(s) whilst downloading %s' % (count, dest))
                xbmc.sleep(sleep * 1000)

            if (resumable and errors > 0) or errors >= 10:
                if (not resumable and resume >= 50) or resume >= 500:
                    # Give up!
                    print('%s download canceled - too many error whilst downloading' % dest)
                    return done(title, dest, False)

                resume += 1
                errors = 0
                if resumable:
                    chunks = []
                    # create new response
                    print('Download resumed (%d) %s' % (resume, dest))
                    resp = getResponse(url, headers, total)
                else:
                    # use existing response
                    pass
        update(title, '100%', "%.2f" % (content / 1048576) + " MB", '%dMB' % mb)
    except Exception as e:
        pass


def downloadManager():
    window = MyAddon('Download Manager')
    window.doModal()
    window.cancelThread = True
    del window


def prepareDatabase():
    control.makeFile(control.dataPath)
    dbcon = database.connect(control.downloadsFile, detect_types=database.PARSE_DECLTYPES, cached_statements=20000)
    dbcur = dbcon.cursor()
    dbcur.execute(
        "CREATE TABLE IF NOT EXISTS download_manager (""filename TEXT, ""percentage TEXT, ""filesize TEXT, ""downloaded TEXT);")


def insertIntoDb(fileName, percentage, fileSize, downloaded):
    dbcon = database.connect(control.downloadsFile)
    dbcur = dbcon.cursor()
    dbcur.execute("INSERT INTO download_manager Values (?, ?, ?, ?)", (fileName, percentage, fileSize, downloaded))
    dbcon.commit()


def update(fileName, percentage, downloaded, filesize):
    dbcon = database.connect(control.downloadsFile)
    dbcur = dbcon.cursor()
    dbcur.execute("UPDATE download_manager SET percentage=?, downloaded=? WHERE filename=? AND filesize=?",
                  (percentage, downloaded, fileName, filesize))
    dbcon.commit()


import time


class MyAddon(pyxbmct.AddonDialogWindow):
    def __init__(self, title=''):
        super(MyAddon, self).__init__(title)
        self.setGeometry(900, 450, 8, 8)
        self.set_active_controls()
        # Connect a key action (Backspace) to close the window.
        self.setFocus(self.button)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.abort = False
        self.cancelThread = False

    def set_active_controls(self):
        int_label = pyxbmct.Label('Lista Pobierania', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 0, 0, 1, 8)
        int_label = pyxbmct.Label('Nazwa Pliku', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 1, 0, 1, 2)
        int_label = pyxbmct.Label('Procent Pobrania', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 1, 2, 1, 2)
        int_label = pyxbmct.Label('Ukończone', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 1, 4, 1, 2)
        int_label = pyxbmct.Label('Wielkość Pliku', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 1, 6, 1, 2)

        self.button = pyxbmct.Button('Pobierz listę')
        self.placeControl(self.button, 7, 3, 1, 2)

        self.items_fileName = [pyxbmct.FadeLabel() for x in range(0, 4)]
        self.items_percent = [pyxbmct.Label("", alignment=pyxbmct.ALIGN_CENTER) for x in range(0, 4)]
        self.items_completed = [pyxbmct.Label("", alignment=pyxbmct.ALIGN_CENTER) for x in range(0, 4)]
        self.items_fileSize = [pyxbmct.Label("", alignment=pyxbmct.ALIGN_CENTER) for x in range(0, 4)]

        for counter, items in enumerate(
                (self.items_fileName, self.items_percent, self.items_completed, self.items_fileSize)):
            self.placeControl(items[0], 2, 0 + (counter * 2), 1, 2)
            self.placeControl(items[1], 3, 0 + (counter * 2), 1, 2)
            self.placeControl(items[2], 4, 0 + (counter * 2), 1, 2)
            self.placeControl(items[3], 5, 0 + (counter * 2), 1, 2)

        self.connectEventList([xbmcgui.ACTION_SELECT_ITEM, xbmcgui.ACTION_MOUSE_LEFT_CLICK], self.list_update)

    def worker(self):
        dbcon = database.connect(control.downloadsFile)
        dbcur = dbcon.cursor()
        one_update = False
        while not self.cancelThread:
            try:
                time.sleep(0.3)
                dbcur.execute("SELECT * FROM download_manager")
                match = dbcur.fetchall()
                for i, item in enumerate(match[:4]):
                    if type(item[0]) == str or not one_update:
                        self.items_fileName[i].addLabel(item[0])
                    if type(item[1]) == str:
                        self.items_percent[i].setLabel(item[1])
                    if type(item[3]) == str:
                        self.items_completed[i].setLabel(item[3])
                    if type(item[2]) == str or not one_update:
                        self.items_fileSize[i].setLabel(item[2])
                one_update = True
            except:
                pass

    def list_update(self):
        if not self.abort:
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.abort = False

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                               ('WindowClose', 'effect=fade start=100 end=0 time=500',)])


def clear_db():
    try:
        dbcon = database.connect(control.downloadsFile)
        dbcur = dbcon.cursor()
        dbcur.execute("DROP TABLE IF EXISTS download_manager")
        dbcur.execute("VACUUM")
        dbcur.commit()
    except:
        pass
