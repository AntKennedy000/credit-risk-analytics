"""Verificações de integração quando os artefatos locais estão disponíveis."""
import json
import sqlite3
import unittest
import numpy as np
import pandas as pd
import joblib
from src.data import ROOT, load_data, features
from src.metrics import evaluate

@unittest.skipUnless((ROOT/'artifacts/modelo.joblib').exists(), 'Execute o treino para validar os artefatos locais.')
class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary=json.loads((ROOT/'reports/resumo.json').read_text(encoding='utf-8'))
        cls.predictions=pd.read_csv(ROOT/'data/processed/carteira_teste.csv')

    def test_sql_matches_predictions(self):
        with sqlite3.connect(ROOT/'artifacts/carteira.db') as connection:
            sql=pd.read_sql_query((ROOT/'sql/indicadores.sql').read_text(encoding='utf-8'),connection)
        self.assertEqual(sql.clientes.sum(),len(self.predictions))
        self.assertEqual(sql.inadimplentes.sum(),self.predictions.inadimplente.sum())
        saved=pd.read_csv(ROOT/'reports/faixas_risco.csv')
        pd.testing.assert_frame_equal(sql,saved,check_exact=False,rtol=1e-10)

    def test_saved_metrics_are_recomputed(self):
        actual=evaluate(self.predictions.inadimplente,self.predictions.pd_estimada,self.summary['limiar_alerta'])
        for name,value in actual.items():
            self.assertAlmostEqual(value,self.summary['teste'][name],places=10)

    def test_persisted_model_reproduces_test_predictions(self):
        frame, checksum=load_data()
        self.assertEqual(checksum,self.summary['sha256_origem'])
        ordered=frame.set_index('ID').loc[self.predictions.id]
        model=joblib.load(ROOT/'artifacts/modelo.joblib')['model']
        actual=model.predict_proba(features(ordered))[:,1]
        np.testing.assert_allclose(actual,self.predictions.pd_estimada,atol=1e-12)

    def test_persisted_partitions_have_no_feature_overlap(self):
        frame,_=load_data()
        partitions=pd.read_csv(ROOT/'data/processed/particoes.csv').set_index('id')
        self.assertEqual(len(partitions),len(frame))
        self.assertTrue(partitions.index.is_unique)
        hashes=pd.util.hash_pandas_object(features(frame),index=False)
        labels=frame.ID.map(partitions.particao)
        sets={name:set(hashes[labels==name]) for name in ['treino','validacao','teste']}
        self.assertFalse(sets['treino'] & sets['validacao'])
        self.assertFalse(sets['treino'] & sets['teste'])
        self.assertFalse(sets['teste'] & sets['validacao'])

if __name__=='__main__': unittest.main()
