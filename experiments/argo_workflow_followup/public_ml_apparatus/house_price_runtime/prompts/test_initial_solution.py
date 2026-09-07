"""Mock-only starter API test. No real estimator fit or task data."""
from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd
import initial_solution


class InitialSolutionTest(unittest.TestCase):
    def test_training_only_pipeline_and_original_prediction_order(self):
        columns=initial_solution.FEATURES
        train=pd.DataFrame({name:[1,2,3] for name in columns})
        train["Id"]=[10,11,12]
        train["SalePrice"]=[100,200,300]
        features=pd.DataFrame({name:[4,5] for name in columns})
        features["Id"]=[20,21]
        seen={}
        class SpyPipeline:
            def __init__(self,steps):seen["steps"]=steps
            def fit(self,x,y):
                seen["fit_columns"]=list(x.columns);seen["fit_rows"]=len(x)
                seen["fit_targets"]=list(y);return self
            def predict(self,x):
                seen["predict_columns"]=list(x.columns);seen["predict_rows"]=len(x)
                return [250.0,150.0]
        with patch.object(initial_solution,"Pipeline",SpyPipeline):
            result=initial_solution.fit_predict(train,features)
        self.assertEqual(result,[250.0,150.0])
        self.assertEqual(seen["fit_rows"],3);self.assertEqual(seen["predict_rows"],2)
        self.assertEqual(seen["fit_targets"],[100,200,300])
        self.assertEqual(seen["fit_columns"],columns);self.assertEqual(seen["predict_columns"],columns)
        self.assertEqual(list(features["Id"]),[20,21])
        self.assertEqual(seen["steps"][0][1].strategy,"median")
        self.assertEqual(seen["steps"][1][1].n_estimators,100)
        self.assertEqual(seen["steps"][1][1].random_state,1)
        self.assertEqual(seen["steps"][1][1].n_jobs,1)

if __name__=="__main__":unittest.main(verbosity=2)
