import hashlib,json,sys,tempfile,unittest,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'host'))
from image_review import ImageReview

class LearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=ImageReview(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def populate(self,perfect_original=False):
        db=self.store.connect()
        for i in range(300):
            label='meme' if i%2 else 'not_meme'
            score=(2 if label=='meme' else -2) if perfect_original else (3 if label=='meme' else 1)
            ident=hashlib.sha256(str(i).encode()).hexdigest()
            db.execute('INSERT INTO items(sha256,band,score,subtype,width,height,media_sha,media_size,ready,label,revision) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(ident,'Borderline',score,'Photo',100,100,ident,10,1,label,1))
        db.commit();db.close()
    def test_minimum_skip_and_undo_exclusion(self):
        self.assertFalse(self.store.train()['eligible'])
        self.populate();db=self.store.connect();db.execute("UPDATE items SET label='skip' WHERE label='meme'");db.commit();db.close()
        self.assertFalse(self.store.train()['eligible'])
    def test_activation_persistence_predictions_and_correction(self):
        self.populate();result=self.store.train();self.assertTrue(result['active'])
        self.assertEqual(result['model']['threshold'],2)
        self.assertEqual(result['model']['holdout_count'],60)
        other=ImageReview(self.tmp.name);self.assertTrue(other.learning_status()['active'])
        future={'score_schema':'mungoon-refinement-rank-v1','items':[{'sha256':'f'*64,'score':1.5}]}
        self.assertEqual(other.predict(future)['items'][0]['suggestion'],'not_meme')
        existing=hashlib.sha256(b'1').hexdigest()
        future['items']=[{'sha256':existing,'score':-20}]
        self.assertEqual(other.predict(future)['items'][0]['source'],'your_decision')
        receipt=other.decide({'op':str(uuid.uuid4()),'sha256':existing,'label':'not_meme','revision':1},'owner')
        self.assertFalse(other.learning_status()['active'])
        other.undo({'op':str(uuid.uuid4()),'event':receipt['event']},'owner')
        self.assertTrue(other.learning_status()['active'])
    def test_rejected_model_and_bad_inputs(self):
        self.populate(True);result=self.store.train();self.assertFalse(result['active'])
        self.assertFalse(result['model']['accepted'])
        for score in (float('nan'),float('inf'),True,101):
            with self.assertRaises(ValueError):self.store.predict({'score_schema':'mungoon-refinement-rank-v1','items':[{'sha256':'a'*64,'score':score}]})
        with self.assertRaises(ValueError):self.store.predict({'score_schema':'other','items':[]})
    def test_training_does_not_change_catalog_decisions_or_history(self):
        self.populate();before=self.store.export('json')[0];self.store.train();after=self.store.export('json')[0]
        a,b=json.loads(before),json.loads(after);self.assertEqual(a['items'],b['items']);self.assertEqual(a['events'],b['events'])
    def test_threshold_ties_and_heldout_separation(self):
        self.populate();r=self.store.train()['model'];self.assertEqual(r['training_count']+r['holdout_count'],300)
        rows=[{'score':0,'label':'meme'},{'score':0,'label':'not_meme'}]
        self.assertEqual(self.store.fit_threshold(rows),0)

if __name__=='__main__':unittest.main()
