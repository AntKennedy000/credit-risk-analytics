"""Origem pública, validação e atributos observáveis antes do desfecho."""
from pathlib import Path
import hashlib
import io
import urllib.request
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://archive.ics.uci.edu/static/public/350/default%2Bof%2Bcredit%2Bcard%2Bclients.zip'
SOURCE = 'https://doi.org/10.24432/C55S3H'
TARGET = 'default payment next month'
PAY = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
NUMERIC = ['LIMIT_BAL'] + [f'BILL_AMT{i}' for i in range(1, 7)] + [f'PAY_AMT{i}' for i in range(1, 7)]
DERIVED = ['utilizacao_limite', 'pagamento_sobre_fatura', 'meses_com_atraso', 'maior_atraso']
FEATURES = NUMERIC + PAY + DERIVED

def load_data():
    path = ROOT / 'data/raw/uci_credit.zip'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        request = urllib.request.Request(URL, headers={'User-Agent': 'CreditRiskAnalytics/1.0'})
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read()
        # Validate in memory before writing a complete archive to disk.
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            if not any(name.endswith('.xls') for name in archive.namelist()):
                raise ValueError('Arquivo UCI não contém a planilha esperada.')
        path.write_bytes(payload)
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.endswith('.xls')]
        if len(names) != 1:
            raise ValueError('Esperada uma planilha de origem.')
        frame = pd.read_excel(io.BytesIO(archive.read(names[0])), header=1, engine='xlrd')
    validate_data(frame)
    return frame, hashlib.sha256(path.read_bytes()).hexdigest()

def validate_data(frame):
    required = ['ID', TARGET] + NUMERIC + PAY
    if not set(required).issubset(frame.columns):
        raise ValueError('Esquema de dados inesperado.')
    if frame[required].isna().any().any():
        raise ValueError('Valores ausentes na origem; audite antes de treinar.')
    if not frame['ID'].is_unique:
        raise ValueError('IDs repetidos na origem.')
    if set(frame[TARGET].unique()) != {0, 1}:
        raise ValueError('Desfecho deve conter as duas classes binárias.')
    if (frame['LIMIT_BAL'] <= 0).any():
        raise ValueError('Limite precisa ser positivo.')
    if not np.isfinite(frame[NUMERIC + PAY].to_numpy(dtype=float)).all():
        raise ValueError('Valores numéricos não finitos.')

def features(frame):
    result = frame[NUMERIC + PAY].copy()
    result['utilizacao_limite'] = frame['BILL_AMT1'] / frame['LIMIT_BAL']
    # Negative or zero bills are not a valid denominator; zero ratio is an explicit convention.
    result['pagamento_sobre_fatura'] = np.divide(
        frame['PAY_AMT1'], frame['BILL_AMT1'],
        out=np.zeros(len(frame), dtype=float), where=frame['BILL_AMT1'].to_numpy() > 0)
    result['meses_com_atraso'] = (frame[PAY] > 0).sum(axis=1)
    result['maior_atraso'] = frame[PAY].clip(lower=0).max(axis=1)
    return result[FEATURES]
