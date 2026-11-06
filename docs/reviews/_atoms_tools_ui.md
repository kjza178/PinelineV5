# Atoms: tools / desktop / restart + static UI JS

- **Date:** 2026-11-06
- **Scope:** module-level funcs via AST in `tools/**/*.py`, `app_desktop.py`, `restart_server.py`; JS names via regex on `static/ui/{index3,films_ui,hongguo,hongguo2,workflow}.html`
- **JS regex:** `function\s+(\w+)|(?:async\s+)?(\w+)\s*=\s*(?:async\s*)?\(`
- **JS note:** unique names, keyword false-positives skipped; cap **200** per file

## Counts

| Bucket | Files | Functions |
|---|---:|---:|
| Python (module-level) | 17 | 100 |
| HTML JS (unique names) | 5 | 634 |
| **Combined** | **22** | **734** |

- Cap hit (200): `static/ui/index3.html`

### Per-file counts

| File | Count |
|---|---:|
| `app_desktop.py` | 4 |
| `restart_server.py` | 8 |
| `tools/__init__.py` | 0 |
| `tools/context_studio/__init__.py` | 0 |
| `tools/context_studio/__main__.py` | 1 |
| `tools/context_studio/address_lexicon.py` | 4 |
| `tools/context_studio/analyzer.py` | 5 |
| `tools/context_studio/app_streamlit.py` | 0 |
| `tools/context_studio/character_mapper.py` | 10 |
| `tools/context_studio/exporter.py` | 1 |
| `tools/context_studio/schema.py` | 3 |
| `tools/context_studio/srt_io.py` | 4 |
| `tools/lib_check.py` | 9 |
| `tools/migrate_work.py` | 12 |
| `tools/pick_dirs_dialog.py` | 4 |
| `tools/preset_switcher.py` | 4 |
| `tools/test_channel.py` | 31 |
| `static/ui/index3.html` | 200 |
| `static/ui/films_ui.html` | 117 |
| `static/ui/hongguo.html` | 153 |
| `static/ui/hongguo2.html` | 156 |
| `static/ui/workflow.html` | 8 |

## Python — module-level functions (AST)

### `app_desktop.py` (4)

- L36: `def is_port_open`
- L44: `def start_backend`
- L78: `def wait_for_server`
- L87: `def main`

### `restart_server.py` (8)

- L61: `def _manifest_opts`
- L69: `def _tg`
- L78: `def _proc_env`
- L87: `def _precheck`
- L100: `def _requeue`
- L115: `def _start_server`
- L136: `def _restart_sidecar`
- L145: `def main`

### `tools/__init__.py` (0)

- _(none)_

### `tools/context_studio/__init__.py` (0)

- _(none)_

### `tools/context_studio/__main__.py` (1)

- L20: `def main`

### `tools/context_studio/address_lexicon.py` (4)

- L195: `def address_bank`
- L235: `def style_lock_policy`
- L265: `def merge_unique`
- L277: `def enrich_style_lock`

### `tools/context_studio/analyzer.py` (5)

- L12: `def _heuristic_analyze`
- L99: `def _sample_lines`
- L129: `def _llm_analyze`
- L245: `def analyze`
- L252: `def summarize`

### `tools/context_studio/app_streamlit.py` (0)

- _(none)_

### `tools/context_studio/character_mapper.py` (10)

- L27: `def _lock_mode`
- L43: `def _plausible_name`
- L48: `def _char_key`
- L52: `def _ensure_char`
- L86: `def infer_roles_from_segments`
- L150: `def build_relation_pronouns`
- L177: `def _matrix_from_pronouns`
- L192: `def sanitize_pronouns`
- L239: `def enrich_characters`
- L331: `def validate_pronouns`

### `tools/context_studio/exporter.py` (1)

- L9: `def write_pack`

### `tools/context_studio/schema.py` (3)

- L14: `def scan_number_flags`
- L51: `def empty_glossary_skeleton`
- L78: `def apply_style_lock_from_genre`

### `tools/context_studio/srt_io.py` (4)

- L14: `def _ts_to_sec`
- L19: `def parse_srt`
- L57: `def parse_asr_json`
- L78: `def load_segments`

### `tools/lib_check.py` (9)

- L30: `def resolve_title_vi`
- L74: `def find_source_video`
- L90: `def cut_sample`
- L168: `def add_to_yt_queue`
- L236: `def test_library_by_url`
- L265: `def scan_all_lib_from_yt_queue`
- L330: `def clear_samples`
- L357: `def list_yt_accounts`
- L379: `def batch_enqueue_untested_lib`

### `tools/migrate_work.py` (12)

- L42: `def log`
- L55: `def tg`
- L64: `def robocopy`
- L78: `def api`
- L86: `def api_retry`
- L99: `def running_stages`
- L115: `def procs`
- L124: `def kill_with_parent_cmd`
- L157: `def start_bat`
- L164: `def wait_http`
- L175: `def start_services_and_requeue`
- L200: `def main`

### `tools/pick_dirs_dialog.py` (4)

- L14: `def _nat_key`
- L19: `def _count_videos`
- L35: `def _list_children`
- L47: `def main`

### `tools/preset_switcher.py` (4)

- L30: `def get_active_preset`
- L55: `def list_available_presets`
- L75: `def is_model_ready`
- L125: `def switch_preset`

### `tools/test_channel.py` (31)

- L37: `def _safe_resolve_title_vi`
- L96: `def _utc_now`
- L100: `def _utc_now_plus_minutes`
- L104: `def _today_utc`
- L112: `def get_channel_limit_state`
- L125: `def mark_channel_limit_reached`
- L136: `def get_projects_health`
- L146: `def update_project_health`
- L160: `def verify_all_projects_health`
- L237: `def get_exhausted_projects`
- L246: `def mark_project_exhausted`
- L252: `def reset_exhausted_projects`
- L268: `def list_projects`
- L314: `def get_today_uploads_count`
- L389: `def get_status`
- L417: `def disconnect`
- L430: `def get_auth_url`
- L482: `def finish_oauth`
- L574: `def get_available_service`
- L606: `def get_read_service`
- L627: `def get_youtube_service`
- L635: `def upload_test_sample`
- L703: `def delete_test_video`
- L725: `def wait_and_check_test_video`
- L813: `def recheck_single`
- L892: `def check_and_process_pending_rechecks`
- L922: `def start_recheck_daemon`
- L944: `def run_full_test_for_season`
- L1045: `def _batch_worker`
- L1158: `def start_batch_test`
- L1187: `def get_batch_progress`

## HTML — JS function names (regex)

### `static/ui/index3.html` (200)

- `fmtSize`, `hhmm`, `parseUrls`, `updateUrlCount`
- `addJob`, `id`, `fpRenderSel`, `fpClearSel`
- `fpRemoveAt`, `fpSetPaths`, `pickMultiFolders`, `cur`
- `addSelectedFolders`, `target`, `nf`, `first`
- `addLocalPath`, `raw`, `addLocalFile`, `onload`
- `onerror`, `applyComposeUi`, `openQueue`, `setJobMode`
- `showCompose`, `closeCompose`, `select`, `toggleListSel`
- `jrow`, `start`, `moveBtns`, `renderList`
- `listStructSig`, `patchJrow`, `need`, `sortGroupSeries`
- `groupJobs`, `seasonOf`, `toggleGroup`, `groupSelected`
- `addSelectedToGroup`, `m`, `ungroupSelected`, `renameGroup`
- `dissolveGroup`, `mergeAllSeries`, `skip`, `defaultStep`
- `stages`, `selectStep`, `shellMidOk`, `autoBarHtml`
- `asrE`, `ttsE`, `logShellHtml`, `patchOneStep`
- `patchStepsShell`, `patchLogData`, `renderDetail`, `qh`
- `model`, `patchDetailLive`, `textContent`, `width`
- `fillAutoVoices`, `eng`, `list`, `autoEngineChanged`
- `e`, `panelSig`, `patchPanelLive`, `renderPanel`
- `stageCtrl`, `hasPartial`, `trD`, `ttsD`
- `asrD`, `dlD`, `mark`, `stepRow`
- `rawSt`, `isAsrSep`, `asrN`, `splitNote`
- `mini`, `buildLog`, `toggleLog`, `feedSentences`
- `toggle`, `loadArtifact`, `muxDone`, `durSec`
- `loadDynamicModels`, `isSel`, `artTranslate`, `zh`
- `runContextStudio`, `pollContextStudio`, `tick`, `showContextStudio`
- `chars`, `terms`, `tblTrans`, `ii`
- `initTransColResize`, `syncRail`, `tw`, `startDrag`
- `pct`, `up`, `focusMissLine`, `lineEditFocus`
- `lineEditInput`, `lineEditKey`, `lineEditSave`, `val`
- `orig`, `cleanZhSpam`, `viEditFocus`, `viEditInput`
- `viEditKey`, `viEditSave`, `artTts`, `clipRow`
- `ttsShowAll`, `fillTranslate`, `artOcr`, `artSeparate`
- `audioModeOptions`, `artMux`, `resLbl`, `fillMuxFrames`
- `files`, `fillMuxLogos`, `fillAutoFrames`, `fillAutoLogos`
- `muxModeChanged`, `display`, `autoPrefLoad`, `autoPrefSave`
- `autoPrefApply`, `autoPrefBind`, `queueBatchPush`, `v`
- `flushBatchPush`, `_btnFlash`, `loadBatchCfg`, `markPerJobDiff`
- `saveBatchCfg`, `autoAudioChanged`, `duck`, `loadVoices`
- `curEngine`, `curAsrEngine`, `st`, `saveAsrEngine`
- `asrEngineChanged`, `fillVoices`, `saveTtsEngine`, `engineChanged`
- `doTranslate`, `trMode`, `trModel`, `muxJob`
- `audio_mode`, `add_sub`, `fit`, `resolution`
- `flip`, `zVal`, `zoom`, `motion`
- `lut`, `grain`, `brand_mode`, `brand_text`
- `brand_logo`, `frame`, `vbitrate`, `regenClip`
- `assembleJob`, `spd`, `fn`, `cloneVoice`
- `name`, `msg`, `previewVoice`, `onended`
- `oncanplay`, `regenTts`, `fillTts`, `uploadAudio`
- `removeAudio`, `uploadSource`, `importSourcePath`, `path`
- `revealJob`, `splitJobParts`, `mergeJobParts`, `guardAct`

### `static/ui/films_ui.html` (117)

- `toast`, `tab`, `loadLib`, `stateLabel`
- `groupBlockBadge`, `formatRecheckTime`, `seasonBlockBadge`, `renderLib`
- `fBlock`, `openTestBlockModal`, `updateTestModalBadge`, `doModalRecheck`
- `closeTestBlockModal`, `doSkipCurrentLib`, `deleteLocalSeason`, `deleteEntireSeriesLocal`
- `deleteBlockedSeasonsOfCore`, `doDeleteCurrentLocalLib`, `doCutSample`, `doEnqueueSample`
- `doCheckTestUrl`, `setManualBlockStatus`, `checkTestChannelStatus`, `upBadge`
- `textContent`, `renderProjectsList`, `openTestChannelModal`, `closeTestChannelModal`
- `resetProjectQuota`, `avail`, `total`, `recheckTestChannelHealth`
- `startTestChannelOAuth`, `pollForTestChannelAuth`, `submitTestChannelCode`, `disconnectTestChannel`
- `testCheckedPrompt`, `startPinelineTestAllPrompt`, `doStartBatchTest`, `updateBatchProgressUI`
- `startBatchProgressPolling`, `poll`, `triggerRecheckPending`, `recheckOneSeason`
- `doPinelineDirectTestOne`, `clearSamplesCachePrompt`, `scanLibraryBlocks`, `act`
- `onSeriesPickChange`, `togglePickAllSeries`, `clearSeriesSelection`, `updateSeriesSelection`
- `addCheckedUnified`, `addCheckedSeries`, `addChecked`, `priorityCheckedSeries`
- `skipCheckedSeries`, `load`, `checkSingleBlock`, `batchCheckBlockPrompt`
- `checkAllUploadedBlock`, `promptDeleteSingle`, `batchDeletePrompt`, `closeDelModal`
- `execDeleteModal`, `promptPurge`, `purgeMissing`, `syncDb`
- `togglePickAll`, `clearPickAll`, `updateBatchBar`, `openMetaModal`
- `doRegenIndividualThumb`, `closeMetaModal`, `selectHookOpt`, `txt`
- `doFetchBaikeInfo`, `q`, `doGenerateMeta`, `doRenderThumbnail`
- `doCopyGptPrompt`, `copyText`, `copyThumbUrl`, `checkCanvaStatus`
- `openCanvaModal`, `closeCanvaModal`, `saveAndAuthCanva`, `doCreateCanvaDesign`
- `loadUploader`, `onUpAccountChange`, `onUpFilePicked`, `renderUploaderQueue`
- `renderUploaderHistory`, `submitEnqueueUpload`, `removeUploadItem`, `clearDoneUploads`
- `launchUploader`, `openPickFilmModal`, `renderPickFilmList`, `pickFilmForUpload`
- `openSettingsModal`, `closeSettingsModal`, `switchSettingsTab`, `loadSettings`
- `saveSettings`, `testLlmConn`, `testTelegramMsg`, `loadAutoPublishConfig`
- `saveAutoPublishConfig`, `triggerAutoPublishScan`, `quickUploadJob`, `buildIntegratedMasterPrompt`
- `badge`, `sub`, `doGenerateAuroraAiThumb`, `CURRENT_THUMB_URL`
- `pollAutoPubState`

### `static/ui/hongguo.html` (153)

- `exQ`, `jget`, `jpost`, `loadDlQueueFromStorage`
- `saveDlQueueToStorage`, `updateQueueBadges`, `onResCheckboxChange`, `bindResCheckboxes`
- `_qHandler`, `switchLeftTab`, `leftTab`, `hidden`
- `setRankBoard`, `rankBoard`, `reloadHotPane`, `setRankCat`
- `renderHotCards`, `loadRank`, `ensureExGenres`, `chips`
- `onclick`, `loadCatalog`, `fetchExplorer`, `items`
- `fillRankEpisodes`, `applyTitleVi`, `closeDetail`, `openBaikeDetailFromCard`
- `openBaikeDetail`, `tags`, `rel`, `setDetailRelChecked`
- `enqueueDetailMain`, `enqueueDetailRelated`, `dlDetailMain`, `dlDetailRelated`
- `ping`, `seasonStem`, `t`, `franchiseCore`
- `parseCnInt`, `s`, `seasonTimelineKey`, `cmpTimeline`
- `orderFranchiseItems`, `titleMark`, `formatTitleHtml`, `previewFromItem`
- `enqueueGroup`, `renderSeriesItem`, `mergeSeeds`, `expandQueries`
- `x`, `clientExpandSearch`, `ingest`, `addByPaste`
- `raw`, `item`, `stem`, `doSearch`
- `rejected`, `groups`, `toggleGroup`, `pickGroup`
- `selectAllVisible`, `selectedIds`, `updateDlBtn`, `dlGroup`
- `doDownload`, `doCancel`, `renderQueueList`, `removeFromDlQueue`
- `clearDlQueue`, `startDlQueue`, `_dlStatusSig`, `clearDlStatus`
- `applyDock`, `toggleDock`, `_dlLineTs`, `renderLog`
- `lsnHint`, `lsnTake`, `lsnItems`, `lsnList`
- `lsnN`, `lsnEps`, `lsnName`, `lsnMeta`
- `lsnBigAll`, `lsnBigAlbums`, `lsnGroups`, `lsnBusy`
- `lsnSugPill`, `lsnPlain`, `lsnAutoPill`, `lsnBadgeCount`
- `lsnUpdateBadge`, `lsnRender`, `lsnScores`, `lsnSubmit`
- `lsnDecline`, `lsnRefresh`, `lsnUpdateAll`, `lsnClick`
- `refreshStatus`, `textContent`, `dlLogLines`, `_loadLibSel`
- `_saveLibSel`, `_rememberLibSel`, `refreshLibrary`, `badge`
- `busy`, `mergeOneBtn`, `_pvEls`, `_pvMsg`
- `_pvStopCdn`, `_pvStopLib`, `_pvShape`, `_pvTabs`
- `previewLib`, `openPreview`, `openLibPreview`, `onloadedmetadata`
- `previewCatalog`, `openCatalogPreview`, `pvLoadCdn`, `onload`
- `closePreview`, `selectLib`, `selectLibPending`, `syncLibSelectAll`
- `libSelected`, `mergeNames`, `skip`, `mergeSelected`
- `deleteLibOne`, `deleteLibSelected`, `libPath`, `loadJobIndex`
- `vp`, `jobFor`, `jobLog`, `addJobs`
- `names`, `addJobsSelected`, `mergeAllLibrary`, `clearMergeQ`
- `refreshMerge`, `q`, `pct`, `mergeHist`
- `refreshAll`

### `static/ui/hongguo2.html` (156)

- `exQ`, `jget`, `jpost`, `loadDlQueueFromStorage`
- `saveDlQueueToStorage`, `updateQueueBadges`, `setCtaStatus`, `onResCheckboxChange`
- `bindResCheckboxes`, `_qHandler`, `switchLeftTab`, `setDiscoverMode`
- `discoverMode`, `setOpsQueue`, `opsQueue`, `hidden`
- `setRankBoard`, `reloadHotPane`, `setRankCat`, `renderHotCards`
- `loadRank`, `ensureExGenres`, `chips`, `onclick`
- `loadCatalog`, `fetchExplorer`, `items`, `fillRankEpisodes`
- `applyTitleVi`, `closeDetail`, `openBaikeDetailFromCard`, `openBaikeDetail`
- `tags`, `rel`, `setDetailRelChecked`, `enqueueDetailMain`
- `enqueueDetailRelated`, `dlDetailMain`, `dlDetailRelated`, `ping`
- `seasonStem`, `t`, `franchiseCore`, `parseCnInt`
- `s`, `seasonTimelineKey`, `cmpTimeline`, `orderFranchiseItems`
- `titleMark`, `formatTitleHtml`, `previewFromItem`, `enqueueGroup`
- `renderSeriesItem`, `mergeSeeds`, `expandQueries`, `x`
- `clientExpandSearch`, `ingest`, `addByPaste`, `raw`
- `item`, `stem`, `doSearch`, `rejected`
- `groups`, `toggleGroup`, `pickGroup`, `selectAllVisible`
- `selectedIds`, `updateDlBtn`, `dlGroup`, `doDownload`
- `doCancel`, `renderQueueList`, `removeFromDlQueue`, `clearDlQueue`
- `startDlQueue`, `_dlStatusSig`, `clearDlStatus`, `applyDock`
- `toggleDock`, `_dlLineTs`, `renderLog`, `lsnHint`
- `lsnTake`, `lsnItems`, `lsnList`, `lsnN`
- `lsnEps`, `lsnName`, `lsnMeta`, `lsnBigAll`
- `lsnBigAlbums`, `lsnGroups`, `lsnBusy`, `lsnSugPill`
- `lsnPlain`, `lsnAutoPill`, `lsnBadgeCount`, `lsnUpdateBadge`
- `lsnRender`, `lsnScores`, `lsnSubmit`, `lsnDecline`
- `lsnRefresh`, `lsnUpdateAll`, `lsnClick`, `refreshStatus`
- `textContent`, `dlLogLines`, `_loadLibSel`, `_saveLibSel`
- `_rememberLibSel`, `refreshLibrary`, `badge`, `busy`
- `mergeOneBtn`, `_pvEls`, `_pvMsg`, `_pvStopCdn`
- `_pvStopLib`, `_pvShape`, `_pvTabs`, `previewLib`
- `openPreview`, `openLibPreview`, `onloadedmetadata`, `previewCatalog`
- `openCatalogPreview`, `pvLoadCdn`, `onload`, `closePreview`
- `selectLib`, `selectLibPending`, `syncLibSelectAll`, `libSelected`
- `mergeNames`, `skip`, `mergeSelected`, `deleteLibOne`
- `deleteLibSelected`, `libPath`, `loadJobIndex`, `vp`
- `jobFor`, `jobLog`, `addJobs`, `names`
- `addJobsSelected`, `mergeAllLibrary`, `clearMergeQ`, `refreshMerge`
- `q`, `pct`, `mergeHist`, `refreshAll`

### `static/ui/workflow.html` (8)

- `resizeCanvas`, `drawCanvas`, `spacing`, `addLog`
- `selectStage`, `resetSimulation`, `startSimulation`, `runNextStep`

