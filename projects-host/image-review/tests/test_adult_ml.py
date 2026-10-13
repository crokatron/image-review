import copy,json,math,unittest,uuid
import test_review as fixtures
from image_review import ImageReview,ReviewConflict,ADULT_MODEL,ADULT_MODEL_REVISION

class AdultMLTests(unittest.TestCase):
    setUp=fixtures.ReviewTests.setUp
    tearDown=fixtures.ReviewTests.tearDown
    def batch(self,scores=(.98,.45,.03)):
        return {'model':ADULT_MODEL,'model_revision':ADULT_MODEL_REVISION,'items':[{'sha256':h,'media_sha':self.items[i]['media_sha'],'score':score} for i,(h,score) in enumerate(zip(self.ids,scores))]}
    def test_machine_filters_sort_and_persistence(self):
        result=self.store.import_adult_predictions(self.batch())
        self.assertEqual(result['stats']['scored'],3)
        other=ImageReview(self.temp.name)
        q=other.queue({'band':['all'],'mode':['adult'],'adult_ml':['flagged'],'sort':['adult']})
        self.assertEqual(q['queue_count'],2);self.assertEqual([r['sha256'] for r in q['items']],self.ids[:2]);self.assertEqual(q['items'][0]['adult_prediction']['band'],'likely_adult')
        for band,i in (('likely_adult',0),('uncertain',1),('likely_safe',2)):
            q=other.queue({'band':['all'],'adult_ml':[band]});self.assertEqual(q['queue_count'],1);self.assertEqual(q['items'][0]['sha256'],self.ids[i])
        self.assertEqual(other.queue({'band':['all'],'adult_ml':['unscored']})['queue_count'],0)
    def test_no_manual_labels_or_tags_modified_and_corrections_override_review(self):
        self.store.annotate('adult',{'op':str(uuid.uuid4()),'sha256':self.ids[2],'revision':0,'value':{'state':'adult'}},'owner')
        before=json.loads(self.store.export('json')[0]);self.store.import_adult_predictions(self.batch());after=json.loads(self.store.export('json')[0])
        for field in ('items','events','annotations','annotation_events','people'):self.assertEqual(before[field],after[field])
        q=self.store.queue({'band':['all'],'mode':['adult'],'adult_state':['adult'],'adult_ml':['all']})
        self.assertEqual(q['items'][0]['sha256'],self.ids[2]);self.assertEqual(q['items'][0]['adult_prediction']['band'],'likely_safe')
        self.assertEqual(q['items'][0]['adult_review']['state'],'adult')
    def test_idempotent_and_atomic_rejection(self):
        batch=self.batch();self.store.import_adult_predictions(batch);self.store.import_adult_predictions(batch)
        changed=copy.deepcopy(batch);changed['items'][0]['score']=.1
        with self.assertRaises(ReviewConflict):self.store.import_adult_predictions(changed)
        self.assertEqual(self.store.queue({'band':['all'],'adult_ml':['likely_adult']})['items'][0]['adult_prediction']['score'],.98)
    def test_bad_scores_revisions_and_hashes(self):
        for score in (-1,2,float('nan'),float('inf'),True):
            batch=self.batch();batch['items'][0]['score']=score
            with self.assertRaises(ValueError):self.store.import_adult_predictions(batch)
        batch=self.batch();batch['items'][-1]['media_sha']='f'*64
        with self.assertRaises(ValueError):self.store.import_adult_predictions(batch)
        self.assertEqual(self.store.queue({'band':['all']})['adult_ml']['scored'],0)
        batch=self.batch();batch['model_revision']='bad'
        with self.assertRaises(ValueError):self.store.import_adult_predictions(batch)
        with self.assertRaises(ValueError):self.store.queue({'adult_ml':["x' OR 1=1"]})
    def test_boundary_bands(self):
        self.store.import_adult_predictions(self.batch((.85,.15,.150001)))
        stats=self.store.queue({'band':['all']})['adult_ml']
        self.assertEqual((stats['likely_adult'],stats['likely_safe'],stats['uncertain']),(1,1,1))

if __name__=='__main__':unittest.main()
