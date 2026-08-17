from urllib.request import Request, urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser
import re

MAX_BYTES = 700_000
TIMEOUT = 10

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
        self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script","style","noscript","svg"}: self.skip += 1
    def handle_endtag(self, tag):
        if tag.lower() in {"script","style","noscript","svg"} and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            t=re.sub(r"\s+"," ",data).strip()
            if t: self.parts.append(t)

def fetch_url(url):
    u=urlparse(url)
    if u.scheme not in {"http","https"} or not u.netloc:
        raise ValueError("Only http/https URLs are allowed")
    req=Request(url, headers={"User-Agent":"ALPHA-V2/1.0"})
    with urlopen(req, timeout=TIMEOUT) as r:
        raw=r.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:
            raw=raw[:MAX_BYTES]
        ctype=r.headers.get("Content-Type","")
        charset="utf-8"
        m=re.search(r"charset=([^;]+)", ctype, re.I)
        if m: charset=m.group(1).strip()
        text=raw.decode(charset, errors="replace")
    parser=TextExtractor()
    parser.feed(text)
    return {"url":url, "content_type":ctype, "text":" ".join(parser.parts)[:20000]}
