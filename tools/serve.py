"""Local-only preview with inspectable export files. Python standard library only."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, re, argparse, urllib.parse
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_POST(self):
        if self.path!='/api/export':self.send_error(404);return
        expected=f'http://127.0.0.1:{self.server.server_port}'
        if self.headers.get('Origin')!=expected or self.headers.get('Content-Type','').split(';')[0]!='application/json':self.send_error(403);return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=8_000_000:raise ValueError('Export size out of range')
            body=json.loads(self.rfile.read(size));name=body['name'];content=body['content']
            if not isinstance(content,str) or not re.fullmatch(r'StreamSignal_[A-Za-z0-9_-]+\.(csv|html|json)',name):raise ValueError('Invalid export')
            target=ROOT/'exported';target.mkdir(exist_ok=True)
            candidate=target/name;stem=candidate.stem;suffix=candidate.suffix;counter=1
            while True:
                try:
                    with candidate.open('x',encoding='utf-8',newline='') as f:f.write(content)
                    break
                except FileExistsError:counter+=1;candidate=target/f'{stem}_{counter}{suffix}'
            data=json.dumps({'url':'exported/'+urllib.parse.quote(candidate.name)}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        except (ValueError,TypeError,KeyError):self.send_error(400,'Invalid export request')
    def end_headers(self):
        if urllib.parse.urlsplit(self.path).path.startswith('/exported/') or urllib.parse.urlsplit(self.path).path in ['/results/forecast_report.html','/results/multihazard_report.html']:
            name=Path(urllib.parse.urlsplit(self.path).path).name
            if name in ['forecast_report.html','multihazard_report.html'] or re.fullmatch(r'StreamSignal_[A-Za-z0-9_-]+\.(csv|html|json)',name):self.send_header('Content-Disposition',f'attachment; filename="{name}"')
        self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'StreamSignal: http://127.0.0.1:{args.port}/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
