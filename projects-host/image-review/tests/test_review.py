import hashlib,importlib.util,json,sys,tempfile,threading,unittest,uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'host'))
from image_review import ImageReview,ReviewConflict

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=ImageReview(self.temp.name)
        self.body=b'\xff\xd8synthetic-jpeg\xff\xd9'
        self.ids=[hashlib.sha256(('fixture'+str(i)).encode()).hexdigest() for i in range(3)]
        self.items=[{'sha256':h,'band':['Borderline','Likely memes','Likely non-memes'][i],'score':i-.5,'subtype':'Photo','width':640,'height':480,'media_sha':hashlib.sha256(self.body).hexdigest(),'media_size':len(self.body)} for i,h in enumerate(self.ids)]
        self.store.import_items(self.items)
        for h in self.ids:self.store.import_media(h,self.body)
    def tearDown(self):self.temp.cleanup()
    def value(self,i=0,label='meme',revision=0):return {'op':str(uuid.uuid4()),'sha256':self.ids[i],'label':label,'revision':revision}
    def test_reopen_persistence_and_reversible_export(self):
        result=self.store.decide(self.value(),'owner')
        other=ImageReview(self.temp.name)
        self.assertEqual(other.queue({})['selected']['reviewed'],1)
        body,_,_=other.export('json');doc=json.loads(body)
        self.assertFalse(doc['original_images_modified']);self.assertEqual(doc['events'][0]['previous_label'],None)
        other.undo({'op':str(uuid.uuid4()),'event':result['event']},'owner')
        self.assertEqual(other.queue({})['selected']['pending'],1)
        doc=json.loads(other.export('json')[0]);self.assertEqual(len(doc['events']),2);self.assertEqual(doc['events'][1]['undo_of'],result['event'])
        self.assertIsNone(doc['items'][0]['label'])
    def test_lost_response_retry_and_idempotency(self):
        value=self.value();first=self.store.decide(value,'owner');second=self.store.decide(value,'owner')
        self.assertTrue(second['replayed']);self.assertEqual(first['event'],second['event'])
        with self.assertRaises(ReviewConflict):self.store.decide({**value,'label':'not_meme'},'owner')
        self.assertEqual(len(json.loads(self.store.export('json')[0])['events']),1)
    def test_concurrent_devices_and_stale_undo(self):
        values=[self.value(label='meme'),self.value(label='not_meme')]
        def save(v):
            try:return self.store.decide(v,'owner')
            except ReviewConflict:return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(save,values))
        self.assertEqual(results.count('conflict'),1)
        first=next(r for r in results if r!='conflict')
        self.store.decide(self.value(label='skip',revision=1),'owner')
        with self.assertRaises(ReviewConflict):self.store.undo({'op':str(uuid.uuid4()),'event':first['event']},'owner')
    def test_filters_skip_and_all_done(self):
        result=self.store.decide(self.value(label='skip'),'owner')
        self.assertEqual(self.store.queue({})['items'],[])
        self.assertEqual(self.store.queue({'state':['skipped']})['items'][0]['label'],'skip')
        self.store.decide(self.value(label='not_meme',revision=1),'owner')
        self.assertEqual(self.store.queue({})['queue_count'],0)
        self.assertEqual(self.store.queue({'state':['decided']})['selected']['reviewed'],1)
        q=self.store.queue({'band':['all'],'sort':['meme']});self.assertEqual(q['items'][0]['sha256'],self.ids[2])
    def test_bad_catalog_and_preview_do_not_replace(self):
        with self.assertRaises(ReviewConflict):self.store.import_items([{**self.items[0],'band':'Likely memes'}])
        with self.assertRaises(ValueError):self.store.import_media('../escape',self.body)
        with self.assertRaises(ValueError):self.store.import_media(self.ids[0],b'\xff\xd8changed\xff\xd9')
        self.assertEqual((self.store.media/(self.ids[0]+'.jpg')).read_bytes(),self.body)
        self.assertEqual(self.store.import_items(self.items)['imported'],3)

if __name__=='__main__':unittest.main()
