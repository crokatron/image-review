import json,uuid,unittest,hashlib
import test_review as fixtures
from image_review import ImageReview,ReviewConflict

class AnnotationTests(unittest.TestCase):
    setUp=fixtures.ReviewTests.setUp
    tearDown=fixtures.ReviewTests.tearDown
    def person(self,name='Alex'):
        return self.store.create_person({'op':str(uuid.uuid4()),'name':name})['id']
    def payload(self,channel='people',i=0,revision=0,value=None):
        return {'op':str(uuid.uuid4()),'sha256':self.ids[i],'revision':revision,'value':value or ({'state':'tagged','people':[self.person()],'other':False} if channel=='people' else {'state':'adult'})}
    def test_independent_labels_reopen_and_export(self):
        person=self.person();p=self.payload(value={'state':'tagged','people':[person],'other':True})
        event=self.store.annotate('people',p,'owner')
        self.store.annotate('adult',self.payload('adult'),'owner')
        self.store.decide({'op':str(uuid.uuid4()),'sha256':self.ids[0],'label':'not_meme','revision':0},'owner')
        other=ImageReview(self.temp.name);item=other.queue({'band':['all'],'state':['decided']})['items'][0]
        self.assertEqual(item['people_review']['people'],[person]);self.assertEqual(item['adult_review']['state'],'adult');self.assertEqual(item['label'],'not_meme')
        other.annotate('people',{'op':str(uuid.uuid4()),'event':event['event']},'owner',undo=True)
        item=other.queue({'band':['all'],'state':['decided']})['items'][0]
        self.assertIsNone(item['people_review']['state']);self.assertEqual(item['adult_review']['state'],'adult');self.assertEqual(item['label'],'not_meme')
        doc=json.loads(other.export('json')[0]);self.assertEqual(len(doc['events']),1);self.assertEqual(len(doc['annotation_events']),3);self.assertEqual(doc['people'][0]['name'],'Alex')
    def test_combined_filters_and_tag_first_ignore_meme_labels(self):
        a=self.person();b=self.person('Sam')
        for i,ids in enumerate(([a],[a,b],[])):
            self.store.annotate('people',self.payload(i=i,value={'state':'tagged' if ids else 'none','people':ids,'other':i==1}),'owner')
        self.store.annotate('adult',self.payload('adult',i=1),'owner')
        q={'band':['priority'],'person':[a],'people_state':['tagged'],'mode':['meme']}
        self.assertEqual(self.store.queue(q)['queue_count'],2)
        q['adult_state']=['adult'];self.assertEqual(self.store.queue(q)['queue_count'],1)
        self.assertEqual(self.store.queue({'band':['all'],'people_state':['other']})['queue_count'],1)
        self.store.decide({'op':str(uuid.uuid4()),'sha256':self.ids[0],'label':'meme','revision':0},'owner')
        self.assertEqual(self.store.queue({'band':['all'],'mode':['people'],'person':[a]})['queue_count'],2)
        self.assertEqual(self.store.queue({'band':['all'],'mode':['people'],'people_state':['unreviewed']})['queue_count'],0)
    def test_retry_stale_revision_and_wrong_channel_undo(self):
        p=self.payload();event=self.store.annotate('people',p,'owner')
        self.assertTrue(self.store.annotate('people',p,'owner')['replayed'])
        with self.assertRaises(ReviewConflict):self.store.annotate('people',{**p,'value':{'state':'none','people':[],'other':False}},'owner')
        with self.assertRaises(ReviewConflict):self.store.annotate('people',self.payload(),'owner')
        with self.assertRaises(ValueError):self.store.annotate('adult',{'op':str(uuid.uuid4()),'event':event['event']},'owner',undo=True)
        self.store.annotate('people',self.payload(revision=1,value={'state':'none','people':[],'other':False}),'owner')
        with self.assertRaises(ReviewConflict):self.store.annotate('people',{'op':str(uuid.uuid4()),'event':event['event']},'owner',undo=True)
    def test_name_dedup_and_validation(self):
        value={'op':str(uuid.uuid4()),'name':' Alex '};a=self.store.create_person(value)
        self.assertEqual(self.store.create_person({'op':str(uuid.uuid4()),'name':'alex'})['id'],a['id'])
        with self.assertRaises(ReviewConflict):self.store.create_person({**value,'name':'Other'})
        for name in ('','x'*65,'bad\nname'):
            with self.assertRaises(ValueError):self.person(name)
        for v in ({'state':'none','people':[a['id']],'other':False},{'state':'tagged','people':[],'other':False},{'state':'tagged','people':[str(uuid.uuid4())],'other':False}):
            with self.assertRaises(ValueError):self.store.annotate('people',self.payload(value=v),'owner')
    def test_extra_library_does_not_train_meme_cutoff(self):
        extra={**self.items[0],'sha256':hashlib.sha256(b'library').hexdigest(),'band':'Photos','score':0}
        self.store.import_items([extra]);self.store.import_media(extra['sha256'],self.body)
        self.store.decide({'op':str(uuid.uuid4()),'sha256':extra['sha256'],'label':'meme','revision':0},'owner')
        self.assertEqual(self.store.learning_status()['counts'],{})
        self.assertEqual(self.store.queue({'band':['Photos'],'state':['decided']})['queue_count'],1)
    def test_malicious_filters_and_payloads(self):
        for q in ({'person':["x' OR 1=1"]},{'adult_state':['bad']},{'mode':['bad']}):
            with self.assertRaises(ValueError):self.store.queue(q)
        with self.assertRaises(ValueError):self.store.annotate('adult',self.payload('adult',value={'state':'anything'}),'owner')

if __name__=='__main__':unittest.main()
