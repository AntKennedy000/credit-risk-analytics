import unittest
import numpy as np
import pandas as pd
from src.data import features, validate_data, TARGET, NUMERIC, PAY, FEATURES
from src.metrics import evaluate, select_threshold, policy_scenarios, psi, risk_band
from src.train import split_data
from src.predict import score

class MockModel:
    def predict_proba(self, x):
        return np.tile([.8,.2],(len(x),1))

class PipelineTests(unittest.TestCase):
    def fixture(self):
        frame = pd.DataFrame({c:[100.,200.] for c in NUMERIC+PAY})
        frame['ID']=[1,2]; frame[TARGET]=[0,1]
        frame['BILL_AMT1']=[0,-100]; frame[PAY]=0
        return frame

    def test_features_no_future_target_or_identifier(self):
        frame=self.fixture(); x=features(frame)
        self.assertEqual(list(x.columns), FEATURES)
        self.assertNotIn('ID',x); self.assertNotIn(TARGET,x)
        self.assertTrue(np.isfinite(x.to_numpy()).all())
        self.assertEqual(x.pagamento_sobre_fatura.tolist(),[0,0])

    def test_data_contract(self):
        frame=self.fixture(); validate_data(frame)
        frame.loc[0,'LIMIT_BAL']=0
        with self.assertRaises(ValueError): validate_data(frame)

    def test_duplicate_inputs_do_not_leak(self):
        x=pd.DataFrame({'a':np.repeat(np.arange(200),2)})
        y=pd.Series(np.tile([0,1],200))
        train,val,test,groups=split_data(x,y)
        self.assertEqual(len(set(train)|set(val)|set(test)),len(x))
        for a,b in [(train,val),(train,test),(val,test)]:
            self.assertFalse(set(groups[a]) & set(groups[b]))

    def test_perfect_predictions(self):
        result=evaluate([0,0,1,1],np.array([0.,0.,1.,1.]))
        self.assertEqual(result['roc_auc'],1)
        self.assertEqual(result['ks'],1)
        self.assertEqual(result['brier'],0)
        self.assertEqual(result['tp'],2)

    def test_policy_boundaries_and_empty_population(self):
        table=policy_scenarios([0,1,1],np.array([.1,.2,.5]))
        self.assertEqual(table.elegiveis.tolist(),[1,2,2,2])
        self.assertEqual(table.iloc[1].taxa_inadimplencia_elegiveis,.5)
        self.assertEqual(policy_scenarios([1],[.9]).elegiveis.sum(),0)
        self.assertEqual(list(risk_band([.1,.2,.4,.5])),['Baixo','Moderado','Alto','Muito alto'])

    def test_psi_identity_and_extreme_probabilities(self):
        values=np.array([0,.1,.5,1])
        self.assertEqual(psi(values,values),0)
        self.assertTrue(np.isfinite(psi(np.zeros(10),np.ones(10))))

    def test_threshold_uses_supplied_validation(self):
        threshold=select_threshold([0,0,1,1],np.array([.1,.2,.4,.5]))
        self.assertTrue(.2<threshold<=.4)

    def test_inference_rejects_invalid_input(self):
        bundle={'model':MockModel(),'features':FEATURES,'threshold':.2}
        frame=self.fixture()
        self.assertEqual(score(frame,bundle).alerta.tolist(),[1,1])
        with self.assertRaises(ValueError): score(frame.drop(columns=['LIMIT_BAL']),bundle)
        frame.loc[0,'PAY_0']=99
        with self.assertRaises(ValueError): score(frame,bundle)
        frame=self.fixture(); frame.loc[0,'BILL_AMT2']=float('inf')
        with self.assertRaises(ValueError): score(frame,bundle)

if __name__=='__main__': unittest.main()
