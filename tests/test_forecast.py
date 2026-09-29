"""Independent checks for temporal features and exported model predictions."""
import unittest, importlib.util, pathlib, json, datetime as dt, csv, copy
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('forecast',ROOT/'tools/train_forecast.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=f.load_data();cls.rows=f.build_rows(cls.data)
        cls.result=json.loads((ROOT/'results/forecast_metrics.json').read_text())
        with (ROOT/'results/forecast_test_predictions.csv').open(encoding='utf-8-sig') as file:cls.pred=list(csv.DictReader(file))
    def test_future_weather_never_enters_features(self):
        data={'dates':self.data['dates'][:8],'series':[[r[:] for r in self.data['series'][0][:8]]]}
        before=f.build_rows(data)[0];data['series'][0][3]=[999.]*10
        after=f.build_rows(data)[0]
        np.testing.assert_array_equal(before['features'],after['features'])
        self.assertEqual(after['label'],1);self.assertEqual(after['targetRain'],999)
    def test_missing_feature_or_target_excludes_all_affected_targets(self):
        dates=[(dt.date(2026,1,1)+dt.timedelta(days=i)).isoformat() for i in range(12)]
        data={'dates':dates,'series':[[[1.]*10 for _ in dates]]};data['series'][0][5]=[None]*10
        targets={r['targetDate'] for r in f.build_rows(data)}
        self.assertFalse(targets.intersection(dates[5:9]));self.assertIn(dates[9],targets)
    def test_target_based_splits_and_gap_counts(self):
        for key,lo,hi,n in [('train','2023-01-01','2024-12-31',15288),('validation','2025-01-01','2025-12-31',7665),('test','2026-01-01','2026-09-21',5376)]:
            selected=[r for r in self.rows if lo<=r['targetDate']<=hi]
            self.assertEqual(len(selected),n);self.assertEqual(len({(r['group'],r['targetDate']) for r in selected}),n)
            for r in selected:self.assertEqual((dt.date.fromisoformat(r['targetDate'])-dt.date.fromisoformat(r['issueDate'])).days,1)
    def test_scaler_fitted_only_to_training(self):
        X=np.array([r['features'] for r in self.rows if r['targetDate']<='2024-12-31'])
        np.testing.assert_allclose(X.mean(axis=0),self.result['model']['means'],rtol=1e-12)
        np.testing.assert_allclose(X.std(axis=0),self.result['model']['scales'],rtol=1e-12)
    def test_exported_probabilities_reproduce_model_parameters(self):
        X=np.array([r['features'] for r in self.rows if r['targetDate']>='2026-01-01']);m=self.result['model']
        z=((X-np.array(m['means']))/np.array(m['scales']))@np.array(m['coefficients'])+m['intercept']
        p=1/(1+np.exp(-z));np.testing.assert_allclose(p,[float(r['modelProbability']) for r in self.pred],atol=1e-12)
        self.assertTrue(np.all((p>=0)&(p<=1)))
    def test_test_metrics_recompute_from_export(self):
        y=np.array([int(r['event']) for r in self.pred]);p=np.array([float(r['modelProbability']) for r in self.pred])
        recomputed=f.metrics(y,p,self.result['validation']['logistic']['threshold'])
        for k,v in recomputed.items():self.assertAlmostEqual(v,self.result['test']['logistic'][k],places=12)
    def test_model_selection_uses_validation_brier(self):
        choice=min(self.result['candidates'],key=lambda c:(c['validationBrier'],c['C']))
        self.assertEqual(choice['C'],self.result['selectedC'])
        for key in self.result['test']:self.assertEqual(self.result['test'][key]['threshold'],self.result['validation'][key]['threshold'])
    def test_all_bin_and_month_counts_reconcile(self):
        for bins in self.result['reliability'].values():self.assertEqual(sum(b['count'] for b in bins),5376)
        self.assertEqual(sum(m['n'] for m in self.result['monthly']),5376)
        self.assertEqual(sum(m['events'] for m in self.result['monthly']),394)
    def test_seasonal_baseline_uses_training_labels_only(self):
        training=[r for r in self.rows if r['targetDate']<='2024-12-31'];test=[r for r in self.rows if r['targetDate']>='2026-01-01']
        p=f.seasonal_prob(training,test);np.testing.assert_allclose(p,[float(r['seasonalProbability']) for r in self.pred],atol=1e-12)
        changed=[{**r,'label':1-r['label']} for r in test[:21]]
        np.testing.assert_array_equal(f.seasonal_prob(training,changed),p[:21])
    def test_reliability_includes_probability_one(self):
        bins=f.reliability(np.array([0,1]),np.array([0.,1.]));self.assertEqual(bins[0]['count'],1);self.assertEqual(bins[-1]['count'],1)

if __name__=='__main__':unittest.main(verbosity=2)
