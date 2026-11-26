import http.server, json, time, urllib.parse, sys, os
ROOT = sys.argv[1]; LOG = sys.argv[2]
state = {'printing': 0, 'pr': '', 'pn': '', 'age': -1}
# Fake SD card, as Marlin v3.2.14 lists it (directory order; 8.3 names from a FAT image made with pyfatfs)
SD = {'': [('f', 40, '___V3.GCO', '燈罩_v3.gcode'), ('f', 2345678, 'LAMPSHAD.GCO', 'lampshade_QQSPro_157mm.gcode'),
           ('f', 40, 'TEST.GCO', 'TEST.GCO'), ('f', 40, '______0_.GCO', '非平面燈罩_0.2mm_PETG_3h12m_QQSPro_第二版_最終修正版_真的最後一次_這次一定不改了.gcode'),
           ('f', 40, 'EMOJI___.GCO', 'emoji_😀_"quote".gcode'), ('d', 0, '_____', '模型資料夾')],
      '/_____': [('f', 300, '_.GCO', '貓.gcode')]}
LIST = {'on': False}; PRINT = {'r': -1, 'ms': -1, 't': 0}
hexs = lambda s: s.encode('latin-1').hex().upper()
def unhex(h): return bytes.fromhex(h).decode('latin-1')
def log(o): open(LOG, 'a').write(json.dumps(o, ensure_ascii=False) + '\n')
class H(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ct='application/json; charset=utf-8'):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header('Content-Type', ct); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)   # the ESP server decodes args once
        if u.path == '/': return self._send(200, open(os.path.join(ROOT, 'index.htm'), 'rb').read(), 'text/html; charset=utf-8')
        if u.path == '/status': return self._send(200, json.dumps({'ver': 'QQS1.4_251126', 'mode': 'sta', 'ssid': 'CHT-家裡', 'ip': '192.168.1.117', 'rssi': -61, 'mac': 'AA', 'printing': state['printing'], 'busy': 0, 'pr': state['pr'], 'pn': state['pn'], 'age': state['age'], 'heap': 21384, 'hmin': 17920}, ensure_ascii=False))
        if u.path == '/mock':   # test hook: /mock?pr=...&pn=...&age=...&printing=...
            for k in ('pr', 'pn'): state[k] = q.get(k, [''])[0]
            state['age'] = int(q.get('age', ['-1'])[0]); state['printing'] = int(q.get('printing', ['0'])[0])
            return self._send(200, 'ok', 'text/plain')
        f = os.path.join(ROOT, u.path.lstrip('/'))
        if u.path.endswith('.gif') and os.path.isfile(f): return self._send(200, open(f, 'rb').read(), 'image/gif')
        if u.path == '/files':
            if 'go' in q:
                d = unhex(q.get('d', [''])[0]); LIST.clear(); LIST.update(on=True, t=time.time(), d=q.get('d', [''])[0], path=d)
                return self._send(200, '{"st":"wait"}')
            if not LIST.get('on'): return self._send(200, '{"st":"none"}')
            if time.time() - LIST['t'] < 0.5: return self._send(200, json.dumps({'st': 'wait', 'got': 0}))
            if LIST['path'] not in SD: return self._send(200, json.dumps({'st': 'ok', 'd': LIST['d'], 'code': 3, 'total': 0, 'got': 0, 'f': []}))
            ent = SD[LIST['path']]
            return self._send(200, json.dumps({'st': 'ok', 'd': LIST['d'], 'code': 0, 'total': len(ent), 'got': len(ent), 'f': [[1 if t == 'd' else 0, sz, hexs(dos), name] for t, sz, dos, name in ent]}, ensure_ascii=False))
        if u.path == '/print':
            if 'go' in q:
                path = unhex(q['f'][0]); PRINT.update(r=-1, t=time.time()); PRINT['path'] = path
                with open(LOG, 'a') as lf: lf.write(json.dumps({'print': path}, ensure_ascii=False) + '\n')
            elif PRINT['r'] < 0 and time.time() - PRINT['t'] > 0.6:
                path = PRINT['path']; parent, _, dos = path.rpartition('/')
                ent = [e for e in SD.get(parent, []) if e[2] == dos and e[0] == 'f']
                busy = state['pr'].startswith('s=') and not state['pr'].startswith('s=0')
                PRINT['r'] = 1 if busy else 3 if not ent else 0
                if PRINT['r'] == 0:
                    state.update(pr='s=2 p=0 e=3 r=-1 t=300/240 b=600/80 f=0 v=100 w=100 z=0 a=0', pn=ent[0][3], age=500, printing=1)
            return self._send(200, json.dumps({'r': PRINT['r'], 'ms': int((time.time() - PRINT['t']) * 1000)}))
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
            n = q.get('X-Filename', [''])[0]; SD[''].append(('f', len(data), ('UP%06d.GCO' % (len(SD['']))), n))
            return self._send(200, '{"err":0}')
        self._send(404, 'x', 'text/plain')
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(('127.0.0.1', 8765), H).serve_forever()
