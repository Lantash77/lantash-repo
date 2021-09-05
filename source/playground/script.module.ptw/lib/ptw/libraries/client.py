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

import base64
import gzip
import random
import re

try:
    import urllib.parse as urllib
except:
    pass

from io import StringIO
from future.moves.http import cookiejar
import requests
from future.moves.urllib.parse import urlparse
from html import unescape

import xbmc
from ptw.debug import log_exception
from ptw.libraries import cfscrape
from ptw.libraries import dom_parser
from ptw.libraries import log_utils

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def request(url, close=True, redirect=True, error=False, proxy=None, post=None, headers=None, mobile=False, XHR=False,
            limit=None, referer=None, cookie=None, compression=True, output='',
            timeout='30'):
    try:
        if not url:
            return

        proxies = {}
        if not proxy == None:
            proxies = {
                "http": proxy,
                "https": proxy}

        if output == 'cookie' or output == 'extended' or not close == True:
            cookies = cookiejar.LWPCookieJar()

        if url.startswith('//'):
            url = 'http:' + url

        _headers = {}
        if headers:
            try:
                _headers.update(headers)
            except:
                log_exception()
        if 'User-Agent' in _headers:
            pass
        elif not mobile == True:
            # headers['User-Agent'] = agent()
            _headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0"
        else:
            _headers['User-Agent'] = 'Apple-iPhone/701.341'
        if 'Referer' in _headers:
            pass
        elif referer is not None:
            _headers['Referer'] = referer
        if not 'Accept-Language' in _headers:
            _headers['Accept-Language'] = 'en-US'
        if 'X-Requested-With' in _headers:
            pass
        elif XHR == True:
            _headers['X-Requested-With'] = 'XMLHttpRequest'
        if 'Cookie' in _headers:
            pass
        elif not cookie == None:
            _headers['Cookie'] = cookie
        if 'Accept-Encoding' in _headers:
            pass
        elif compression and limit is None:
            _headers['Accept-Encoding'] = 'gzip'

        try:

            if redirect == False and not output == 'chunk':
                if post:
                    response = requests.post(url, headers=_headers, verify=False, data=post, proxies=proxies,
                                             timeout=int(timeout), allow_redirects=False)
                else:
                    response = requests.get(url, headers=_headers, verify=False, proxies=proxies, timeout=int(timeout),
                                            allow_redirects=False)
            elif redirect and not output == 'chunk':
                if post:
                    response = requests.post(url, headers=_headers, data=post, verify=False, proxies=proxies,
                                             timeout=int(timeout))
                else:
                    response = requests.get(url, headers=_headers, verify=False, proxies=proxies, timeout=int(timeout))

            cookies = response.cookies

            if response.status_code == 503 or ('shinden' in url and response.status_code == 403):
                s = requests.Session()
                headersok = {
                    'User-Agent': _headers['User-Agent']}
                s.headers = headersok
                scraper = cfscrape.create_scraper(s)
                if output == 'session':
                    return s
                if output == 'cookie':
                    return scraper.get_cookie_string(url, user_agent=_headers['User-Agent'])[0]
                else:
                    return scraper.get(url).content
        except Exception as e:
            pass

        if output == 'cookie':
            result = ''
            try:
                result = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
            except:
                pass
            if close == True:
                response.close()
            return result

        elif output == 'geturl':
            result = response.url
            if close == True:
                response.close()
            return result

        elif output == 'headers':
            result = response.headers
            if close == True:
                response.close()
            return result

        elif output == 'chunk':
            with requests.get(url, stream=True, headers=_headers, verify=False) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        return chunk
                    else:
                        return None

        elif output == 'file_size':
            try:
                content = int(response.headers['Content-Length'])
            except:
                content = '0'
            response.close()
            return content

        if limit == '0':
            result = response.read(224 * 1024)
        elif not limit == None:
            result = response.read(int(limit) * 1024)
        else:
            result = response.text

        try:
            encoding = dict(response.headers)['Content-Encoding']
        except:
            encoding = None
        # if encoding == 'gzip':
        #     result = gzip.GzipFile(fileobj=StringIO(result)).read()

        if output == 'extended':
            try:
                response_headers = dict([(item[0].title(), item[1]) for item in response.headers().items()])
            except:
                response_headers = response.headers
            response_code = str(response.status_code)
            try:
                cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
            except:
                pass
            if close == True:
                response.close()
            return (result, response_code, response_headers, _headers, cookie)
        else:
            if close == True:
                response.close()
            return result
    except Exception as e:
        log_utils.log('Request-Error: (%s) => %s' % (str(e), url), log_utils.LOGDEBUG)


def _basic_request(url, headers=None, post=None, timeout='30', limit=None):
    try:
        request = urllib2.Request(url, data=post)
        _add_request_header(request, headers or {})
        response = urllib2.urlopen(request, timeout=int(timeout))
        return _get_result(response, limit)
    except:
        log_exception()


def _add_request_header(_request, headers):
    try:
        if not headers:
            headers = {}

        try:
            scheme = _request.get_type()
        except:
            scheme = 'http'

        referer = headers.get('Referer') if 'Referer' in headers else '%s://%s' % (scheme, _request.get_host())

        _request.add_unredirected_header('Host', _request.get_host())
        _request.add_unredirected_header('Referer', referer)
        for key in headers:
            _request.add_header(key, headers[key])
    except:
        log_exception()


def _get_result(response, limit=None):
    if limit == '0':
        result = response.read(224 * 1024)
    elif limit:
        result = response.read(int(limit) * 1024)
    else:
        result = response.read(5242880)

    try:
        encoding = response.info().getheader('Content-Encoding')
    except:
        encoding = None
    if encoding == 'gzip':
        result = gzip.GzipFile(fileobj=StringIO(result)).read()

    return result


def parseDOM(html, name='', attrs=None, ret=False):
    if attrs:
        attrs = dict((key, re.compile(value + ('$' if value else ''))) for key, value in attrs.items())
    results = dom_parser.parse_dom(html, name, attrs, ret)
    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]
    return results


def replaceHTMLCodes(txt):
    if type(txt) == bytes:
        txt = txt.decode('utf-8')
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = txt.strip()
    return txt


def randomagent():
    BR_VERS = [['%s.0' % i for i in range(18, 50)],
               ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111',
                '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
                '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124',
                '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71', '46.0.2490.80',
                '46.0.2490.86', '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112',
                '50.0.2661.86', '51.0.2704.103', '52.0.2743.116', '53.0.2785.143', '54.0.2840.71', '61.0.3163.100'],
               ['11.0'], ['8.0', '9.0', '10.0', '10.6']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1',
                'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
                'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES),
                                  br_ver=random.choice(BR_VERS[index]))


def agent():
    return 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'


class bfcookie:

    def __init__(self):
        self.COOKIE_NAME = 'BLAZINGFAST-WEB-PROTECT'

    def get(self, netloc, ua, timeout):
        try:
            headers = {
                'User-Agent': ua,
                'Referer': netloc}
            result = _basic_request(netloc, headers=headers, timeout=timeout)

            match = re.findall('xhr\.open\("GET","([^,]+),', result)
            if not match:
                return False

            url_Parts = match[0].split('"')
            url_Parts[1] = '1680'
            url = urlparse.urljoin(netloc, ''.join(url_Parts))

            match = re.findall('rid=([0-9a-zA-Z]+)', url_Parts[0])
            if not match:
                return False

            headers['Cookie'] = 'rcksid=%s' % match[0]
            result = _basic_request(url, headers=headers, timeout=timeout)
            return self.getCookieString(result, headers['Cookie'])
        except:
            log_exception()

    # not very robust but lazieness...
    def getCookieString(self, content, rcksid):
        vars = re.findall('toNumbers\("([^"]+)"', content)
        value = self._decrypt(vars[2], vars[0], vars[1])
        cookie = "%s=%s;%s" % (self.COOKIE_NAME, value, rcksid)
        return cookie

    def _decrypt(self, msg, key, iv):
        from binascii import unhexlify, hexlify
        import pyaes
        msg = unhexlify(msg)
        key = unhexlify(key)
        iv = unhexlify(iv)
        if len(iv) != 16:
            return False
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
        plain_text = decrypter.feed(msg)
        plain_text += decrypter.feed()
        f = hexlify(plain_text)
        return f


class sucuri:
    def __init__(self):
        self.cookie = None

    def get(self, result):
        try:
            s = re.compile("S\s*=\s*'([^']+)").findall(result)[0]
            s = base64.b64decode(s)
            s = s.replace(' ', '')
            s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
            s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
            s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
            s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
            s = re.sub(';location.reload\(\);', '', s)
            s = re.sub(r'\n', '', s)
            s = re.sub(r'document\.cookie', 'cookie', s)

            cookie = ''
            exec(s)
            self.cookie = re.compile('([^=]+)=(.*)').findall(cookie)[0]
            self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])

            return self.cookie
        except:
            log_exception()


"""Bennu Specific"""


def _get_keyboard(default="", heading="", hidden=False):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return bytes(keyboard.getText(), "utf-8")
    return default


def removeNonAscii(s):
    return "".join(i for i in s if ord(i) < 128)
