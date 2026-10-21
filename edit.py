#!/usr/bin/env python3
"""Local layout editor for the site. Run `python3 edit.py`, then open the URL it prints.
Add ?edit to any post that supports it (my-translator.html) to drag things around; Save writes the file."""
import json, re, http.server, webbrowser, os, sys
PORT = 8791
HERE = os.path.dirname(os.path.abspath(__file__))

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=HERE, **k)
    def log_message(self, *a): pass
    def do_POST(self):
        if self.path != '/save': return self.send_error(404)
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        name = os.path.basename(body['file'])
        path = os.path.join(HERE, name)
        if not os.path.isfile(path): return self.send_error(404, 'no such file')
        src = open(path, encoding='utf-8').read()
        block = '<script id="layout" type="application/json">\n' + json.dumps(body['layout'], indent=1) + '\n</script>'
        new, n = re.subn(r'<script id="layout" type="application/json">.*?</script>', lambda m: block, src, count=1, flags=re.S)
        if n != 1: return self.send_error(400, 'layout block not found')
        open(path, 'w', encoding='utf-8').write(new)
        self.send_response(200); self.send_header('Content-Type', 'text/plain'); self.end_headers()
        self.wfile.write(f'Saved {len(body["layout"]["items"])} items to {name}'.encode())

url = f'http://localhost:{PORT}/my-translator.html?edit'
print('Editing at', url, '\nCtrl+C to stop.')
webbrowser.open(url)
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
