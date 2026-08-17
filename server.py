from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import json, argparse, mimetypes
from .agent import AlphaAgent

WEB=Path(__file__).resolve().parent.parent/"web"

def response(handler, code, obj):
    raw=json.dumps(obj,ensure_ascii=False).encode()
    handler.send_response(code)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Content-Length",str(len(raw)))
    handler.send_header("Access-Control-Allow-Origin","*")
    handler.end_headers()
    handler.wfile.write(raw)

class Handler(BaseHTTPRequestHandler):
    agent=None
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.end_headers()
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/state":
            return response(self,200,self.agent.introspect())
        if path=="/api/memories":
            return response(self,200,self.agent.store.state.memories[-100:])
        if path=="/api/evolution":
            return response(self,200,self.agent.store.state.evolution[-100:])
        if path=="/api/experiments":
            return response(self,200,self.agent.store.state.experiments[-100:])
        if path.startswith("/api/"):
            return response(self,404,{"error":"not found"})
        rel="index.html" if path=="/" else path.lstrip("/")
        f=(WEB/rel).resolve()
        if not str(f).startswith(str(WEB.resolve())) or not f.exists() or not f.is_file():
            return response(self,404,{"error":"not found"})
        data=f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type",mimetypes.guess_type(str(f))[0] or "application/octet-stream")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_POST(self):
        path=urlparse(self.path).path
        n=int(self.headers.get("Content-Length","0"))
        body=self.rfile.read(n)
        try: data=json.loads(body or b"{}")
        except Exception: return response(self,400,{"error":"invalid json"})
        try:
            if path=="/api/chat":
                return response(self,200,self.agent.answer(str(data.get("question",""))))
            if path=="/api/research":
                return response(self,200,self.agent.research(str(data.get("url",""))))
            if path=="/api/experiment":
                return response(self,200,self.agent.experiment(str(data.get("question","")),str(data.get("hypothesis",""))))
            if path=="/api/evolve":
                return response(self,200,self.agent.evolve())
            if path=="/api/learn":
                return response(self,200,self.agent.learn_from_text(str(data.get("text","")),str(data.get("source","human")),float(data.get("confidence",0.5))))
            return response(self,404,{"error":"not found"})
        except Exception as e:
            return response(self,500,{"error":str(e)})
    def log_message(self,*args): pass

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--host",default="127.0.0.1")
    ap.add_argument("--port",type=int,default=8080)
    ap.add_argument("--internet",action="store_true")
    args=ap.parse_args()
    Handler.agent=AlphaAgent(internet=args.internet)
    print(f"ALPHA V2 listening on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()

if __name__=="__main__":
    main()
