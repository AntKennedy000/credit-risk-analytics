"""Métricas e cenários sem custos financeiros inventados."""
import numpy as np
import pandas as pd
from sklearn.metrics import (roc_auc_score, average_precision_score, brier_score_loss,
    log_loss, roc_curve, precision_score, recall_score, f1_score, confusion_matrix)

def evaluate(y, p, threshold=0.5):
    fpr, tpr, _ = roc_curve(y, p)
    auc = roc_auc_score(y, p)
    tn, fp, fn, tp = confusion_matrix(y, p >= threshold, labels=[0, 1]).ravel()
    return dict(roc_auc=float(auc), average_precision=float(average_precision_score(y, p)),
        brier=float(brier_score_loss(y, p)), log_loss=float(log_loss(y, p, labels=[0, 1])),
        ks=float(np.max(tpr - fpr)), gini=float(2 * auc - 1),
        precision=float(precision_score(y, p >= threshold, zero_division=0)),
        recall=float(recall_score(y, p >= threshold, zero_division=0)),
        f1=float(f1_score(y, p >= threshold, zero_division=0)),
        tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp))

def select_threshold(y, p):
    # Fixed grid; selection is exclusively on validation, never on test.
    candidates = np.linspace(0.05, 0.80, 151)
    scores = [f1_score(y, p >= t, zero_division=0) for t in candidates]
    return float(candidates[int(np.argmax(scores))])

def policy_scenarios(y, p):
    y, p = np.asarray(y), np.asarray(p)
    rows = []
    for cutoff in [0.10, 0.20, 0.30, 0.40]:
        eligible = p <= cutoff
        rows.append(dict(limite_pd=cutoff, elegiveis=int(eligible.sum()),
            taxa_elegibilidade=float(eligible.mean()),
            inadimplentes_elegiveis=int(y[eligible].sum()),
            taxa_inadimplencia_elegiveis=float(y[eligible].mean()) if eligible.any() else None,
            pd_media_elegiveis=float(p[eligible].mean()) if eligible.any() else None))
    return pd.DataFrame(rows)

def psi(reference, current):
    # Fixed probability bins. This measures sample distribution differences, not temporal drift.
    edges = np.linspace(0, 1, 11)
    a = np.histogram(reference, edges)[0].astype(float) + 0.5
    b = np.histogram(current, edges)[0].astype(float) + 0.5
    a, b = a/a.sum(), b/b.sum()
    return float(np.sum((b-a)*np.log(b/a)))

def risk_band(probabilities):
    return pd.cut(probabilities, [-np.inf, .10, .20, .40, np.inf],
        labels=['Baixo', 'Moderado', 'Alto', 'Muito alto'], right=True)
