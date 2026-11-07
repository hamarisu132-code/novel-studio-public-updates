import json, sqlite3, threading, webbrowser, zipfile, io, os, sys, secrets
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
DB=DATA/'novel_studio.db'
TOKEN_FILE=DATA/'.running_token'
SHUTDOWN_TOKEN=secrets.token_urlsafe(32)
SERVER=None

def conn():
 c=sqlite3.connect(DB,timeout=15); c.row_factory=sqlite3.Row; c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA foreign_keys=ON'); return c
def init_db():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS works(id INTEGER PRIMARY KEY,title TEXT NOT NULL,genre TEXT DEFAULT '',description TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
 CREATE TABLE IF NOT EXISTS chapters(id INTEGER PRIMARY KEY,work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE,title TEXT NOT NULL,body TEXT DEFAULT '',position INTEGER DEFAULT 0,status TEXT DEFAULT '下書き',updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
 CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY,work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE,kind TEXT NOT NULL,title TEXT NOT NULL,body TEXT DEFAULT '',tag TEXT DEFAULT '',status TEXT DEFAULT '',chapter_ref TEXT DEFAULT '',updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
 CREATE INDEX IF NOT EXISTS idx_chapters_work ON chapters(work_id); CREATE INDEX IF NOT EXISTS idx_entries_work ON entries(work_id,kind);''')

def create_daily_backup():
 from datetime import date
 import shutil
 backups=DATA/'backups'; backups.mkdir(parents=True,exist_ok=True)
 path=backups/('novel_studio_'+date.today().isoformat()+'.db')
 if not path.exists() and DB.exists():
  with sqlite3.connect(DB) as source, sqlite3.connect(path) as target:
   source.backup(target)
 for old in sorted(backups.glob('novel_studio_*.db'))[:-30]:
  old.unlink()

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'static'),**kwargs)
 def log_message(self,fmt,*args): pass
 def reply(self,status,data):
  b=json.dumps(data,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  p=urlparse(self.path)
  if p.path=='/api/data':
   with conn() as c:
    result={t:[dict(x) for x in c.execute('SELECT * FROM '+t+' ORDER BY '+('position,id' if t=='chapters' else 'id DESC'))] for t in ('works','chapters','entries')}
   return self.reply(200,result)
  if p.path=='/api/backup':
   with conn() as c:
    data={t:[dict(x) for x in c.execute('SELECT * FROM '+t)] for t in ('works','chapters','entries')}
   buf=io.BytesIO()
   with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('novel_studio_backup.json',json.dumps(data,ensure_ascii=False,indent=2))
    for w in data['works']:
     for ch in data['chapters']:
      if ch['work_id']==w['id']:
       safe=''.join(x for x in (w['title']+'_'+ch['title']) if x not in '/\\:*?"<>|')[:100]
       z.writestr(f'texts/{w["id"]}_{ch["id"]}_{safe}.txt',ch['body'])
   b=buf.getvalue(); self.send_response(200); self.send_header('Content-Type','application/zip'); self.send_header('Content-Disposition','attachment; filename="novel_studio_backup.zip"'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
  return super().do_GET()
 def do_POST(self):
  p=urlparse(self.path).path
  if p=='/api/shutdown':
   try:
    n=int(self.headers.get('Content-Length','0'))
    obj=json.loads(self.rfile.read(n)) if 0<n<1024 else {}
    if obj.get('token')!=SHUTDOWN_TOKEN: return self.reply(403,{'error':'forbidden'})
    self.reply(200,{'ok':True})
    threading.Thread(target=SERVER.shutdown,daemon=True).start()
    return
   except (ValueError,TypeError): return self.reply(400,{'error':'invalid request'})
  if p!='/api/save': return self.reply(404,{'error':'not found'})
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n>5_000_000: return self.reply(413,{'error':'too large'})
   obj=json.loads(self.rfile.read(n)); table=obj['table']; values=obj.get('values',{}); rid=obj.get('id')
   allowed={'works':{'title','genre','description'},'chapters':{'work_id','title','body','position','status'},'entries':{'work_id','kind','title','body','tag','status','chapter_ref'}}
   if table not in allowed or not isinstance(values,dict): return self.reply(400,{'error':'invalid table or values'})
   values={k:v for k,v in values.items() if k in allowed[table]}
   if not values: return self.reply(400,{'error':'empty values'})
   with conn() as c:
    if rid:
     cols=','.join(f'{k}=?' for k in values)
     cur=c.execute(f'UPDATE {table} SET {cols},updated_at=CURRENT_TIMESTAMP WHERE id=?',list(values.values())+[rid]);
     if cur.rowcount==0: return self.reply(404,{'error':'missing record'})
    else:
     cols=','.join(values); marks=','.join('?' for _ in values)
     cur=c.execute(f'INSERT INTO {table} ({cols}) VALUES ({marks})',list(values.values())); rid=cur.lastrowid
   return self.reply(200,{'id':rid})
  except (ValueError,KeyError,sqlite3.Error,TypeError) as e: return self.reply(400,{'error':str(e)})
 def do_DELETE(self):
  p=urlparse(self.path).path
  if p!='/api/delete': return self.reply(404,{'error':'not found'})
  try:
   n=int(self.headers.get('Content-Length','0')); obj=json.loads(self.rfile.read(n)); table=obj['table']; rid=int(obj['id'])
   if table not in ('works','chapters','entries'): return self.reply(400,{'error':'invalid table'})
   with conn() as c: c.execute(f'DELETE FROM {table} WHERE id=?',(rid,))
   return self.reply(200,{'ok':True})
  except (ValueError,KeyError,sqlite3.Error) as e: return self.reply(400,{'error':str(e)})
if __name__=='__main__':
 init_db()
 create_daily_backup()
 port=8765
 try:
  server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
  SERVER=server
 except OSError:
  print('ポート8765が使用中です。既に起動している場合は http://127.0.0.1:8765 を開いてください。'); input('Enterで終了'); sys.exit(1)
 TOKEN_FILE.write_text(SHUTDOWN_TOKEN,encoding='utf-8')
 print('NOVEL STUDIO 起動: http://127.0.0.1:8765')
 threading.Timer(0.8,lambda:webbrowser.open('http://127.0.0.1:8765')).start()
 try: server.serve_forever()
 except KeyboardInterrupt: pass
 finally:
  server.server_close()
  if TOKEN_FILE.exists() and TOKEN_FILE.read_text(encoding="utf-8")==SHUTDOWN_TOKEN: TOKEN_FILE.unlink()
