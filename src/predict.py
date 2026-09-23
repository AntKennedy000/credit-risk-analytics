"""Inferência local para atributos financeiros completos; sem acesso a serviços."""
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from src.data import ROOT, NUMERIC, PAY, features
from src.metrics import risk_band

def score(frame, bundle):
    missing = set(NUMERIC + PAY) - set(frame.columns)
    if missing:
        raise ValueError(f'Colunas obrigatórias ausentes: {sorted(missing)}')
    if frame.empty:
        raise ValueError('O arquivo precisa conter pelo menos um registro.')
    raw = frame[NUMERIC + PAY].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(raw.to_numpy(dtype=float)).all():
        raise ValueError('Entradas precisam ser números finitos e sem ausentes.')
    if (raw['LIMIT_BAL'] <= 0).any():
        raise ValueError('LIMIT_BAL precisa ser positivo.')
    if not raw[PAY].isin(range(-2,10)).all().all():
        raise ValueError('Estados PAY devem ser inteiros entre -2 e 9.')
    x = features(raw)
    if not np.isfinite(x.to_numpy()).all():
        raise ValueError('Atributos derivados excedem a capacidade numérica.')
    p = bundle['model'].predict_proba(x[bundle['features']])[:, 1]
    return pd.DataFrame({'linha':np.arange(1,len(frame)+1), 'pd_estimada':p,
        'faixa_risco':risk_band(p), 'alerta':(p>=bundle['threshold']).astype(int)})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    model_path=ROOT/'artifacts/modelo.joblib'
    if not model_path.exists():
        parser.error('Execute python -m src.train antes da inferência.')
    if args.input.resolve() == args.output.resolve():
        parser.error('A saída precisa ser diferente do arquivo de entrada.')
    result=score(pd.read_csv(args.input), joblib.load(model_path))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(result.to_string(index=False))

if __name__=='__main__': main()
