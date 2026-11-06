# -*- coding: utf-8 -*-
"""One-shot: hongguo2 Update UX when seasons is null + layout."""
from pathlib import Path

paths = [
    Path(r"Z:\PinelineV5\static\ui\hongguo2.html"),
    Path(r"Z:\PinelineV4\hongguo2.html"),
]
for extra in (
    Path(r"Z:\PinelineV2\static\ui\hongguo2.html"),
    Path(r"Z:\PinelineV2\hongguo2.html"),
):
    if extra.exists():
        paths.append(extra)

src = paths[0].read_text(encoding="utf-8")
orig = src

old_css = """  .layout{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(300px,0.85fr);height:auto;min-height:0;gap:0}
  .col-discover,.col-ops{display:flex;flex-direction:column;min-height:0;min-width:0}
  .col-discover{border-right:1px solid var(--line)}
  .col-ops{background:var(--side)}"""
new_css = """  .layout{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(360px,1fr);height:auto;min-height:0;gap:0}
  .col-discover,.col-ops{display:flex;flex-direction:column;min-height:0;min-width:0}
  .col-discover{border-right:1px solid var(--line)}
  .col-ops{background:var(--side)}"""
if old_css not in src:
    raise SystemExit("css layout block missing")
src = src.replace(old_css, new_css, 1)

old_banner = """  .seasons-banner{border-bottom:1px solid var(--line);background:var(--panel)}
  .seasons-banner-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 12px;background:var(--raise)}
  .seasons-banner-head h2{margin:0;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700}
  .seasons-banner-head .cnt{margin-left:5px;font-size:10.5px;padding:0 6px;border-radius:999px;background:var(--accent);color:#231a08}
  .seasons-banner-head .cnt:empty{display:none}
  .seasons-banner-head .collapse-btn{flex:none;min-width:32px;padding:4px 8px}
  .seasons-banner.collapsed .seasons-banner-body{display:none}
  .seasons-banner-body{padding:8px 12px 10px;max-height:220px;overflow:auto}
  .seasons-progress{display:flex;flex-direction:column;gap:6px;padding:14px 16px;margin-bottom:8px;border-radius:12px;
    border:1px solid rgba(233,169,60,.35);background:var(--accent-dim)}
  .seasons-progress[hidden]{display:none!important}
  .seasons-progress .sp-title{font-weight:800;font-size:13.5px;color:var(--text)}
  .seasons-progress .sp-sub{font:600 12.5px/1.4 var(--mono);color:var(--text2);font-variant-numeric:tabular-nums}
  .seasons-progress .sp-bar{height:6px;border-radius:999px;background:var(--raise);overflow:hidden}
  .seasons-progress .sp-bar > i{display:block;height:100%;width:0;background:var(--accent);border-radius:999px;transition:width .25s}"""

new_banner = """  .seasons-banner{border-bottom:1px solid var(--line);background:var(--panel)}
  .seasons-banner-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 12px;background:var(--raise)}
  .seasons-banner-head h2{margin:0;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700}
  .seasons-banner-head .cnt{margin-left:5px;font-size:10.5px;padding:0 6px;border-radius:999px;background:var(--accent);color:#231a08}
  .seasons-banner-head .cnt:empty{display:none}
  .seasons-banner-head .collapse-btn{flex:none;min-width:32px;padding:4px 8px}
  .seasons-banner.collapsed .seasons-banner-body{display:none}
  .seasons-banner.busy{box-shadow:inset 0 -2px 0 var(--accent)}
  .seasons-banner-body{padding:8px 12px 10px;max-height:min(36vh,320px);overflow:auto}
  .seasons-banner.busy .seasons-banner-body{max-height:min(48vh,460px)}
  .seasons-live{flex:1;min-width:180px;max-width:420px;display:flex;flex-direction:column;gap:4px}
  .seasons-live[hidden]{display:none!important}
  .seasons-live .sp-sub{font:600 12px/1.35 var(--mono);color:var(--text2);font-variant-numeric:tabular-nums}
  .seasons-live .sp-bar{height:5px;border-radius:999px;background:var(--bg);overflow:hidden}
  .seasons-live .sp-bar > i{display:block;height:100%;width:0;background:var(--accent);border-radius:999px;transition:width .25s}
  .seasons-progress{display:flex;flex-direction:column;gap:6px;padding:14px 16px;margin-bottom:8px;border-radius:12px;
    border:1px solid rgba(233,169,60,.35);background:var(--accent-dim)}
  .seasons-progress[hidden]{display:none!important}
  .seasons-progress .sp-title{font-weight:800;font-size:13.5px;color:var(--text)}
  .seasons-progress .sp-sub{font:600 12.5px/1.4 var(--mono);color:var(--text2);font-variant-numeric:tabular-nums}
  .seasons-progress .sp-bar{height:6px;border-radius:999px;background:var(--raise);overflow:hidden}
  .seasons-progress .sp-bar > i{display:block;height:100%;width:0;background:var(--accent);border-radius:999px;transition:width .25s}"""

if old_banner not in src:
    raise SystemExit("banner css missing")
src = src.replace(old_banner, new_banner, 1)

old_media = """    .seasons-banner-body{max-height:280px}"""
new_media = """    .seasons-banner-body{max-height:min(42vh,360px)}
    .seasons-banner.busy .seasons-banner-body{max-height:min(55vh,520px)}"""
if old_media not in src:
    raise SystemExit("media css missing")
src = src.replace(old_media, new_media, 1)

old_head = """      <button class="btn pri" type="button" onclick="lsnUpdateAll()">↻ Cập nhật tất cả</button>
      <button class="btn" type="button" onclick="lsnRefresh()">Làm mới</button>
      <span class="grow"></span>
      <span class="muted hint-inline" id="seasons-hint">Đọc seasons từ Hongguo /dl/status</span>"""
new_head = """      <button class="btn pri" type="button" onclick="lsnUpdateAll()">↻ Cập nhật tất cả</button>
      <button class="btn" type="button" onclick="lsnRefresh()">Làm mới</button>
      <div class="seasons-live" id="seasonsLive" hidden>
        <div class="sp-sub" id="seasonsLiveSub">—</div>
        <div class="sp-bar" aria-hidden="true"><i id="seasonsLiveBar"></i></div>
      </div>
      <span class="grow"></span>
      <span class="muted hint-inline" id="seasons-hint">Đọc seasons / series từ Hongguo /dl/status</span>"""
if old_head not in src:
    raise SystemExit("banner head html missing")
src = src.replace(old_head, new_head, 1)

start = src.find("function lsnProgressFrac(d){")
end = src.find("function lsnTake(st){")
if start < 0 or end < 0:
    raise SystemExit(f"markers missing {start} {end}")

new_funcs = r"""function lsnProgressFrac(d){
  const ss=(d&&d.seasons)||{};
  const cur=lsnPickNum(d&&d.checked, ss.checked, d&&d.done, ss.done, d&&d.progress, ss.progress);
  const tot=lsnPickNum(d&&d.to_check, ss.to_check, d&&d.total, ss.total, d&&d.to_check_n, ss.total_n);
  if(cur!=null && tot!=null && tot>0) return {cur, tot, label:cur+'/'+tot};
  const series=Array.isArray(d&&d.series)?d.series:[];
  if(series.length){
    const done=series.filter(s=>{
      const st=String((s&& (s.status||s.state))||'');
      return st==='done'||st==='checked'||st==='ok';
    }).length;
    const prog=series.reduce((a,s)=>a+num(s&&s.done),0);
    const all=series.reduce((a,s)=>a+num(s&&s.total),0);
    if(all>0) return {cur:prog, tot:all, label:prog+'/'+all+' tập'};
    return {cur:done, tot:series.length, label:done+'/'+series.length+' series'};
  }
  const bc=lsnBucketCounts(ss);
  if(bc.albumN){
    const doneAlb=Math.max(0, bc.albumN-bc.partialN-bc.deferredN);
    return {cur:doneAlb, tot:bc.albumN, label:doneAlb+'/'+bc.albumN+' album'};
  }
  return {cur:null, tot:null, label:''};
}
function lsnIsScanning(d){
  d=d||window.__hgLastStatus||{};
  const ss=d.seasons||{};
  const state=String(ss.state||'');
  const phase=String(d.phase||'');
  const mode=String(d.mode||'');
  if(_lsnBusy) return true;
  if(d.running && (mode==='library' || state.match(/run|scan|check|update/i) || phase.match(/scan|check|update|download/i))) return true;
  if(state==='running'||state==='scanning'||state==='checking'||state==='update') return true;
  return false;
}
function lsnStatusVn(d){
  d=d||window.__hgLastStatus||{};
  const ss=d.seasons||{};
  const state=String(ss.state||'');
  const phase=String(d.phase||'');
  const bc=lsnBucketCounts(ss);
  const frac=lsnProgressFrac(d);
  const found=lsnPickNum(d.found, ss.found);
  const seriesN=(Array.isArray(d.series)?d.series.length:0) || lsnPickNum(d.total, ss.total, d.to_check, ss.to_check) || 0;
  const scanning=lsnIsScanning(d);
  if(scanning){
    const bits=[];
    if(frac.label) bits.push(frac.label);
    else if(seriesN) bits.push(seriesN+' series');
    if(found!=null) bits.push('tìm thấy '+found);
    if(phase) bits.push(phase);
    if(d.eps_done!=null && d.eps_need!=null) bits.push(num(d.eps_done)+'/'+num(d.eps_need)+' tập');
    if(state) bits.push('seasons.'+state);
    const title = phase==='downloading' ? 'Đang tải sau quét…'
      : (phase==='cancelled' ? 'Update bị hủy…' : 'Đang quét thư viện…');
    return {title, sub: bits.join(' · ') || 'Chờ Hongguo báo tiến độ', frac};
  }
  if(state==='done' || state==='idle' || (!d.running && (_lsn || found!=null || seriesN))){
    const bits=[bc.sug? (bc.sug+' gợi ý') : '', bc.soon? (bc.soon+' sắp ra') : '',
                bc.auto? (bc.auto+' đã thêm') : '', bc.albumN? (bc.albumN+' album lớn') : '',
                found!=null? ('tìm thấy '+found) : '',
                frac.label? ('đã kiểm '+frac.label) : ''].filter(Boolean);
    return {title: bits.length ? ('Xong: '+bits.join(' · ')) : 'Update all xong', sub: [phase, state?('seasons.'+state):''].filter(Boolean).join(' · '), frac:{cur:null,tot:null,label:''}};
  }
  if(!_lsn) return {title:'Chưa có seasons', sub:'Bấm Cập nhật tất cả để quét (Downloader phải chạy)', frac};
  return {title:'Mùa mới', sub:state?('seasons.state='+state):'', frac};
}
function lsnApplyProgressDom(info, show){
  const ban=document.getElementById('seasonsBanner');
  if(ban) ban.classList.toggle('busy', !!show);
  const live=document.getElementById('seasonsLive');
  const liveSub=document.getElementById('seasonsLiveSub');
  const liveBar=document.getElementById('seasonsLiveBar');
  const card=document.getElementById('seasonsProgress');
  const title=document.getElementById('seasonsProgressTitle');
  const sub=document.getElementById('seasonsProgressSub');
  const bar=document.getElementById('seasonsProgressBar');
  const pct=(info.frac.cur!=null && info.frac.tot>0) ? Math.min(100, Math.round(100*info.frac.cur/info.frac.tot)) : (show?18:0);
  const line=(info.title||'')+(info.sub?(' · '+info.sub):'');
  if(live){
    live.hidden=!show;
    if(liveSub) liveSub.textContent=line||'—';
    if(liveBar) liveBar.style.width=pct+'%';
  }
  if(card){
    if(!show){ card.hidden=true; }
    else {
      if(title) title.textContent=info.title;
      if(sub) sub.textContent=info.sub||info.frac.label||'';
      if(bar) bar.style.width=pct+'%';
      card.hidden=false;
    }
  }
}
function lsnShowProgress(show, d){
  if(!show){ lsnApplyProgressDom({title:'', sub:'', frac:{cur:null,tot:null,label:''}}, false); return; }
  const info=lsnStatusVn(d);
  lsnApplyProgressDom(info, true);
  lsnSetBannerOpen(true);
}
function lsnScanFallbackHtml(st){
  const series=Array.isArray(st&&st.series)?st.series:[];
  if(!series.length) return '';
  const order=['downloading','queued','checked','done','failed','cancelled','?'];
  const by={};
  series.forEach(s=>{
    const k=String((s&& (s.status||s.state))||'?') || '?';
    (by[k]=by[k]||[]).push(s);
  });
  const found=lsnPickNum(st.found);
  const frac=lsnProgressFrac(st);
  const say=[frac.label?('đã kiểm '+frac.label):'', found!=null?('tìm thấy '+found):'', st.phase?String(st.phase):''].filter(Boolean).join(' · ');
  let h='<div class="lsn-head"><span class="lsn-title">📋 Quét thư viện</span><span class="lsn-sub">'+esc(say|| (series.length+' series'))+'</span></div>';
  order.concat(Object.keys(by).filter(k=>!order.includes(k))).forEach(k=>{
    const xs=by[k]; if(!xs||!xs.length) return;
    const label={downloading:'Đang tải',queued:'Chờ tải',checked:'Đã kiểm',done:'Xong',failed:'Lỗi',cancelled:'Đã hủy'}[k]||k;
    h+='<div class="lsn-row"><span class="lsn-k">'+esc(label)+' · '+xs.length+'</span><div class="lsn-items">'
      +xs.slice(0,48).map(x=>{
        const title=String(x.title||x.name||x.sid||'');
        const need=num(x.need), have=num(x.have), tot=num(x.total), done=num(x.done);
        let meta='';
        if(need>0) meta='cần +'+need;
        else if(tot>0) meta=done+'/'+tot;
        else if(have>0) meta='có '+have;
        const cls=(k==='checked'||k==='done')?'ok':(k==='downloading'?'dl':'');
        return lsnPlain({sid:x.sid,title}, meta, cls);
      }).join('')
      +(xs.length>48?('<span class="muted">+'+ (xs.length-48)+'…</span>'):'')
      +'</div></div>';
  });
  return h;
}
"""

src = src[:start] + new_funcs + src[end:]

old_render_bit = """  const has=_lsn && !_lsnHide && (auto.length||stoppedAll.length||locked.length||soon.length||bigs.length||sug.length);
  const scanning=!!(_lsnBusy || (st.running && (st.mode==='library' || String((st.seasons||{}).state||'').match(/run|scan|check|update/i))));
  if(scanning && !has){ lsnShowProgress(true, st); }
  else if(!scanning){ lsnShowProgress(false, st); }
  if(empty) empty.hidden=!!(has || scanning);
  if(!has){ el.hidden=true; el.innerHTML=''; lsnUpdateBadge(); return; }
  lsnShowProgress(false, st);"""

new_render_bit = """  const has=_lsn && !_lsnHide && (auto.length||stoppedAll.length||locked.length||soon.length||bigs.length||sug.length);
  const scanning=lsnIsScanning(st);
  const wantScan=!has && (scanning || (!_lsnHide && (st.found!=null || (st.mode==='library' && Array.isArray(st.series) && st.series.length))));
  if(scanning || wantScan){ lsnShowProgress(true, st); }
  else { lsnShowProgress(false, st); }
  if(empty) empty.hidden=!!(has || wantScan || scanning);
  if(!has){
    const scanHtml=wantScan ? lsnScanFallbackHtml(st) : '';
    if(scanHtml){ el.hidden=false; el.innerHTML=scanHtml; lsnUpdateBadge(); return; }
    el.hidden=true; el.innerHTML=''; lsnUpdateBadge(); return;
  }
  if(!scanning) lsnShowProgress(false, st);"""

if old_render_bit not in src:
    raise SystemExit("lsnRender bit missing")
src = src.replace(old_render_bit, new_render_bit, 1)

old_loop = """  const t0=Date.now(), maxMs=12*60*1000;
  while(Date.now()-t0<maxMs){
    await new Promise(r=>setTimeout(r,2000));
    let d;
    try{ d=await jget('/api/hg/status'); }catch(e){ continue; }
    window.__hgLastStatus=d;
    lsnTake(d); lsnRender();
    const ss=d.seasons||{};
    const state=String(ss.state||'');
    const info=lsnStatusVn(d);
    if(d.running || state==='running' || state==='scanning' || state==='checking' || state==='update'){
      lsnHint(info.title+(info.sub?(' · '+info.sub):''));
      lsnShowProgress(true, d);
      continue;
    }
    if(state==='done' || state==='idle' || (!d.running && _lsn)){
      lsnHint(info.title+(info.sub?(' · '+info.sub):''));
      break;
    }
    if(!d.running && Date.now()-t0>8000){
      lsnHint('Update all đã gửi — chưa thấy seasons.state=done (Downloader đang chạy?)');
      break;
    }
  }
  _lsnBusy=false; lsnShowProgress(false); lsnRender();
  const last=window.__hgLastStatus||{};
  const doneInfo=lsnStatusVn(last);
  lsnHint(doneInfo.title+(doneInfo.sub?(' · '+doneInfo.sub):''));
}"""

new_loop = """  const t0=Date.now(), maxMs=12*60*1000;
  let sawRunning=false;
  while(Date.now()-t0<maxMs){
    await new Promise(r=>setTimeout(r,1500));
    let d;
    try{ d=await jget('/api/hg/status'); }catch(e){ continue; }
    window.__hgLastStatus=d;
    lsnTake(d); lsnRender();
    const info=lsnStatusVn(d);
    lsnHint(info.title+(info.sub?(' · '+info.sub):''));
    lsnShowProgress(true, d);
    if(d.running || lsnIsScanning(d)){ sawRunning=true; continue; }
    if(_lsn || (sawRunning && Date.now()-t0>2500) || (!sawRunning && Date.now()-t0>6000)){
      break;
    }
  }
  _lsnBusy=false;
  const last=window.__hgLastStatus||{};
  const doneInfo=lsnStatusVn(last);
  const keep=!!(last.found!=null || (Array.isArray(last.series)&&last.series.length) || lsnHasBoard());
  lsnShowProgress(keep, last);
  lsnRender();
  lsnHint(doneInfo.title+(doneInfo.sub?(' · '+doneInfo.sub):''));
}"""

if old_loop not in src:
    raise SystemExit("update loop missing")
src = src.replace(old_loop, new_loop, 1)

if src == orig:
    raise SystemExit("no changes?")

for p in paths:
    p.write_text(src, encoding="utf-8")
    print("wrote", p, "bytes", len(src.encode("utf-8")))
print("ok")
