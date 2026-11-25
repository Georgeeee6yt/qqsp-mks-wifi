import http.server, json, time, urllib.parse, sys, os
ROOT = sys.argv[1]; LOG = sys.argv[2]
state = {'printing': 0, 'pr': '', 'pn': '', 'age': -1}
def log(o): open(LOG, 'a').write(json.dumps(o, ensure_ascii=False) + '\n')
class H(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ct='application/json; charset=utf-8'):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header('Content-Type', ct); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)   # the ESP server decodes args once
        if u.path == '/': return self._send(200, open(os.path.join(ROOT, 'index.htm'), 'rb').read(), 'text/html; charset=utf-8')
        if u.path == '/status': return self._send(200, json.dumps({'ver': 'QQS1.1_251125', 'mode': 'sta', 'ssid': 'CHT-家裡', 'ip': '192.168.1.117', 'rssi': -61, 'mac': 'AA', 'printing': state['printing'], 'busy': 0, 'pr': state['pr'], 'pn': state['pn'], 'age': state['age']}, ensure_ascii=False))
        if u.path == '/mock':   # test hook: /mock?pr=...&pn=...&age=...&printing=...
            for k in ('pr', 'pn'): state[k] = q.get(k, [''])[0]
            state['age'] = int(q.get('age', ['-1'])[0]); state['printing'] = int(q.get('printing', ['0'])[0])
            return self._send(200, 'ok', 'text/plain')
        f = os.path.join(ROOT, u.path.lstrip('/'))
        if u.path.endswith('.gif') and os.path.isfile(f): return self._send(200, open(f, 'rb').read(), 'image/gif')
        if u.path == '/scan':
            time.sleep(1.5)
            return self._send(200, json.dumps([{'ssid': 'CHT-家裡', 'rssi': -48, 'enc': 1, 'ch': 6}, {'ssid': 'Neighbor "5G"', 'rssi': -70, 'enc': 1, 'ch': 11}, {'ssid': 'FreeWiFi', 'rssi': -85, 'enc': 0, 'ch': 1}], ensure_ascii=False))
        if u.path == '/update_cfg':
            a = {k: v[0] for k, v in q.items()}; log({'cfg': a})
            return self._send(200, '<p>Configure successfully!<br />Please use the new ip to connect again.</p>', 'text/html')
        self._send(404, 'not found', 'text/plain')
    def do_POST(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        n = int(self.headers.get('Content-Length', 0)); data = b''
        while len(data) < n: data += self.rfile.read(min(65536, n - len(data))); time.sleep(0.002)
        if u.path == '/upload':
            if state['printing']: return self._send(409, '409 Conflict', 'text/plain')
            log({'upload': q.get('X-Filename', [''])[0], 'len': len(data), 'ct': self.headers.get('Content-Type'), 'head': data[:16].decode('latin-1')})
            return self._send(200, '{"err":0}')
        self._send(404, 'x', 'text/plain')
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(('127.0.0.1', 8765), H).serve_forever()
