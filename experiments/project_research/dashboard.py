"""Read-only local dashboard generated from durable research records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import utc_now
from .state import Store


TEMPLATE = r'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>자율연구 실행 기록</title><style>
:root{font:16px/1.6 system-ui,sans-serif;color:#e7edf7;background:#0b1220}body{max-width:1220px;margin:0 auto;padding:28px}h1{font-size:28px;margin:0}h2{font-size:20px}small,.muted{color:#a5b3ca}header{border-bottom:1px solid #35445e;padding-bottom:24px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}.card,details{background:#141f32;border:1px solid #35445e;border-radius:10px;padding:18px}label{margin-right:20px}select{font:inherit;background:#141f32;color:inherit;border:1px solid #35445e;padding:6px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:12px 8px;border-bottom:1px solid #35445e;text-align:left;vertical-align:top}.scroll{overflow:auto}pre{white-space:pre-wrap;word-break:break-word;font-size:13px}.pill{color:#82e0b1}details{margin:12px 0}a{color:#9dc4ff}.unknown{color:#ffc982}
</style><header><h1>검증된 결론까지 이어지는 자율연구</h1><p>현재 질문 · 부족한 근거 · 다음 선택의 이유</p><small id="updated"></small></header>
<div id="cards" class="cards"></div><section><h2>연구 캠페인</h2><p class="muted">계획, 실제 연구 실행, 개발 품질 AAA, 최종 평가, PI 판정을 각각 표시합니다.</p><label>분야 <select id="domain"><option value="">전체</option><option>wine</option><option>duckdb</option><option>diffusion</option></select></label><label>단계 <select id="stage"><option value="first_week">첫 주 B/P</option><option value="comparison">후속 B/H/P</option></select></label><div class="scroll"><table><thead><tr><th>프로젝트</th><th>질문</th><th>부족한 근거 / 다음 엣지</th><th>상태</th><th>품질 / 우위 / PI</th></tr></thead><tbody id="campaigns"></tbody></table></div></section>
<section><h2>실제 개발 실험과 관측</h2><div id="experiments"></div></section><section><h2>검수 · 모델 교체 · 복구 · 비용</h2><div id="events"></div></section>
<p class="muted">이 화면은 로컬 기록의 재생입니다. 진행 중 실행은 ORX 상태 조회 근거가 있을 때만 표시합니다. native ARGO 건설은 중지 상태입니다.</p>
<script id="data" type="application/json">__DATA__</script><script>
const d=JSON.parse(document.getElementById('data').textContent);const el=id=>document.getElementById(id);const text=(tag,s)=>{const n=document.createElement(tag);n.textContent=s;return n};
el('updated').textContent='기록 생성: '+d.generated_at+' · 원본 ORX 실행 ID와 근거 파일을 상세 기록에서 확인';
const charges=d.state.charges,spent=charges.reduce((s,x)=>s+(x.actual??x.reserved),0),unknown=charges.filter(x=>x.state==='UNKNOWN').length;
const measurements=d.state.events.filter(x=>x.event==='development_research_result');
for(const [title,value,note] of [['실제 개발 실험',measurements.filter(x=>x.status==='SUCCEEDED').length+'건','자동 B/P 캠페인 완료와 구분'],['추가 예산',spent.toLocaleString()+' / 300,000원','확인액 + 미정산 예약액; 미확인 '+unknown+'건'],['PI 완료 판정','0건','판정 수신 전에는 완료로 집계하지 않음'],['다음 보고',d.programme.first_report_due,'첫 실제 실험 기한: '+d.programme.first_real_experiment_due]]){const c=text('div','');c.className='card';c.append(text('small',title),text('h2',String(value)),text('small',note));el('cards').append(c)}
function render(){el('campaigns').replaceChildren();for(const c of d.programme.campaigns.filter(x=>x.stage===el('stage').value&&(!el('domain').value||x.domain===el('domain').value))){const records=d.state.records.filter(x=>x.project_id===c.id);const decision=records.filter(x=>x.type==='DecisionRecord').at(-1);const checkpoint=records.filter(x=>x.type==='Checkpoint').at(-1);const assessment=records.filter(x=>x.type==='Assessment').at(-1);const row=document.createElement('tr');const q=checkpoint?.question||decision?.question||'에이전트가 문헌·개발 관측으로 구체화';const edge=decision?decision.selected_edge+' — '+decision.expected_information:'모델 경로·과금·격리 실사용 검증과 연구 세션 시작';for(const v of [c.id,q,(checkpoint?.uncertainties||[]).join('; ')+' '+edge,c.status,(assessment?.quality||c.quality)+' / '+(assessment?.superiority||c.superiority)+' / '+(assessment?.pi_acceptance||c.pi_acceptance)])row.append(text('td',v));el('campaigns').append(row)}}
for(const id of ['domain','stage'])el(id).addEventListener('change',render);render();
function detail(target,title,value){const box=document.createElement('details');box.append(text('summary',title),text('pre',JSON.stringify(value,null,2)));el(target).append(box)}
if(!measurements.length)el('experiments').append(text('p','실제 연구 결과가 아직 기록되지 않았습니다.'));
for(const r of measurements)detail('experiments',r.domain+' · '+r.status+' · '+r.id,r);
for(const r of d.results)detail('experiments',r.domain+' · 관측 결과 · '+r.id,r);
for(const r of [...d.state.events.filter(x=>x.event!=='development_research_result'),...d.state.continuations,...d.state.charges,...d.state.records.filter(x=>x.type==='Assessment')])detail('events',r.event||r.id||r.project||'기록',r);
</script></html>'''


def render(root: Path, output: Path):
    programme = json.loads((root / "control/programme.json").read_text())
    state = Store(root / "control/state.sqlite").snapshot()
    results = []
    for event in state["events"]:
        if event.get("event") == "development_research_result":
            path = Path(event["receipt"])
            if path.is_file() and path.resolve().is_relative_to((root / "runs").resolve()):
                value = json.loads(path.read_text())
                results.append({k: value.get(k) for k in ("id", "domain", "status", "result", "resources", "result_sha256", "scope")})
    data = {"generated_at": utc_now(), "programme": programme, "state": state, "results": results}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.root, args.output)


if __name__ == "__main__":
    main()
