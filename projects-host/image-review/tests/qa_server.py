"""Loopback-only browser fixture: real gateway auth with ephemeral test JWTs, synthetic images."""
import base64,hashlib,importlib.util,io,json,os,sys,threading,time,types
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'qa';ROOT.mkdir(exist_ok=True)
os.environ['PROJECT_DATA']=str(ROOT/'data')
mock=types.ModuleType('server_lamp');mock.Handler=SimpleHTTPRequestHandler;mock.CAD_LOCK=threading.Lock();sys.modules['server_lamp']=mock
spec=importlib.util.spec_from_file_location('review_qa_gateway',BASE/'integrated-server.py')
gateway=importlib.util.module_from_spec(spec);spec.loader.exec_module(gateway)
gateway.ROOT=ROOT
(ROOT/'release.json').write_text('{"id":"review-qa"}')
for name in ('index.html','style.css','app.js'):
    p=ROOT/'public/image-review'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((BASE/'public'/name).read_bytes())
key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
gateway.ACCESS.keys={'qa':key.public_key()};gateway.ACCESS.keys_until=time.time()+86400
def b64(b):return base64.urlsafe_b64encode(b).decode().rstrip('=')
claims={'email':gateway.OWNER_EMAIL,'sub':'qa-owner','type':'app','iss':gateway.ACCESS_ISSUER,'aud':[gateway.ACCESS_AUDIENCE],'iat':int(time.time()),'exp':int(time.time())+86400}
header=b64(gateway.canonical_json({'alg':'RS256','kid':'qa'}));payload=b64(gateway.canonical_json(claims));message=header+'.'+payload
TOKEN=message+'.'+b64(key.sign(message.encode(),padding.PKCS1v15(),hashes.SHA256()))
store=gateway.IMAGE_REVIEW
def reset():
    db=store.connect()
    for table in ('events','items','learning','annotations','annotation_events','image_people','people','adult_predictions'):db.execute('DELETE FROM '+table)
    db.commit();db.close()
    rows=[]
    for i in range(6):
        h=hashlib.sha256(('qa-harmless-'+str(i)).encode()).hexdigest()
        image=Image.new('RGB',(800,650),['#315d46','#546b3a','#7d584b'][i%3]);draw=ImageDraw.Draw(image)
        draw.rounded_rectangle((85,80,715,535),40,fill='#dcdfbe');draw.ellipse((270,150,530,410),fill='#658251');draw.text((300,450),'SAMPLE '+str(i+1),fill='#263b2c',font_size=30)
        out=io.BytesIO();image.save(out,'JPEG');body=out.getvalue()
        row={'sha256':h,'band':'Borderline' if i<4 else 'Likely memes' if i==4 else 'Likely non-memes','score':i-.5,'subtype':'Photo','width':800,'height':650,'media_sha':hashlib.sha256(body).hexdigest(),'media_size':len(body)}
        store.import_items([row]);store.import_media(h,body);rows.append(row)
    return rows
rows=reset()
class Handler(gateway.Handler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/qa-session':return self.send_json({'token':TOKEN,'ids':[r['sha256'] for r in rows]})
        return super().do_GET()
    def do_POST(self):
        if self.path=='/qa-reset':reset();return self.send_json({'reset':True})
        if self.path=='/qa-adult-ml':
            body={'model':gateway.ADULT_MODEL,'model_revision':gateway.ADULT_MODEL_REVISION,
                  'items':[{'sha256':row['sha256'],'media_sha':row['media_sha'],'score':[.98,.42,.02,.01,.99,.03][i]} for i,row in enumerate(rows)]}
            return self.send_json(store.import_adult_predictions(body))
        if self.path=='/qa-learning':
            # Extra synthetic reviewed scores, never deployed to the NAS.
            db=store.connect()
            for i in range(300):
                ident=hashlib.sha256(('learning-fixture-'+str(i)).encode()).hexdigest()
                label='meme' if i%2 else 'not_meme'
                db.execute('INSERT OR REPLACE INTO items(sha256,band,score,subtype,width,height,media_sha,media_size,ready,label,revision) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(ident,'Borderline',3 if i%2 else 1,'Photo',100,100,ident,10,1,label,1))
            db.commit();db.close();return self.send_json({'seeded':300})
        return super().do_POST()
http=ThreadingHTTPServer(('127.0.0.1',9142),Handler)
gateway.ORIGINS.add('http://127.0.0.1:9142')
print('QA fixture listening on 127.0.0.1:9142 (synthetic images only)',flush=True)
http.serve_forever()
