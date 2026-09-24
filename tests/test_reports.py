"""Regressões de apresentação para cenários sem clientes elegíveis."""
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import numpy as np

from src.data import ROOT
from src.metrics import policy_scenarios
from src.report import render_dashboard, render_markdown, render_reports


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.summary = json.loads((ROOT / 'reports/resumo.json').read_text(encoding='utf-8'))
        self.validation = pd.read_csv(ROOT / 'reports/comparacao_validacao.csv')

    def test_dashboard_serializes_empty_scenarios_as_null(self):
        for probabilities in ([.15, .9], [.9, .9]):
            with self.subTest(probabilities=probabilities):
                scenarios = policy_scenarios([0, 1], probabilities)
                with tempfile.TemporaryDirectory(dir=ROOT / 'artifacts') as folder:
                    path = Path(folder)
                    (path / 'reports').mkdir()
                    with patch('src.report.ROOT', path):
                        render_dashboard(self.summary, self.validation, None, scenarios)
                    content = (path / 'reports/painel.html').read_text(encoding='utf-8')
                    payload = re.search(r'const scenarios=(.*?);const select=', content).group(1)
                    records = json.loads(payload)
                    self.assertNotIn('NaN', payload)
                    self.assertEqual(records[0]['elegiveis'], 0)
                    self.assertIsNone(records[0]['taxa_inadimplencia_elegiveis'])
                    if probabilities[0] == .15:
                        self.assertEqual(records[1]['elegiveis'], 1)
                        self.assertEqual(records[1]['taxa_inadimplencia_elegiveis'], 0)

    def test_markdown_distinguishes_no_clients_from_zero_defaults(self):
        for probabilities in ([.15, .9], [.9, .9]):
            with self.subTest(probabilities=probabilities):
                with tempfile.TemporaryDirectory(dir=ROOT / 'artifacts') as folder:
                    path = Path(folder)
                    (path / 'reports').mkdir()
                    with patch('src.report.ROOT', path):
                        render_markdown(self.summary, self.validation,
                                        policy_scenarios([0, 1], probabilities))
                    content = (path / 'reports/resultados.md').read_text(encoding='utf-8')
                    self.assertIn('| 10% | 0 | 0.00% | Sem elegíveis |', content)
                    self.assertNotIn('nan%', content)
                    if probabilities[0] == .15:
                        self.assertIn('| 20% | 1 | 50.00% | 0.00% |', content)

    def test_full_report_renders_when_no_cutoff_has_clients(self):
        y, p = np.array([0, 1]), np.array([.9, .9])
        bands = pd.DataFrame({'faixa_risco':['Muito alto'],
                              'pd_media':[.9], 'taxa_inadimplencia':[.5]})
        importance = pd.DataFrame({'variavel':['exemplo'],
                                  'importancia_media':[.1], 'desvio':[0.]})
        with tempfile.TemporaryDirectory(dir=ROOT / 'artifacts') as folder:
            path = Path(folder)
            (path / 'reports').mkdir()
            (path / 'evidencias').mkdir()
            with patch('src.report.ROOT', path):
                render_reports(self.summary, self.validation, bands,
                               policy_scenarios(y, p), importance, y, p)
            self.assertEqual(len(list((path / 'evidencias').glob('*.png'))), 3)
            self.assertTrue((path / 'reports/painel.html').exists())
            content = (path / 'reports/resultados.md').read_text(encoding='utf-8')
            self.assertEqual(content.count('Sem elegíveis'), 4)


if __name__ == '__main__':
    unittest.main()
