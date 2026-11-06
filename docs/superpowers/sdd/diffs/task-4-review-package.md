# Task 4 Review Package

## index3.html
- match `Chạy hàng chờ`: True
- match `btn-queue-run`: True
- match `function collectRunAllOpts`: True
- match `function runJobQueue`: True
- match `function stopJobQueue`: True
- match `function paintQueueStatus`: True
- match `paintQueueStatus\(\)`: True
### qbar snippet
```javascript
html+=`<div class="qbar" id="qbar">
    <button type="button" class="btn" onclick="groupSelected()" title="Gom các job đã tick thành 1 series">＋ Gom nhóm</button>
    <button type="button" class="btn" onclick="addSelectedToGroup()" title="Thêm job đã tick vào nhóm có sẵn">↳ Vào nhóm</button>
    <button type="button" class="btn" onclick="ungroupSelected()" title="Tách job đã tick khỏi nhóm">⤢ Tách</button>
    <span class="qhint">${listSel.size?listSel.size+' chọn':''}</span>
    <button type="button" class="btn pri" id="btn-queue-run" onclick="runJobQueue()" title="Chạy run-all tuần tự các job đã tick">▶ Chạy hàng chờ</button>
    <button type="button" class="btn stop" id="btn-queue-stop" o
```

### function collectRunAllOpts
```javascript
function collectRunAllOpts(){
  const audio_mode=(document.getElementById('auto-audio')||{value:'voice_bgm'}).value;
  const voice=(document.getElementById('auto-voice')||{}).value||null;
  const speed=parseFloat((document.getElementById('auto-speed')||{value:'1.0'}).value);
  const tts_engine=(document.getElementById('auto-engine')||{value:'vieneu'}).value;
  const asr_engine=(document.getElementById('auto-asr')||{value:'hybrid_fa'}).value;
  const ocr=!!(document.getElementById('auto-ocr')||{}).checked;
  const fit=(document.getElementById('auto-fit')||{checked:true}).checked;
  const resolution=(document.getElementById('auto-res')||{value:'source'}).value||'source';
  const translate_mode=(document.getElementById('auto-tr-mode')||{value:'batch'}).value||'batch';
  const zoom=parseFloat((document.getElementById('auto-zoom')||{value:'1.12'}).value)||1.12;
  const motion=!!(document.getElementById('auto-motion')||{checked:true}).checked;
  const lut=!!(document.getElementById('auto-lut')||{checked:true}).checked;
  const grain=(document.getElementById('auto-grain')||{value:'weak'}).value||'weak';
  const vbitrate=(document.getElementById('auto-vbit')||{value:'8M'}).value||'8M';
  const flip=(document.getElementById('auto-flip')||{value:''}).value||'';
  const frame=(document.getElementById('auto-frame')||{value:'off'}).value||'off';
  const brand_mode=(document.getElementById('auto-brand-mode')||{value:'off'}).value||'off';
  const brand_text=(document.getElementById('auto-brand-text')||{value:''}).value||'';
  const brand_logo=(document.getElementById('auto-brand-logo')||{value:'off'}).value||'off';
  const orig_vol=parseFloat((document.getElementById('auto-ovol')||{value:(audio_mode==='duck_bgm')?'0.22':'0.6'}).value);
  return {voice,speed,tts_engine,asr_engine,audio_mode,voice_vol:0.2,orig_vol,ocr,fit,resolution,translate_mode,
    zoom,motion,lut,grain,flip,frame,brand:brand_mode!=='off',brand_mode,brand_text,brand_logo,vbitrate};
}
```

### function runJobQueue
```javascript
function runJobQueue(){
  const ids=[...listSel];
  if(!ids.length){ alert('Tick ít nhất 1 job ở sidebar'); return; }
  if(!confirm(`Chạy hàng chờ ${ids.length} job (tuần tự run-all)?`)) return;
  const body={job_ids:ids,skip_done:true,...collectRunAllOpts()};
  if(!body.voice){ alert('Chọn giọng trên thanh 1-click trước'); return; }
  const r=await fetch('/api/queue/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json().catch(()=>({}));
  if(!r.ok){ alert(d.error||r.status); return; }
  alert(`Đã xếp ${(d.queued||[]).length} job`+(d.skipped_done&&d.skipped_done.length?` · bỏ qua done: ${d.skipped_done.length}`:''));
  void paintQueueStatus(); void refresh();
}
```

### function stopJobQueue
```javascript
function stopJobQueue(){
  await fetch('/api/queue/jobs/stop',{method:'POST'});
  void paintQueueStatus(); void refresh();
}
```

### function paintQueueStatus
```javascript
function paintQueueStatus(){
  try{
    const st=await (await fetch('/api/queue/jobs')).json();
    const el=document.getElementById('queue-status');
    if(!el) return;
    if(st.current||(st.queue&&st.queue.length)||st.worker){
      el.textContent=`Queue: ${st.current||'—'} · còn ${(st.queue||[]).length}`+(st.worker?' · chạy':'');
    } else {
      el.textContent='';
    }
    if(st.worker||(st.queue&&st.queue.length)||st.current){
      if(!_queuePollTimer) _queuePollTimer=setInterval(()=>{ void paintQueueStatus(); void refresh(); },2000);
    } else if(_queuePollTimer){
      clearInterval(_queuePollTimer); _queuePollTimer=null;
    }
  }catch(e){}
}
```


## index.html
- match `Chạy hàng chờ`: True
- match `btn-queue-run`: True
- match `function collectRunAllOpts`: True
- match `function runJobQueue`: True
- match `function stopJobQueue`: True
- match `function paintQueueStatus`: True
- match `paintQueueStatus\(\)`: True
### qbar snippet
```javascript
html+=`<div class="qbar" id="qbar">
    <button type="button" class="btn" onclick="groupSelected()" title="Gom các job đã tick thành 1 series">＋ Gom nhóm</button>
    <button type="button" class="btn" onclick="addSelectedToGroup()" title="Thêm job đã tick vào nhóm có sẵn">↳ Vào nhóm</button>
    <button type="button" class="btn" onclick="ungroupSelected()" title="Tách job đã tick khỏi nhóm">⤢ Tách</button>
    <span class="qhint">${listSel.size?listSel.size+' chọn':''}</span>
    <button type="button" class="btn pri" id="btn-queue-run" onclick="runJobQueue()" title="Chạy run-all tuần tự các job đã tick">▶ Chạy hàng chờ</button>
    <button type="button" class="btn stop" id="btn-queue-stop" o
```

### function collectRunAllOpts
```javascript
function collectRunAllOpts(){
  const audio_mode=(document.getElementById('auto-audio')||{value:'voice_bgm'}).value;
  const voice=(document.getElementById('auto-voice')||{}).value||null;
  const speed=parseFloat((document.getElementById('auto-speed')||{value:'1.0'}).value);
  const tts_engine=(document.getElementById('auto-engine')||{value:'vieneu'}).value;
  const asr_engine=(document.getElementById('auto-asr')||{value:'hybrid_fa'}).value;
  const ocr=!!(document.getElementById('auto-ocr')||{}).checked;
  const fit=(document.getElementById('auto-fit')||{checked:true}).checked;
  const resolution=(document.getElementById('auto-res')||{value:'source'}).value||'source';
  const translate_mode=(document.getElementById('auto-tr-mode')||{value:'batch'}).value||'batch';
  const zoom=parseFloat((document.getElementById('auto-zoom')||{value:'1.12'}).value)||1.12;
  const motion=!!(document.getElementById('auto-motion')||{checked:true}).checked;
  const lut=!!(document.getElementById('auto-lut')||{checked:true}).checked;
  const grain=(document.getElementById('auto-grain')||{value:'weak'}).value||'weak';
  const vbitrate=(document.getElementById('auto-vbit')||{value:'8M'}).value||'8M';
  const flip=(document.getElementById('auto-flip')||{value:''}).value||'';
  const frame=(document.getElementById('auto-frame')||{value:'off'}).value||'off';
  const brand_mode=(document.getElementById('auto-brand-mode')||{value:'off'}).value||'off';
  const brand_text=(document.getElementById('auto-brand-text')||{value:''}).value||'';
  const brand_logo=(document.getElementById('auto-brand-logo')||{value:'off'}).value||'off';
  const orig_vol=parseFloat((document.getElementById('auto-ovol')||{value:(audio_mode==='duck_bgm')?'0.22':'0.6'}).value);
  return {voice,speed,tts_engine,asr_engine,audio_mode,voice_vol:0.2,orig_vol,ocr,fit,resolution,translate_mode,
    zoom,motion,lut,grain,flip,frame,brand:brand_mode!=='off',brand_mode,brand_text,brand_logo,vbitrate};
}
```

### function runJobQueue
```javascript
function runJobQueue(){
  const ids=[...listSel];
  if(!ids.length){ alert('Tick ít nhất 1 job ở sidebar'); return; }
  if(!confirm(`Chạy hàng chờ ${ids.length} job (tuần tự run-all)?`)) return;
  const body={job_ids:ids,skip_done:true,...collectRunAllOpts()};
  if(!body.voice){ alert('Chọn giọng trên thanh 1-click trước'); return; }
  const r=await fetch('/api/queue/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json().catch(()=>({}));
  if(!r.ok){ alert(d.error||r.status); return; }
  alert(`Đã xếp ${(d.queued||[]).length} job`+(d.skipped_done&&d.skipped_done.length?` · bỏ qua done: ${d.skipped_done.length}`:''));
  void paintQueueStatus(); void refresh();
}
```

### function stopJobQueue
```javascript
function stopJobQueue(){
  await fetch('/api/queue/jobs/stop',{method:'POST'});
  void paintQueueStatus(); void refresh();
}
```

### function paintQueueStatus
```javascript
function paintQueueStatus(){
  try{
    const st=await (await fetch('/api/queue/jobs')).json();
    const el=document.getElementById('queue-status');
    if(!el) return;
    if(st.current||(st.queue&&st.queue.length)||st.worker){
      el.textContent=`Queue: ${st.current||'—'} · còn ${(st.queue||[]).length}`+(st.worker?' · chạy':'');
    } else {
      el.textContent='';
    }
    if(st.worker||(st.queue&&st.queue.length)||st.current){
      if(!_queuePollTimer) _queuePollTimer=setInterval(()=>{ void paintQueueStatus(); void refresh(); },2000);
    } else if(_queuePollTimer){
      clearInterval(_queuePollTimer); _queuePollTimer=null;
    }
  }catch(e){}
}
```

