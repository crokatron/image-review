"""Real HTTP authorization for reviewer UI, media, decisions, exports and import."""
import base64,hashlib,http.client,importlib.util,json,os,sys,tempfile,threading,time,types,unittest
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
BASE=Path(__file__).resolve().parents[1]

class GatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        os.environ['PROJECT_DATA']=str(cls.root/'data')
        mock=types.ModuleType('server_lamp');mock.Handler=SimpleHTTPRequestHandler;mock.CAD_LOCK=threading.Lock();sys.modules['server_lamp']=mock
        spec=importlib.util.spec_from_file_location('review_auth_gateway',BASE/'integrated-server.py')
        cls.gateway=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.gateway);cls.gateway.ROOT=cls.root
        cls.gateway.Handler.log_message=lambda *a:None
        (cls.root/'public/image-review').mkdir(parents=True)
        for name in ('index.html','style.css','app.js'):(cls.root/'public/image-review'/name).write_bytes((BASE/'public'/name).read_bytes())
        cls.rsa=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        cls.gateway.ACCESS.keys={'test':cls.rsa.public_key()};cls.gateway.ACCESS.keys_until=time.time()+3600
        _,rev=cls.gateway.ACCESS.users()
        cls.gateway.ACCESS.update({'email':'family@example.com','projects':['mechanisms'],'enabled':True},rev,cls.gateway.OWNER_EMAIL)
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),cls.gateway.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
        body=b'\xff\xd8harmless\xff\xd9';cls.ident=hashlib.sha256(b'fixture').hexdigest()
        cls.gateway.IMAGE_REVIEW.import_items([{'sha256':cls.ident,'band':'Borderline','score':0.,'subtype':'Photo','width':100,'height':100,'media_sha':hashlib.sha256(body).hexdigest(),'media_size':len(body)}]);cls.gateway.IMAGE_REVIEW.import_media(cls.ident,body)
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join();cls.tmp.cleanup()
    def token(self,email):
        def b64(b):return base64.urlsafe_b64encode(b).decode().rstrip('=')
        g=self.gateway;claims={'email':email,'sub':'test','type':'app','iss':g.ACCESS_ISSUER,'aud':[g.ACCESS_AUDIENCE],'iat':int(time.time()),'exp':int(time.time())+3600}
        message=b64(g.canonical_json({'alg':'RS256','kid':'test'}))+'.'+b64(g.canonical_json(claims))
        return message+'.'+b64(self.rsa.sign(message.encode(),padding.PKCS1v15(),hashes.SHA256()))
    def call(self,path,token=None,method='GET',body=None,origin=None):
        headers={'Host':'127.0.0.1:9070'}
        if token:headers['Cf-Access-Jwt-Assertion']=token
        if origin:headers['Origin']=origin
        if body is not None:headers['Content-Type']='application/json';body=json.dumps(body).encode()
        c=http.client.HTTPConnection('127.0.0.1',self.http.server_port);c.request(method,path,body,headers);r=c.getresponse();status=r.status;data=r.read();c.close();return status,data
    def test_owner_only_every_route_and_originals_not_served(self):
        owner=self.token(self.gateway.OWNER_EMAIL);family=self.token('family@example.com')
        routes=['/image-review/','/image-review/style.css','/image-review/app.js','/image-review/api/queue','/image-review/api/learning','/image-review/api/export','/image-review/api/media/'+self.ident]
        for route in routes:
            self.assertIn(self.call(route)[0],(303,401));self.assertEqual(self.call(route,family)[0],403);self.assertEqual(self.call(route,owner)[0],200)
        self.assertEqual(self.call('/data/image-review/decisions.sqlite3',owner)[0],404)
        for route in ['/image-review/api/people/create','/image-review/api/people/decision','/image-review/api/people/undo','/image-review/api/adult/decision','/image-review/api/adult/undo','/image-review/api/decision','/image-review/api/undo','/image-review/api/learning/train','/image-review/api/learning/predict','/image-review/api/import','/image-review/api/media/'+self.ident]:
            self.assertEqual(self.call(route,family,'POST',{},'https://projects.mungoon.net')[0],403)
    def test_import_signed_only_and_origin_required(self):
        owner=self.token(self.gateway.OWNER_EMAIL)
        self.assertEqual(self.call('/image-review/api/import',owner,'POST',[],'https://projects.mungoon.net')[0],403)
        self.assertEqual(self.call('/image-review/api/adult/import-predictions',owner,'POST',{},'https://projects.mungoon.net')[0],403)
        self.assertEqual(self.call('/image-review/api/adult/import-predictions',self.token('family@example.com'),'POST',{},'https://projects.mungoon.net')[0],403)
        self.assertEqual(self.call('/image-review/api/decision',owner,'POST',{},'https://evil.example')[0],403)
        self.assertEqual(self.call('/image-review/api/learning/train',owner,'POST',{},'https://evil.example')[0],403)
        for route in ('people/create','people/decision','adult/decision'):
            self.assertEqual(self.call('/image-review/api/'+route,owner,'POST',{},'https://evil.example')[0],403)
        code,body=self.call('/image-review/api/learning/train',owner,'POST',{},'https://projects.mungoon.net')
        self.assertEqual(code,200);self.assertFalse(json.loads(body)['eligible'])
        self.assertEqual(self.call('/image-review/api/queue',owner,'HEAD')[0],405)
        self.assertEqual(self.call('/image-review/%2e%2e/data',owner)[0],400)

if __name__=='__main__':unittest.main()
