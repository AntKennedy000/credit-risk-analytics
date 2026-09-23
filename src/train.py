"""Execute na raiz: python -m src.train. Resultados regeneráveis em reports/."""
import json
import platform
import sqlite3
from datetime import datetime, timezone
from importlib.metadata import version
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier
from src.data import ROOT, FEATURES, PAY, NUMERIC, DERIVED, TARGET, SOURCE, load_data, features
from src.metrics import evaluate, select_threshold, policy_scenarios, psi, risk_band

SEED = 42

def split_data(x, y):
    # Identical model inputs stay together even when ID or demographics differ.
    groups = pd.util.hash_pandas_object(x, index=False).to_numpy()
    folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED).split(x, y, groups))
    test, validation = folds[0][1], folds[1][1]
    train = np.setdiff1d(np.arange(len(x)), np.concatenate([test, validation]))
    return train, validation, test, groups

def build_models(x_train, y_train, groups):
    preprocessing = ColumnTransformer([
        ('numericas', StandardScaler(), NUMERIC + DERIVED),
        ('historico', OneHotEncoder(handle_unknown='ignore'), PAY)])
    logistic = Pipeline([('preparo', preprocessing),
        ('modelo', LogisticRegression(C=1.0, max_iter=3000, random_state=SEED))])
    xgb = XGBClassifier(n_estimators=180, max_depth=3, learning_rate=.05,
        subsample=.85, colsample_bytree=.85, reg_lambda=5,
        objective='binary:logistic', eval_metric='logloss', tree_method='hist',
        random_state=SEED, n_jobs=2)
    cv = list(StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
        .split(x_train, y_train, groups))
    return {'Referencia': DummyClassifier(strategy='prior'), 'Regressao Logistica': logistic,
        'XGBoost calibrado': CalibratedClassifierCV(xgb, method='sigmoid', cv=cv)}

def main():
    for folder in ['reports', 'evidencias', 'artifacts', 'data/processed']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    frame, checksum = load_data()
    x, y = features(frame), frame[TARGET]
    train, val, test, groups = split_data(x, y)
    for a, b in [(train, val), (train, test), (val, test)]:
        assert not set(groups[a]).intersection(groups[b]), 'Vazamento entre partições'
    models = build_models(x.iloc[train], y.iloc[train], groups[train])
    validation_results, fitted = [], {}
    for name, model in models.items():
        print(f'Treinando: {name}', flush=True)
        model.fit(x.iloc[train], y.iloc[train])
        prediction = model.predict_proba(x.iloc[val])[:, 1]
        validation_results.append({'modelo': name, **evaluate(y.iloc[val], prediction)})
        fitted[name] = model
    validation_table = pd.DataFrame(validation_results).sort_values(['brier', 'modelo'])
    selected = validation_table.iloc[0]['modelo']
    model = fitted[selected]
    pv = model.predict_proba(x.iloc[val])[:, 1]
    threshold = select_threshold(y.iloc[val], pv)
    # All model/threshold choices are now frozen before looking at the test outcomes.
    pt = model.predict_proba(x.iloc[test])[:, 1]
    test_metrics = evaluate(y.iloc[test], pt, threshold)
    print(f'Modelo selecionado na validação: {selected}', flush=True)
    print(f'Resultado reservado: {json.dumps(test_metrics)}', flush=True)
    predictions = pd.DataFrame({'id': frame.iloc[test]['ID'].to_numpy(),
        'pd_estimada': pt, 'inadimplente': y.iloc[test].to_numpy(),
        'faixa_risco': risk_band(pt), 'limite_ntd': frame.iloc[test]['LIMIT_BAL'].to_numpy(),
        'alerta': (pt >= threshold).astype(int)})
    predictions.to_csv(ROOT/'data/processed/carteira_teste.csv', index=False)
    validation_table.to_csv(ROOT/'reports/comparacao_validacao.csv', index=False)
    scenarios = policy_scenarios(y.iloc[test], pt)
    scenarios.to_csv(ROOT/'reports/cenarios_teste.csv', index=False)
    policies_val = policy_scenarios(y.iloc[val], pv)
    policies_val.to_csv(ROOT/'reports/cenarios_validacao.csv', index=False)
    with sqlite3.connect(ROOT/'artifacts/carteira.db') as connection:
        predictions.to_sql('carteira_teste', connection, if_exists='replace', index=False)
        bands = pd.read_sql_query((ROOT/'sql/indicadores.sql').read_text(encoding='utf-8'), connection)
    bands.to_csv(ROOT/'reports/faixas_risco.csv', index=False)
    # Interpret on validation, leaving test for final reporting only.
    importance = permutation_importance(model, x.iloc[val], y.iloc[val],
        scoring='neg_brier_score', n_repeats=3, random_state=SEED, n_jobs=1)
    importances = pd.DataFrame({'variavel': FEATURES, 'importancia_media': importance.importances_mean,
        'desvio': importance.importances_std}).sort_values('importancia_media', ascending=False)
    importances.to_csv(ROOT/'reports/importancia_permutacao.csv', index=False)
    partition = np.full(len(frame), 'treino', dtype=object)
    partition[val], partition[test] = 'validacao', 'teste'
    pd.DataFrame({'id': frame.ID, 'particao': partition}).to_csv(ROOT/'data/processed/particoes.csv', index=False)
    summary = {'executado_em_utc': datetime.now(timezone.utc).isoformat(), 'seed': SEED,
        'fonte': SOURCE, 'sha256_origem': checksum, 'linhas': len(frame),
        'perfis_repetidos_apos_primeiro': int(pd.Series(groups).duplicated().sum()),
        'inadimplentes': int(y.sum()), 'prevalencia': float(y.mean()),
        'particoes': {name: {'clientes':len(idx), 'inadimplentes':int(y.iloc[idx].sum()),
            'prevalencia':float(y.iloc[idx].mean())} for name, idx in [('treino',train),('validacao',val),('teste',test)]},
        'modelo_selecionado':selected, 'criterio':'Menor Brier na validação',
        'limiar_alerta':threshold, 'criterio_limiar':'Maior F1 na validação; grade fixa 0,05–0,80',
        'teste':test_metrics, 'psi_validacao_teste':psi(pv, pt),
        'atributos': FEATURES, 'ambiente': {'python':platform.python_version(),
            **{package:version(package) for package in ['numpy','pandas','scikit-learn','xgboost','matplotlib','xlrd','joblib']}}}
    (ROOT/'reports/resumo.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    joblib.dump({'model':model, 'features':FEATURES, 'threshold':threshold}, ROOT/'artifacts/modelo.joblib')
    from src.report import render_reports
    render_reports(summary, validation_table, bands, scenarios, importances, y.iloc[test].to_numpy(), pt)
    print('Concluído: reports/painel.html e evidencias/*.png', flush=True)

if __name__ == '__main__':
    main()
