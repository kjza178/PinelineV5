# Job Queue (Approach A) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tick nhiều job chưa xong → chạy run-all đủ pipeline **tuần tự** đến hết hàng, có Dừng và persist nhẹ.

**Architecture:** Module `job_queue.py` (state + worker daemon, pattern `hongguo_bridge.merge_queue_*`). Runner blocking inject từ `server.py`: download sync + `_gpu.submit(_auto_gpu)` + `Event.wait()` (không chồng GPU). API `/api/queue/jobs*`. UI `/ui3` reuse checkbox `listSel`.

**Tech Stack:** Python 3.11+, FastAPI/`server.py`, threading, `Manifest`, `_auto_gpu`, pytest.

## Global Constraints

- Một job GPU tại một thời điểm (queue worker chờ `_gpu`; không gọi `_auto_gpu` song song).
- Mỗi job: resume bước thiếu; xong = 5 stage `WIRED_STAGES` done **và** `output.mp4` size > 0.
- Job thiếu giọng → history failed, không kẹt queue.
- Persist: `work/_job_queue.json` (queue + opts + current); history chỉ RAM.
- Không phá `POST /api/jobs/{id}/run-all` / claim `__all__` hiện tại.
- Primary UI: `index3.html` (`/ui3`).

## File map

| File | Responsibility |
|------|----------------|
| `job_queue.py` | State, persist, worker loop, `set_runner` |
| `server.py` | `_queue_run_one`, `JobQueueReq`, 4 routes, wire `set_runner` |
| `tests/test_job_queue.py` | Unit queue add/skip/clear/order |
| `tests/test_job_queue_worker.py` | Worker order + stop với fake runner |
| `index3.html` | qbar buttons + JS enqueue/stop/poll |
| `index.html` | Mirror tối thiểu (cùng API) |
| Spec (đã có) | `docs/superpowers/specs/2026-09-24-job-queue-design.md` |

---


---

### Task 4: UI `/ui3` — reuse listSel + thanh queue

**Files:**
- Modify: `z:\Pineline\index3.html` (`#qbar` trong `renderList`, + JS)
- Modify: `z:\Pineline\index.html` (mirror cùng button/JS nếu sidebar tương tự)

**UI spec:**
1. Không thêm checkbox mới — dùng `listSel` / `.jchk`.
2. Trong `#qbar` thêm:

```html
<button type="button" class="btn pri" id="btn-queue-run" onclick="runJobQueue()" title="Chạy run-all tuần tự các job đã tick">▶ Chạy hàng chờ</button>
<button type="button" class="btn stop" id="btn-queue-stop" onclick="stopJobQueue()">⏹ Dừng hàng chờ</button>
<span class="qhint" id="queue-status"></span>
```

3. Poll status khi worker bật.

- [ ] **Step 1: Patch `renderList` qbar** trong `index3.html` — thêm 2 nút + `#queue-status` cạnh hint chọn.

- [ ] **Step 2: JS helpers** (cạnh `runAll`)

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

let _queuePollTimer=null;
async function paintQueueStatus(){
  try{
    const st=await (await fetch('/api/queue/jobs')).json();
    const el=document.getElementById('queue-status');
    if(!el) return;
    if(st.current|| (st.queue&&st.queue.length)||st.worker){
      el.textContent=`Queue: ${st.current||'—'} · còn ${(st.queue||[]).length}`+(st.worker?' · chạy':'');
    } else {
      el.textContent='';
    }
    if(st.worker || (st.queue&&st.queue.length) || st.current){
      if(!_queuePollTimer) _queuePollTimer=setInterval(()=>{ void paintQueueStatus(); void refresh(); }, 2000);
    } else if(_queuePollTimer){
      clearInterval(_queuePollTimer); _queuePollTimer=null;
    }
  }catch(e){}
}

async function runJobQueue(){
  const ids=[...listSel];
  if(!ids.length){ alert('Tick ít nhất 1 job ở sidebar'); return; }
  if(!confirm(`Chạy hàng chờ ${ids.length} job (tuần tự run-all)?`)) return;
  const body={job_ids:ids, skip_done:true, ...collectRunAllOpts()};
  if(!body.voice){ alert('Chọn giọng trên thanh 1-click trước'); return; }
  const r=await fetch('/api/queue/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json().catch(()=>({}));
  if(!r.ok){ alert(d.error||r.status); return; }
  alert(`Đã xếp ${ (d.queued||[]).length } job`+(d.skipped_done&&d.skipped_done.length?` · bỏ qua done: ${d.skipped_done.length}`:''));
  void paintQueueStatus(); void refresh();
}

async function stopJobQueue(){
  await fetch('/api/queue/jobs/stop',{method:'POST'});
  void paintQueueStatus(); void refresh();
}
```

Gọi `paintQueueStatus()` một lần trong `refresh()` cuối.

Refactor nhẹ (optional cùng task): `runAll` dùng `collectRunAllOpts()` để DRY — không bắt buộc.

- [ ] **Step 3: Manual UI**
  1. Mở `http://127.0.0.1:8800/ui3`
  2. Tick 2 job incomplete, chọn giọng + Âm nền
  3. **Chạy hàng chờ** → job1 `running`, job2 chưa claim `__all__` đến khi job1 mux done
  4. **Dừng hàng chờ** giữa chừng → queue trống, ffmpeg chết

- [ ] **Step 4: Mirror `index.html`** nếu còn `.qbar` / `listSel` tương tự; nếu không có listSel, thêm checkbox tối thiểu + cùng JS.

- [ ] **Step 5: Commit**

```bash
git add index3.html index.html
git commit -m "feat: UI multi-select sequential job queue on ui3"
```

---

