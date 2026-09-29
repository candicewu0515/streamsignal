import unittest,sys,pathlib,json,csv,copy
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import train_multihazard as model
class MultiHazardTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=model.base.load_data();cls.result=json.loads((ROOT/'results/multihazard_metrics.json').read_text())
  with (ROOT/'results/multihazard_predictions.csv').open(encoding='utf-8-sig') as f:cls.pred=list(csv.DictReader(f))
 def test_future_window_and_compound_definition(self):
  window=[[0,0,31,0,0,0,0,0,0,0] for _ in range(3)];self.assertEqual(model.label(window,'compound',3),1)
  window[1][4]=3;self.assertEqual(model.label(window,'compound',3),0);self.assertEqual(model.label(window,'dry',3),0)
  window[1][4]=20;self.assertEqual(model.label(window,'rain',3),1)
 def test_features_are_causal(self):
  data={'dates':self.data['dates'][:20],'series':[[x[:] for x in self.data['series'][0][:20]]]}
  for h in [3,7]:
   before=model.build(data,h,'rain')[0];altered=copy.deepcopy(data);altered['series'][0][7][4]=900
   after=model.build(altered,h,'rain')[0];np.testing.assert_array_equal(before['features'],after['features']);self.assertNotEqual(before['rain'],after['rain'])
 def test_split_windows_never_cross_year_boundaries(self):
  for h in [3,7]:
   split=model.splits(model.build(self.data,h,'rain'))
   for key,lo,hi in [('train','2023-01-01','2024-12-31'),('validation','2025-01-01','2025-12-31'),('test','2026-01-01','2026-09-21')]:
    self.assertTrue(all(lo<=r['targetDate']<=r['endDate']<=hi for r in split[key]));self.assertEqual(len(split[key]),self.result['tasks'][f'rain_{h}']['split'][key]['n'])
 def test_every_exported_task_metric_recomputes(self):
  self.assertEqual(len(self.pred),39648)
  for key,t in self.result['tasks'].items():
   rows=[r for r in self.pred if r['task']==key];self.assertEqual(len({(r['weatherGroup'],r['issueDate']) for r in rows}),len(rows))
   y=np.array([int(r['event']) for r in rows]);p=np.array([float(r['probability']) for r in rows]);m=t['metrics']['test'][t['selected']]
   self.assertTrue(np.all((p>=0)&(p<=1)))
   for name,value in model.base.metrics(y,p,m['threshold']).items():self.assertAlmostEqual(value,m[name],places=12)
   self.assertEqual(sum(b['count'] for b in t['reliability']),len(rows));self.assertEqual(sum(m['n'] for m in t['monthly']),len(rows))
 def test_candidate_selection_uses_only_validation(self):
  for t in self.result['tasks'].values():self.assertEqual(t['selected'],min(['logistic','boosted'],key=lambda k:t['metrics']['validation'][k]['brier']))
 def test_geographic_fold_excludes_city(self):
  for row in self.result['geographic']:self.assertNotIn(row['city'],row['trainingCities']);self.assertEqual(len(row['trainingCities']),4)
 def test_missing_day_removes_any_affected_target_window(self):
  for h in [3,7]:
   rows=model.build(self.data,h,'rain')
   for r in rows:
    for gap in ['2026-08-04','2026-08-27']:self.assertFalse(r['targetDate']<=gap<=r['endDate'])
if __name__=='__main__':unittest.main()
