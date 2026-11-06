# -*- coding: utf-8 -*-
"""Hongguo2: Tìm mùa mới (info-only) + làm rõ Update thư viện tải tập thiếu."""
from pathlib import Path

paths = [
    Path(r"Z:\PinelineV5\static\ui\hongguo2.html"),
    Path(r"Z:\PinelineV4\hongguo2.html"),
    Path(r"Z:\PinelineV2\hongguo2.html"),
]
src = paths[0].read_text(encoding="utf-8")
orig = src

old_btns = """      <h2>Mùa mới <span class="cnt" id="tab-seasons-n"></span></h2>
      <button class="btn pri" type="button" onclick="lsnUpdateAll()">↻ Cập nhật tất cả</button>
      <button class="btn" type="button" onclick="lsnRefresh()">Làm mới</button>"""
new_btns = """      <h2>Mùa mới <span class="cnt" id="tab-seasons-n"></span></h2>
      <button class="btn pri" type="button" onclick="lsnDiscoverNew()" title="Chỉ tìm mùa/series mới từ thư viện — KHÔNG tải">🔎 Tìm mùa mới</button>
      <button class="btn" type="button" onclick="lsnUpdateAll()" title="Hongguo Update all: quét + TẢI tập thiếu của series đã có (dùng chung máy tải)">↻ Cập nhật thư viện</button>
      <button class="btn" type="button" onclick="lsnRefresh()">Làm mới</button>"""
if old_btns not in src:
    raise SystemExit("banner buttons missing")
src = src.replace(old_btns, new_btns, 1)

old_empty = """      <div class="muted" id="seasons-empty" style="padding:8px 4px">Chưa có dữ liệu mùa mới. Bấm <b>Cập nhật tất cả</b> để Hongguo quét thư viện (cần Downloader đang chạy).</div>"""
new_empty = """      <div class="muted" id="seasons-empty" style="padding:8px 4px">Chưa có dữ liệu mùa mới. Bấm <b>Tìm mùa mới</b> để chỉ lấy thông tin (không tải). <b>Cập nhật thư viện</b> = Hongguo quét + tải tập thiếu — phải chờ nếu đang tải phim khác.</div>"""
if old_empty not in src:
    raise SystemExit("empty hint missing")
src = src.replace(old_empty, new_empty, 1)

old_hint = """      <span class="muted hint-inline" id="seasons-hint">Đọc seasons / series từ Hongguo /dl/status</span>"""
new_hint = """      <span class="muted hint-inline" id="seasons-hint">Tìm mùa mới = chỉ thông tin · Cập nhật thư viện = Hongguo tải tập thiếu</span>"""
if old_hint not in src:
    raise SystemExit("hint missing")
src = src.replace(old_hint, new_hint, 1)

# Replace lsnUpdateAll start guard + add lsnDiscoverNew before it
old_update = """async function lsnUpdateAll(){
  if(_lsnBusy) return;
  const st=window.__hgLastStatus||{};
  if(st.running){ lsnHint('Hongguo đang chạy job khác — chờ xong rồi Update all'); return; }
  _lsnBusy=true; _lsnUserClosed=false; _lsnHide=false;
  lsnSetBannerOpen(true);
  lsnShowProgress(true, st);
  lsnRender();
  lsnHint('Đang gửi Update all tới Hongguo…');
  try{
    await jpost('/api/hg/library/update',{});
  }catch(e){
    _lsnBusy=false; lsnShowProgress(false); lsnRender();
    lsnHint(e.message||String(e));
    return;
  }
  const t0=Date.now(), maxMs=12*60*1000;
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

new_update = r"""function lsnCoreApprox(title){
  let t=String(title||'').trim();
  t=t.replace(/第[0-9一二三四五六七八九十百千零〇两兩]+季.*$/u,'');
  t=t.replace(/\s*S\d+\s*.*$/i,'');
  t=t.replace(/（.*?）|\(.*?\)/g,'');
  return t.trim();
}
function lsnToBoardItem(r){
  const sid=String((r&& (r.series_id||r.sid))||'');
  if(!LSN_ID.test(sid)) return null;
  return {
    sid,
    title:String(r.title||r.name||sid),
    eps:num(r.episodes||r.eps||r.total||0),
    season:num(r.season||0),
    score:String(r.score||''),
    base:String(r.core||r.stem||lsnCoreApprox(r.title||r.name||'')||''),
    album:String(r.album||''),
    short:true
  };
}
async function lsnDiscoverNew(){
  if(_lsnBusy) return;
  _lsnBusy=true; _lsnUserClosed=false; _lsnHide=false;
  lsnSetBannerOpen(true);
  const fake={running:true, mode:'library', phase:'discover', checked:0, to_check:1, found:0, series:[]};
  lsnApplyProgressDom({title:'Đang tìm mùa mới…', sub:'chỉ thông tin — không tải', frac:{cur:0,tot:1,label:'0/?'}}, true);
  lsnHint('Đang tìm mùa mới (không tải)…');
  let items=[];
  try{
    const lib=await jget('/api/hg/library');
    items=Array.isArray(lib.items)?lib.items:[];
  }catch(e){
    _lsnBusy=false; lsnShowProgress(false);
    lsnHint('Không đọc được thư viện: '+(e.message||e));
    return;
  }
  const have=new Set(items.map(x=>String(x.series_id||'')).filter(s=>LSN_ID.test(s)));
  const cores=[], seen=new Set();
  items.slice().sort((a,b)=>num(b.updated||b.dl_at)-num(a.updated||a.dl_at)).forEach(it=>{
    const c=lsnCoreApprox(it.title||it.name);
    if(c && !seen.has(c)){ seen.add(c); cores.push(c); }
  });
  const take=cores.slice(0,14);
  const held=[], related=[], bySid=new Map();
  let done=0;
  async function one(c){
    try{
      const r=await jget('/api/hg/search?q='+encodeURIComponent(c)+'&expand=false');
      const rows=[].concat(r.results||[]);
      (r.groups||[]).forEach(g=>{ if(g&&Array.isArray(g.items)) rows.push(...g.items); });
      rows.forEach(row=>{
        const it=lsnToBoardItem(row);
        if(!it || bySid.has(it.sid)) return;
        bySid.set(it.sid, it);
        if(have.has(it.sid)) return;
        // cùng core với query → held (mùa mới); khác → related
        const same=lsnCoreApprox(it.title).includes(c) || c.includes(lsnCoreApprox(it.title)) || (it.base&& (it.base===c || c.includes(it.base)));
        (same?held:related).push(it);
      });
    }catch(e){ /* skip one core */ }
    done++;
    lsnApplyProgressDom({title:'Đang tìm mùa mới…', sub:done+'/'+take.length+' bộ · tìm thấy '+(held.length+related.length)+' (chưa có trong thư viện)', frac:{cur:done,tot:take.length,label:done+'/'+take.length}}, true);
  }
  for(let i=0;i<take.length;i+=3){
    await Promise.all(take.slice(i,i+3).map(one));
  }
  _lsn={
    state:'done', auto:[], locked:[], failed:[], stopped:[], declined:[],
    older:[], removed:[], soon:[],
    held:held, related:related, big:{albums:[]}
  };
  _lsnBusy=false;
  lsnRender();
  const n=held.length+related.length;
  lsnApplyProgressDom({title: n?('Tìm thấy '+n+' mùa/series chưa có'):'Không thấy mùa mới', sub:'chỉ thông tin — bấm + Thêm mới tải', frac:{cur:take.length,tot:take.length,label:take.length+'/'+take.length}}, true);
  lsnHint(n?('Tìm thấy '+held.length+' mùa gần + '+related.length+' liên quan — chưa tải. Bấm + Thêm nếu muốn tải.'):('Đã quét '+take.length+' bộ — không thấy mùa mới ngoài thư viện'));
}
async function lsnUpdateAll(){
  if(_lsnBusy) return;
  const st=window.__hgLastStatus||{};
  const attachOnly=!!(st.running && String(st.mode||'')==='library');
  if(st.running && !attachOnly){
    lsnHint('Hongguo đang tải phim — «Cập nhật thư viện» dùng chung máy tải, phải chờ xong. Muốn chỉ xem thông tin: bấm «Tìm mùa mới».');
    return;
  }
  _lsnBusy=true; _lsnUserClosed=false; _lsnHide=false;
  lsnSetBannerOpen(true);
  lsnShowProgress(true, st);
  lsnRender();
  if(attachOnly){
    lsnHint('Đang theo dõi quét thư viện đang chạy trên Hongguo…');
  } else {
    lsnHint('Gửi Cập nhật thư viện → Hongguo sẽ quét VÀ tải tập thiếu của series đã có…');
    try{
      await jpost('/api/hg/library/update',{});
    }catch(e){
      _lsnBusy=false; lsnShowProgress(false); lsnRender();
      const msg=String(e.message||e);
      if(/already running|đang chạy|wait for it/i.test(msg)){
        lsnHint('Hongguo báo đang có job tải/update — chờ xong, hoặc bấm «Tìm mùa mới» nếu chỉ cần thông tin.');
      } else {
        lsnHint(msg);
      }
      return;
    }
  }
  const t0=Date.now(), maxMs=12*60*1000;
  let sawRunning=attachOnly;
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

if old_update not in src:
    raise SystemExit("lsnUpdateAll block missing")
src = src.replace(old_update, new_update, 1)

if src == orig:
    raise SystemExit("no changes")

for p in paths:
    if p.exists():
        p.write_text(src, encoding="utf-8")
        print("wrote", p)
print("ok")
