"""Evidências reais: gráficos e painel HTML derivados das saídas do experimento."""
import html
import os
import numpy as np
from src.data import ROOT
cache = ROOT / 'artifacts/matplotlib-cache'
cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(cache))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.calibration import calibration_curve

RED, DARK, GRAY = '#a51636', '#17243a', '#6b7280'

def render_reports(summary, validation, bands, scenarios, importances, y, p):
    plt.rcParams.update({'font.family':'DejaVu Sans', 'axes.spines.top':False,
        'axes.spines.right':False, 'axes.titlesize':13, 'axes.labelsize':10, 'figure.dpi':130})
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3), layout='constrained')
    fpr, tpr, _ = roc_curve(y, p)
    axes[0].plot(fpr, tpr, color=RED, lw=2, label=f"AUC = {summary['teste']['roc_auc']:.3f}")
    axes[0].plot([0,1],[0,1], '--', color=GRAY, lw=1)
    axes[0].set(title='Discriminação • ROC', xlabel='Taxa de falsos positivos', ylabel='Taxa de verdadeiros positivos')
    precision, recall, _ = precision_recall_curve(y, p)
    axes[1].plot(recall, precision, color=RED, lw=2, label=f"AP = {summary['teste']['average_precision']:.3f}")
    axes[1].axhline(y.mean(), color=GRAY, ls='--', label='Prevalência')
    axes[1].set(title='Precisão e recall', xlabel='Recall', ylabel='Precisão')
    observed, predicted = calibration_curve(y, p, n_bins=8, strategy='quantile')
    axes[2].plot(predicted, observed, 'o-', color=RED, label='Modelo')
    axes[2].plot([0,1],[0,1], '--', color=GRAY, label='Ideal')
    axes[2].set(title='Calibração por quantis', xlabel='PD média estimada', ylabel='Inadimplência observada')
    for ax in axes:
        ax.legend(fontsize=9); ax.grid(alpha=.15)
    fig.suptitle('Credit Risk Analytics | Avaliação no teste reservado', fontsize=16, weight='bold')
    fig.savefig(ROOT/'evidencias/01-avaliacao-modelo.png', bbox_inches='tight'); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12,4.4), layout='constrained')
    positions = np.arange(len(bands))
    axes[0].bar(positions-.18, bands.pd_media*100, .36, color=DARK, label='PD estimada')
    axes[0].bar(positions+.18, bands.taxa_inadimplencia*100, .36, color=RED, label='Observada')
    axes[0].set_xticks(positions, bands.faixa_risco)
    axes[0].set(title='Risco por faixa', ylabel='Percentual (%)'); axes[0].legend()
    axes[1].plot(scenarios.taxa_elegibilidade*100, scenarios.taxa_inadimplencia_elegiveis*100, 'o-', color=RED)
    for row in scenarios.itertuples():
        axes[1].annotate(f'PD ≤ {row.limite_pd:.0%}', (row.taxa_elegibilidade*100, row.taxa_inadimplencia_elegiveis*100),
            xytext=(3,7), textcoords='offset points', fontsize=9)
    axes[1].set(title='Cenários ilustrativos de elegibilidade', xlabel='Clientes elegíveis (%)', ylabel='Inadimplência entre elegíveis (%)')
    axes[1].margins(.18)
    fig.suptitle('Carteira de teste | Clientes existentes • Taiwan, 2005', fontsize=16, weight='bold')
    fig.savefig(ROOT/'evidencias/02-carteira-cenarios.png', bbox_inches='tight'); plt.close(fig)
    top = importances.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10,5.5), layout='constrained')
    ax.barh(top.variavel, top.importancia_media, xerr=top.desvio, color=RED)
    ax.set(title='Importância por permutação • validação', xlabel='Aumento do Brier ao embaralhar a variável (3 repetições)')
    fig.savefig(ROOT/'evidencias/03-importancia-validacao.png', bbox_inches='tight'); plt.close(fig)
    render_dashboard(summary, validation, bands, scenarios)
    render_markdown(summary, validation, scenarios)

def render_markdown(summary, validation, scenarios):
    lines = ['# Resultados da execução', '',
        'Gerado automaticamente pelo experimento; não editar os valores manualmente.', '',
        f"- Modelo selecionado: **{summary['modelo_selecionado']}**.",
        f"- Origem: {summary['fonte']} (CC BY 4.0).",
        f"- SHA-256: `{summary['sha256_origem']}`.",
        f"- Registros: {summary['linhas']:,}; inadimplentes: {summary['inadimplentes']:,}.",
        f"- Perfis repetidos após a primeira ocorrência: {summary['perfis_repetidos_apos_primeiro']}. Permaneceram agrupados, sem exclusão.",
        '', '## Partições', '', '| Partição | Clientes | Inadimplentes | Prevalência |', '|---|---:|---:|---:|']
    for name, values in summary['particoes'].items():
        lines.append(f"| {name} | {values['clientes']} | {values['inadimplentes']} | {values['prevalencia']:.2%} |")
    lines += ['', '## Comparação na validação', '', '| Modelo | Brier ↓ | ROC AUC ↑ | AP ↑ |', '|---|---:|---:|---:|']
    for row in validation.itertuples():
        lines.append(f'| {row.modelo} | {row.brier:.4f} | {row.roc_auc:.4f} | {row.average_precision:.4f} |')
    lines += ['', '## Avaliação final no teste', '', f"Limiar de alerta escolhido na validação: **{summary['limiar_alerta']:.3f}**.", '',
        '| Métrica | Resultado |', '|---|---:|']
    for name, value in summary['teste'].items():
        lines.append(f'| {name} | {value:.4f} |' if isinstance(value,float) else f'| {name} | {value} |')
    lines += ['', '## Cenários fixos no teste', '',
        '| Corte PD | Elegíveis | Elegibilidade | Inadimplência entre elegíveis |', '|---|---:|---:|---:|']
    for row in scenarios.itertuples():
        lines.append(f'| {row.limite_pd:.0%} | {row.elegiveis} | {row.taxa_elegibilidade:.2%} | {row.taxa_inadimplencia_elegiveis:.2%} |')
    lines += ['', 'Os cortes são ilustrativos e não foram otimizados pelo teste. Não há conclusão sobre rentabilidade ou política ideal.', '',
        f"PSI entre validação e teste: **{summary['psi_validacao_teste']:.5f}**. É uma comparação entre amostras da mesma fotografia, não evidência de monitoramento temporal.", '',
        'Consulte a metodologia e as limitações no README antes de interpretar estes resultados.', '']
    (ROOT/'reports/resultados.md').write_text('\n'.join(lines), encoding='utf-8')

def render_dashboard(summary, validation, bands, scenarios):
    metrics = summary['teste']
    cards = [('Clientes no teste',f"{summary['particoes']['teste']['clientes']:,}".replace(',','.')),
        ('ROC AUC',f"{metrics['roc_auc']:.3f}".replace('.',',')),('Brier',f"{metrics['brier']:.3f}".replace('.',',')),
        ('KS',f"{metrics['ks']:.1%}".replace('.',','))]
    cards_html = ''.join(f'<article><span>{k}</span><strong>{v}</strong></article>' for k,v in cards)
    validation_html = validation[['modelo','brier','roc_auc','average_precision']].rename(
        columns={'modelo':'Modelo','brier':'Brier ↓','roc_auc':'ROC AUC ↑','average_precision':'AP ↑'}
        ).to_html(index=False, float_format=lambda v:f'{v:.4f}'.replace('.',','), border=0)
    scenario_records = scenarios.to_dict(orient='records')
    import json
    template = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Credit Risk Analytics — resultados</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f5f8;color:#17243a;font:16px/1.6 system-ui,sans-serif}
main{max-width:1180px;margin:auto;padding:32px}header{background:#17243a;color:white;border-top:6px solid #ba2444;padding:30px;border-radius:12px}
h1{font-size:36px;line-height:1.15;margin:12px 0}h2{font-size:23px}header p{max-width:800px;color:#d5ddea}.tag{font-size:12px;letter-spacing:2px;color:#ffc4ce}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}article,section{background:white;border:1px solid #e0e5ec;border-radius:12px;padding:24px;margin-bottom:20px}article{margin:0}article span{display:block;color:#667085;font-size:14px}strong{font-size:32px;display:block}
img{width:100%;height:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:12px;text-align:left;border-bottom:1px solid #e7eaf0}th{background:#f6f7fa}.table{overflow:auto}
.small{font-size:14px;color:#667085}select{padding:10px;font-size:16px;margin:0 12px;border:1px solid #a51636;border-radius:6px}output{display:block;padding:16px 0;font-size:18px;color:#8b1530}a{color:#a51636}footer{padding:20px 0;font-size:14px}
@media(max-width:700px){main{padding:16px}.cards{grid-template-columns:repeat(2,1fr)}h1{font-size:28px}header,section{padding:20px}strong{font-size:27px}}
</style><main><header><div class="tag">PORTFÓLIO • EXPERIMENTO REPRODUZÍVEL</div><h1>Credit Risk Analytics</h1><p>Modelagem de inadimplência e análise de risco comportamental em uma base pública de cartões de crédito.</p><p>Modelo selecionado: <b>__MODEL__</b> · Menor Brier na validação.</p></header>
<div class="cards">__CARDS__</div>
<section><h2>Qual modelo estimou melhor as probabilidades?</h2><p>Comparação na validação. O conjunto de teste foi reservado para a avaliação final do modelo escolhido.</p><div class="table">__VALIDATION__</div></section>
<section><h2>Resultado no teste reservado</h2><img src="../evidencias/01-avaliacao-modelo.png" alt="Curvas ROC, precisão e recall e calibração do modelo selecionado"><p class="small">AUC mede ordenação; Brier mede erro das probabilidades. Bons resultados nesta amostra não demonstram desempenho futuro.</p></section>
<section><h2>Como o corte de risco altera o grupo elegível?</h2><label for="cutoff">PD máxima ilustrativa</label><select id="cutoff"><option value="0">10%</option><option value="1">20%</option><option value="2">30%</option><option value="3">40%</option></select><output id="scenario" aria-live="polite"></output><p class="small">Simulação retrospectiva com clientes existentes. Elegibilidade não significa aprovação, contratação ou rentabilidade. Os quatro cortes foram fixados antes da avaliação.</p><img src="../evidencias/02-carteira-cenarios.png" alt="Faixas de risco e cenários de elegibilidade"></section>
<section><h2>Quais variáveis ajudam a previsão?</h2><img src="../evidencias/03-importancia-validacao.png" alt="Importância por permutação calculada na validação"><p class="small">A permutação mede dependência preditiva. Variáveis correlacionadas podem dividir importância; o gráfico não demonstra causalidade.</p></section>
<section><h2>O que estes resultados permitem concluir?</h2><p>O experimento compara modelos e descreve o equilíbrio entre elegibilidade e inadimplência observada. Usa dados históricos de Taiwan, de 2005, com desfecho no mês seguinte.</p><p>Não há validação temporal, dados brasileiros, custos de concessão, LGD ou recuperação. O limite de crédito em NT$ não foi tratado como saldo devedor. O PSI compara validação e teste da mesma fotografia: não é monitoramento temporal.</p><p><a href="resumo.json">Resultados e versões</a> · <a href="comparacao_validacao.csv">Comparação em CSV</a> · <a href="faixas_risco.csv">Indicadores SQL</a> · <a href="../README.md">Documentação</a></p></section>
<footer>Antony Kennedy Ribeiro de Araújo · Projeto autoral educacional · Fonte: <a href="https://doi.org/10.24432/C55S3H">UCI / I-Cheng Yeh</a>, CC BY 4.0. Sem vínculo institucional com Bradesco ou DIO.</footer></main>
<script>const scenarios=__SCENARIOS__;const select=document.getElementById('cutoff');const pct=v=>(v*100).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+'%';function update(){const s=scenarios[Number(select.value)];document.getElementById('scenario').textContent=`${s.elegiveis.toLocaleString('pt-BR')} clientes elegíveis (${pct(s.taxa_elegibilidade)}) · inadimplência observada: ${s.taxa_inadimplencia_elegiveis===null?'sem clientes':pct(s.taxa_inadimplencia_elegiveis)}`;}select.addEventListener('change',update);update();</script></html>'''
    content = template.replace('__MODEL__',html.escape(summary['modelo_selecionado'])).replace('__CARDS__',cards_html).replace('__VALIDATION__',validation_html).replace('__SCENARIOS__',json.dumps(scenario_records, allow_nan=False))
    (ROOT/'reports/painel.html').write_text(content, encoding='utf-8')

if __name__ == '__main__':
    import json
    import pandas as pd
    summary = json.loads((ROOT/'reports/resumo.json').read_text(encoding='utf-8'))
    predictions = pd.read_csv(ROOT/'data/processed/carteira_teste.csv')
    render_reports(summary, pd.read_csv(ROOT/'reports/comparacao_validacao.csv'),
        pd.read_csv(ROOT/'reports/faixas_risco.csv'), pd.read_csv(ROOT/'reports/cenarios_teste.csv'),
        pd.read_csv(ROOT/'reports/importancia_permutacao.csv'),
        predictions.inadimplente.to_numpy(), predictions.pd_estimada.to_numpy())
