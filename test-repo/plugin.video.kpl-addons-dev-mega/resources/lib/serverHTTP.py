from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import TCPServer

import socket
from urllib.parse import urlparse, parse_qs
from ast import literal_eval
try:
    from resources.lib import cache
except:
    import cache
'''
# moved to getstream function to reduce requests mega api
# one request to api only needed to get video url and iv
try:
    from megamine import Mega
    from megamine.crypto import base64_to_a32, a32_to_str, decrypt_attr, base64_url_decode    
except:
    from resources.lib.megamine import Mega
    from resources.lib.megamine.crypto import base64_to_a32, a32_to_str, decrypt_attr, base64_url_decode    
'''
try:
    from Crypto.Cipher import AES
    from Crypto.Util import Counter
except ImportError:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util import Counter
import requests
from typing import NamedTuple, Dict
from contextlib import closing
import re

sess = requests.session()

class parsedUrl(NamedTuple):
    url: str
    type: str
    data: Dict
    headers: Dict[str, str]

class MegaVideoProxy(BaseHTTPRequestHandler):

    def parseUrl(self):

        if '|' in self.path:
            path, headers = self.path.split('|')
            headers = parse_qs(headers)
        else:
            path = self.path
            headers = {}

        query = parse_qs(urlparse(path).query)
        url = query.get('url', [None])[0]
        type = query.get('type', [None])[0]
        mega_data = query.get('mega_data', [None])[0]
        if mega_data:
            mega_data = literal_eval(mega_data)
        return parsedUrl(url, type, mega_data, headers)

    def do_HEAD(self, status=None, headers=None):

        if not headers:
            print(f'received  HEAD from KODI URL {self.path}')

            #print(f'HEAD HEADERS {self.headers}')
            parsed = self.parseUrl()
            hdr_res = sess.head(parsed.url)
            headers = hdr_res.headers

        # Nagłówki HTTP

        self.send_response(206 if headers.get('Range') else 200)
        self.send_header('Content-Type', 'video/mp4')
        #replaced content as application/octet-stream received and not playing ball
        #self.send_header('Content-Type',
        #                 headers.get('Content-Type'))
        self.send_header('Content-Length',
                         headers.get('Content-Length'))
        #self.send_header('Content-Transfer-Encoding',
        #                 headers.get('Content-Transfer-Encoding'))
        #self.send_header('Accept-Ranges', 'bytes')
        if headers.get('Content-Range'):
            self.send_header('Content-Range',
                             headers.get('Content-Range'))
        self.end_headers()

    def do_GET(self):
        print('received  do_GET')

        parsed = self.parseUrl()

        if not parsed.url:
            self.send_error(400, "Missing 'url' parameter")
            return
        if parsed.type == 'mega':
            try:
                file_size = parsed.data.get('file_size')
                iv = parsed.data.get('iv')
                k_str = parsed.data.get('k_str')

                # Obsługa Range
                range_header = self.headers.get("Range")
                print(f"📡 request range: {range_header}")
                if range_header:
                    m = re.match(r"bytes=(\d+)-(\d+)?", range_header)
                    if m:
                        start = int(m.group(1))
                        end = int(m.group(2)) if m.group(2) else file_size - 1
                    else:
                        self.send_error(400, "Invalid Range header")
                        return
                else:
                    start = 0
                    end = file_size - 1

                chunk_size = end - start + 1
                block_offset = start // 16
                byte_offset = start % 16

                # 🧠 Setting AES-CTR with proper IV
                iv64 = (iv[0] << 32) + iv[1]
                initial_counter = (iv64 << 64) + block_offset
                counter = Counter.new(128, initial_value=initial_counter)
                aes = AES.new(k_str, AES.MODE_CTR, counter=counter)

                if byte_offset:
                    aes.decrypt(b'\x00' * byte_offset)

                # Download encypted content
                #headers = {"Range": f"bytes={start}-{end}",
                headers = {"Range": f"bytes={start}-",
                           }
                response = sess.get(parsed.url, headers=headers,
                                        stream=True, timeout=15)

                response.raise_for_status()
                self.do_HEAD(response.headers)


                print(f"🎬 Serving range: {range_header or 'full'}")
                print(f"📦 chunk_size: {chunk_size}")
                print(f"📡 Mega Range: {headers['Range']}")
                print(f"🧮 AES-CTR offset: block={block_offset}, byte offset={byte_offset}")

                # Strumieniowanie
                for chunk in response.iter_content(chunk_size=65536):
                    if not chunk:
                        break

                    decrypted = aes.decrypt(chunk)
                    self.wfile.write(decrypted)
            except Exception as e:
                import html
                #print(f"❌ Error: {e}")
                self.send_error(500, html.escape(repr(e)))

    def do_POST(self):
        """Handle http post requests, used for license"""


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cache.cache_insert('proxyport', str(s.getsockname()[1]))

        return s.getsockname()[1]

'''
def run():
    port = find_free_port()
    server_address = ('127.0.0.1', port)
    httpd = TCPServer(server_address, MegaVideoProxy)
    print(f"🚀 Mega proxy działa na http://localhost:{port}")
    httpd.serve_forever()
'''
def run(server_class=TCPServer, handler_class=MegaVideoProxy, port=find_free_port()):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"🚀 Mega proxy succesfully started on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
