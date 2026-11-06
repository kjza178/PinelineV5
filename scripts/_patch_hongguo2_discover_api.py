# -*- coding: utf-8 -*-
"""Replace client-side lsnDiscoverNew with API /api/hg/library/seasons/discover."""
from pathlib import Path

OLD = r'''async function lsnDiscoverNew(){
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
}'''

NEW = r'''async function lsnDiscoverNew(){
  if(_lsnBusy) return;
  _lsnBusy=true; _lsnUserClosed=false; _lsnHide=false;
  lsnSetBannerOpen(true);
  lsnApplyProgressDom({title:'Đang tìm mùa mới…', sub:'watchlist + films.db — không tải', frac:{cur:0,tot:1,label:'…'}}, true);
  lsnHint('Đang tìm mùa mới từ watchlist/DB (không tải)…');
  let d;
  try{
    d=await jpost('/api/hg/library/seasons/discover',{max_cores:16, expand:false});
  }catch(e){
    _lsnBusy=false; lsnShowProgress(false);
    lsnHint('Discover lỗi: '+(e.message||e)+' — cần restart server nếu route mới chưa nạp');
    return;
  }
  const ss=(d&&d.seasons)||{};
  _lsn={
    state:'done',
    auto:ss.auto||[], locked:ss.locked||[], failed:ss.failed||[], stopped:ss.stopped||[],
    declined:ss.declined||[], older:ss.older||[], removed:ss.removed||[], soon:ss.soon||[],
    held:ss.held||[], related:ss.related||[], big:ss.big||{albums:[]}
  };
  _lsnBusy=false;
  lsnRender();
  const n=num(d&&d.found_n)||((ss.held||[]).length+(ss.related||[]).length);
  const cores=num(d&&d.scanned_cores)||0;
  const wl=num(d&&d.watchlist_n)||0;
  lsnApplyProgressDom({
    title: n?('Tìm thấy '+n+' mùa/series chưa có'):'Không thấy mùa mới',
    sub:'quét '+cores+' bộ · watchlist '+wl+' · chỉ thông tin — + Thêm mới tải',
    frac:{cur:cores,tot:Math.max(cores,1),label:cores+'/'+cores}
  }, true);
  lsnHint(n
    ? ('Tìm thấy '+(d.held_n||0)+' mùa gần + '+(d.related_n||0)+' liên quan (watchlist '+wl+'). Chưa tải.')
    : ('Đã quét '+cores+' bộ từ watchlist/DB — không thấy mùa mới'));
}'''

paths = [
    Path(r"Z:\PinelineV5\static\ui\hongguo2.html"),
    Path(r"Z:\PinelineV4\hongguo2.html"),
    Path(r"Z:\PinelineV2\hongguo2.html"),
]
for p in paths:
    t = p.read_text(encoding="utf-8")
    if OLD not in t:
        if "library/seasons/discover" in t:
            print(p, "already discover API")
            continue
        raise SystemExit(f"old lsnDiscoverNew missing in {p}")
    p.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("patched", p)
print("ok")
