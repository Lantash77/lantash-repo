import requests
import re
import json
import time
from timeit import timeit
from urllib.parse import quote_plus
from html import unescape
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Stream():
    url: str
    header: Optional[Dict] = Dict
    data: Optional[str] = ''

sess = requests.session()
UA = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'


url_ok = 'https://ok.ru/videoembed/2369629915729'
url_vk = 'http://vk.com/video_ext.php?oid=240674519&id=167825815&hash=0c78c27f3437da63&hd=1'

stream_providers = {'vk.com': 'get_vk_stream',
                    'ok.ru': 'get_ok_stream'
                        }


def get_vk_stream(videolink):
    headers = {'user-agent': UA,
               'Referer': 'https://vk.com/',
               }

    r = sess.get(videolink, headers=headers)
    manifest_dash = re.findall(r'dash_sep":"(.+?)"', r.text)[0].replace('\\', '')
    #hls_list_url = re.findall(r'hls":"(.+?)"', r.text)[0].replace('\\', '')
    #hls_stream_list = sess.get(hls_list_url, headers=headers).text
    #hls_stream_urls = sorted(re.findall(r'RESOLUTION=(.+?)\s(https.+)', hls_stream_list))

    #max_ = hls_stream_urls[-1][1]
    # SD = hls_stream_urls[0][1]
    # ask = [i[0] for i in hls_stream_urls]
    # st = sess.get(max, headers=headers)
    return Stream(manifest_dash, header=headers)

def get_ok_stream(videolink):
    headers = {'user-agent': UA,
               'Referer': 'https://vk.com/',
               }
    r = sess.get(videolink, headers=headers)
    r = unescape(r.text)
    match = re.search(r'"metadata":"({.+?})"', r, re.DOTALL)

    if match := re.search(r'"metadata":"({.+?})"', r, re.DOTALL):
        metadata_raw = match.group(1)
        # Dekodujemy escape sequence jak \u0026 i podwójne slashe
        metadata_unescaped = bytes(metadata_raw, "utf-8").decode("unicode_escape")
        metadata_json = json.loads(metadata_unescaped)
        manifest_dash = metadata_json['metadataUrl']
        manifest_HLS = metadata_json['hlsManifestUrl']
        #HLS_list = sess.get(manifest_HLS, headers=headers)
        #hls_stream_urls = sorted(re.findall(r'RESOLUTION=(.+?)\s(.+?)$', HLS_list.text, re.DOTALL))
    else:
        r = r.replace(r'\\u0026', '&').replace(r'\&', '&').replace(r'\\"', r'\"')
        manifest_dash = re.findall(r'metadataUrl":"(.+?)"', r, re.DOTALL)[0]
        manifest_dash_HD = re.findall(r'"hd","url":"(.+?)"', r)[0]
        manifest_HLS = re.findall(r'"hlsManifestUrl":"(.+?)"', r)[0]
        #HLS_list = sess.get(manifest_HLS, headers=headers)
        #hls_stream_urls = sorted(re.findall(r'RESOLUTION=(.+?)\s(.+?)$', HLS_list.text, re.DOTALL))
    return Stream(manifest_dash, header=headers)

def get_mega_stream(videolink):
    from megamine import Mega
    from megamine.crypto import base64_to_a32, a32_to_str
    mega = Mega()
    file_id, file_key = mega._parse_url(videolink).split('!')
    key = base64_to_a32(file_key)
    # Dekodowanie klucza
    k = (
        key[0] ^ key[4],
        key[1] ^ key[5],
        key[2] ^ key[6],
        key[3] ^ key[7]
    )
    k_str = a32_to_str(k)
    iv = key[4:6] + (0, 0)

    file_data = mega._api_request({'a': 'g', 'g': 1, 'p': file_id})
    file_url = file_data['g']
    file_size = file_data['s']
    #file_name = decrypt_attr(base64_url_decode(file_data['at']),k)['n']
    mega_data = {'k_str': k_str,
                 'iv': iv,
                 'file_size': file_size
                 }
    meg_str = repr(mega_data)
    meg_str = quote_plus(meg_str)
    return  Stream(file_url, data=meg_str)


def look_stream(url):

    for ul in stream_providers.keys():
        if ul in url:
            print(f'found {ul}')
            break
        else: continue
    t = globals()
    #funkcja = getattr(__loader__, uls[ul])
    print(globals())
    funkcja, head = globals()[stream_providers[ul]](url)
    print('done')



#t = get_vk_stream(url_vk)




def getstream(videolink):  # TEST Function - not for addon


    headers = {'user-agent': UA,
               'Referer': 'https://vk.com/',
               }

    r = sess.get(videolink, headers=headers)
    #rt = re.search('<div data-module="OKVideo".*?>', r.text).group(0)
    r = CleanHTML(r.text).replace(r'\\u0026', '&').replace(r'\&', '&')
    r = r.replace(r'&quot;', '"').replace(r'\\"', r'\"')
    manifest_dash = re.findall('metadataUrl":"(.+?)"', r)[0]
    #rt2 = CleanHTML(rt2).replace('\\u0026', '&').replace('\&', '&')
    #rt2 = rt2.replace('&quot;', '"').replace('\\"', '\"')
#    rt2 = rt2.replace('\\u003C', '<').replace('\\<', '<')
#    rt2 = rt2.replace('\\u003E', '>').replace('\\>', '>')

    ul = 'https://vd255.mycdn.me/?expires=1670105186724&srcIp=148.252.132.214&pr=10&srcAg=FIREFOX_36X&ms=185.226.52.5&type=1&sig=Zv7YcHMkFIs&ct=6&urls=45.136.22.5&clientType=0&zs=65&id=513723206204'
    res = sess.get(ul, headers=headers)

    rtj = json.loads(rt2, )
    rs = CleanHTML(rtj).replace('&quot;', '"')
    rs2 = rs.replace('\u0026', '&')



    manifest_dash = re.findall(r'dash_sep":"(.+?)"', r.text)[0].replace('\\', '')
    hls_list_url = re.findall(r'hls":"(.+?)"', r.text)[0].replace('\\', '')
    hls_stream_list = sess.get(hls_list_url, headers=headers).text
    hls_stream_urls = sorted(re.findall(r'RESOLUTION=(.+?)\s(https.+)', hls_stream_list))

    max_ = hls_stream_urls[-1][1]
    #SD = hls_stream_urls[0][1]
    #ask = [i[0] for i in hls_stream_urls]



    st = sess.get(manifest_dash, headers=headers)
    return manifest_dash, headers
#look_stream('https://ok.ru/videoembed/2087271598820')
#print('dupa')



