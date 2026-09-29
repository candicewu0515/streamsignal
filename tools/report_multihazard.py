from pathlib import Path
import json,base64,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];F=json.loads((R/'results/multihazard_metrics.json').read_text())
labels=[t['name']+' / '+str(t['horizon'])+'d' for t in F['tasks'].values()];tasks=list(F['tasks'].values())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'text.color':'#163850','axes.labelcolor':'#163850'})
fig,ax=plt.subplots(1,2,figsize=(13,5),layout='constrained');values=[100*t['brierSkill'] for t in tasks]
ax[0].barh(labels[::-1],values[::-1],color='#087d87');ax[0].set_xlabel('Brier skill versus same-group seasonal baseline (%)');ax[0].set_title('A  Temporal test: all eight tasks',loc='left',fontweight='bold');ax[0].set_xlim(-2,36)
for i,v in enumerate(values[::-1]):ax[0].text(v+.5,i,f'{v:.1f}%',va='center')
g=F['geographic'];vs=[100*x['skill'] for x in g];ax[1].barh([x['city'] for x in g][::-1],vs[::-1],color=['#b75a3b' if x<0 else '#087d87' for x in vs[::-1]]);ax[1].axvline(0,color='#90a5b8');ax[1].set_xlim(-12,30);ax[1].set_xlabel('Brier skill versus other-city pooled seasonal baseline (%)');ax[1].set_title('B  Held-out city: 3-day rain only',loc='left',fontweight='bold')
for i,v in enumerate(vs[::-1]):ax[1].text(v+(.5 if v>=0 else -.5),i,f'{v:.1f}%',ha='left' if v>=0 else 'right',va='center')
fig.suptitle('StreamSignal · 2026 retrospective evaluation\nPositive skill means lower probability error; the two panels use different baselines.',fontsize=13,fontweight='bold')
fig.savefig(R/'results/multihazard_evaluation.png',dpi=200,facecolor='white');fig.savefig(R/'results/multihazard_evaluation.svg',facecolor='white');plt.close(fig)
md='''# Multi-hazard findings — version 3

Eight weather tasks extend the original next-day rainfall demonstration to three- and seven-day investigation windows. These models predict weather labels, not measured ecological response. All future target dates remain within their train/validation/test split. The original snapshot was already explored in development; this is not an independent external test.

## Measured temporal results

Positive Brier skill means lower probability error than the same-group seasonal baseline. Candidate selection used validation-year 2025 only. Both linear and boosted candidates were retained in the comparison; logistic regression won every validation comparison. Complexity was not used as a substitute for performance.

| Target | Horizon | Test rows | Events | Selected Brier | Seasonal Brier | Skill | AUC | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
'''
for t in tasks:
 m=t['metrics']['test'][t['selected']];b=t['metrics']['test']['seasonal'];md+=f"| {t['name']} | {t['horizon']}d | {m['n']} | {m['events']} | {m['brier']:.4f} | {b['brier']:.4f} | {100*t['brierSkill']:.1f}% | {m['rocAuc']:.3f} | {100*m['precision']:.1f}% | {100*m['recall']:.1f}% |\n"
md+='''
There are 39,648 exported task/group/issue-date predictions. This count includes overlapping windows and repeated use across tasks; it is not a count of independent observations. Low-rain and hot-and-dry targets can have very different prevalence across cities and seasons. All eight tasks are displayed to avoid selecting only the strongest headline. Seven-day compound skill is modest.

## Geographic stress test

For three-day rain, each city is excluded entirely from fitting, candidate selection and baseline construction. Models fit other cities' 2023–2024 observations, select on those cities' 2025 observations, and test on the held-out city in 2026. The baseline pools other-city training labels within ±30 calendar days. It differs from the same-group temporal baseline.

| Excluded city | Selected model | Model Brier | Pooled seasonal Brier | Skill |
|---|---|---:|---:|---:|
'''
for x in g:md+=f"| {x['city']} | {x['selected']} | {x['test'][x['selected']]['brier']:.4f} | {x['test']['seasonal']['brier']:.4f} | {100*x['skill']:.1f}% |\n"
md+='''
Benevento underperforms the pooled seasonal baseline. This is direct evidence that same-region temporal gains do not guarantee transfer. No deployment-quality transfer claim is made.

## From probability to a field question

Mission control maps a selected weather task to a specific question and measurement checklist. Rain prompts review of turbidity, conductivity, nutrients and local runoff observations; heat prompts water-temperature and dissolved-oxygen observations; low rainfall prompts checks of actual water level, flow and habitat connectivity. The compound task combines weather conditions, not unobserved water outcomes.

These are analyst-authored investigation suggestions supported by general mechanisms in [EPA stormwater guidance](https://www.epa.gov/nutrientpollution/sources-and-solutions-stormwater), [USGS dissolved oxygen information](https://www.usgs.gov/water-science-school/science/dissolved-oxygen-and-water) and [EPA dissolved oxygen mechanisms](https://www.epa.gov/caddis/dissolved-oxygen). The references support the rationale, not the exact forecast thresholds, visit timing, priority weights or site-specific protocols. The field team must define appropriate procedures and current access conditions.

## Explicit planning preferences

The default priority is the model probability. An optional urban-cover uplift changes the priority index but never changes the model probability. Urban cover within 500 m is local context, not catchment imperviousness or measured runoff; its historical availability is unverified. Missing context is labelled and receives no uplift. Budgets and one-per-weather-group selection are explicit and exportable. No route, travel time, ecological benefit or optimal sampling design is estimated.

## Observation register

The Field notebook captures site, date, water temperature, dissolved oxygen, pH, turbidity, conductivity, method and notes. Empty fields remain missing. At least one numeric measurement and a method are required. Broad input bounds are entry checks, not ecological safety limits. Corrections and reversible archiving are supported. Records remain in the browser until exported; local records do not retrain any model or alter the official snapshot.

## Reproduction and limitations

Run `python tools/train_multihazard.py`, then `python tools/report_multihazard.py` in the supplied dependency environment. Full protocol: `MULTIHAZARD_PROTOCOL.md`. Full probabilities and comparisons are in `results/multihazard_predictions.csv` and `results/multihazard_comparison.csv`. Bootstrap intervals, calibration bins, thresholds and monthly performance are in `results/multihazard_metrics.json`.

Seven-day input windows and complete future labels exclude missing periods and may bias the evaluated sample toward complete observations. Daily source publication latency and upstream weather provenance remain unverified. No numerical weather prediction benchmark, independent external dataset, prospective pilot or measured water-quality endpoint has been evaluated. These limits are part of the product, not hidden in a claim of environmental early-warning accuracy.
'''
(R/'docs/MULTIHAZARD_RESULTS.md').write_text(md)
figure=base64.b64encode((R/'results/multihazard_evaluation.png').read_bytes()).decode()
report=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>StreamSignal — Multi-hazard evaluation</title><style>body{{font:15px/1.7 system-ui;color:#163850;max-width:1100px;margin:35px auto;padding:25px}}img{{width:100%}}pre{{font:14px/1.7 system-ui;white-space:pre-wrap}}button{{padding:12px;background:#123e5b;color:white;border:0}}@media print{{button{{display:none}}}}</style><button onclick="print()">Print / Save as PDF</button><h1>Eight forecasts. An explicit field question.</h1><p>Three- and seven-day weather windows, two candidate models, seasonal and persistence baselines, and a held-out-city stress test.</p><img src="data:image/png;base64,{figure}" alt="Temporal model skill for eight tasks and held-out-city model skill for three-day rain"><pre>{html.escape(md)}</pre></html>'''
(R/'results/multihazard_report.html').write_text(report)
print('Multi-hazard figure, report and results narrative generated.')
