# API routes

_Sinh tự động bởi `scripts/brain_build.py` lúc 2026-11-11 02:38. Đừng sửa tay — chạy lại script._


**340 route.** ⚠️ = cùng method+path khai ở >1 nơi.

| Path | Method | Module | Handler | Dòng |
|---|---|---|---|---:|
| `/` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `index` | 46 |
| `/` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `index` | 43 |
| `/api/agent/av-sync/heal-batch` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_av_sync_heal_batch` | 626 |
| `/api/agent/av-sync/heal-batch` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_av_sync_heal_batch` | 633 |
| `/api/agent/av-sync/scan` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_av_sync_scan` | 615 |
| `/api/agent/av-sync/scan` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_av_sync_scan` | 622 |
| `/api/agent/brain/tick` | POST | [server](../modules/server.md) | `api_agent_brain_tick` | 6557 |
| `/api/agent/chat` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_chat` | 444 |
| `/api/agent/chat` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_chat` | 450 |
| `/api/agent/confirm` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_confirm` | 475 |
| `/api/agent/confirm` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_confirm` | 482 |
| `/api/agent/heal-failed` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_heal_failed` | 506 |
| `/api/agent/heal-failed` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_heal_failed` | 513 |
| `/api/agent/jobs/{job_id}/av-sync` ⚠️ | GET | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_av_sync` | 588 |
| `/api/agent/jobs/{job_id}/av-sync` ⚠️ | GET | [routes_agent](../modules/routes_agent.md) | `api_agent_av_sync` | 595 |
| `/api/agent/jobs/{job_id}/av-sync-heal` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_av_sync_heal` | 597 |
| `/api/agent/jobs/{job_id}/av-sync-heal` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_av_sync_heal` | 604 |
| `/api/agent/jobs/{job_id}/qa-gate` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_qa_gate` | 540 |
| `/api/agent/jobs/{job_id}/qa-gate` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_qa_gate` | 547 |
| `/api/agent/jobs/{job_id}/reset-state` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_reset_state` | 559 |
| `/api/agent/jobs/{job_id}/reset-state` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_reset_state` | 566 |
| `/api/agent/jobs/{job_id}/review-diff` ⚠️ | GET | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_review_diff` | 531 |
| `/api/agent/jobs/{job_id}/review-diff` ⚠️ | GET | [routes_agent](../modules/routes_agent.md) | `api_agent_review_diff` | 538 |
| `/api/agent/pending` ⚠️ | GET | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_pending` | 470 |
| `/api/agent/pending` ⚠️ | GET | [routes_agent](../modules/routes_agent.md) | `api_agent_pending` | 477 |
| `/api/agent/resume/{job_id}` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_resume` | 302 |
| `/api/agent/resume/{job_id}` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_resume` | 308 |
| `/api/agent/review/{job_id}` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_review` | 297 |
| `/api/agent/review/{job_id}` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_review` | 303 |
| `/api/agent/scan-failed` ⚠️ | GET | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_scan_failed` | 496 |
| `/api/agent/scan-failed` ⚠️ | GET | [routes_agent](../modules/routes_agent.md) | `api_agent_scan_failed` | 503 |
| `/api/agent/status` ⚠️ | GET | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_status` | 435 |
| `/api/agent/status` ⚠️ | GET | [routes_agent](../modules/routes_agent.md) | `api_agent_status` | 441 |
| `/api/agent/watch-once` ⚠️ | POST | [http_routes.routes_agent](../modules/http_routes.routes_agent.md) | `api_agent_watch_once` | 569 |
| `/api/agent/watch-once` ⚠️ | POST | [routes_agent](../modules/routes_agent.md) | `api_agent_watch_once` | 576 |
| `/api/auto-publish/config` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_get_config` | 472 |
| `/api/auto-publish/config` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_save_config` | 479 |
| `/api/auto-publish/scan` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_scan` | 515 |
| `/api/auto-publish/state` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_status` | 527 |
| `/api/auto-publish/status` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_status` | 527 |
| `/api/auto-publish/trigger` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_trigger` | 487 |
| `/api/brand-logos` | GET | [server](../modules/server.md) | `list_brand_logos` | 5539 |
| `/api/canva/auth-url` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_auth_url` | 551 |
| `/api/canva/callback` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_callback` | 562 |
| `/api/canva/config` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_save_config` | 590 |
| `/api/canva/create` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_create` | 602 |
| `/api/canva/status` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_status` | 538 |
| `/api/clone-voice` | POST | [server](../modules/server.md) | `clone_voice` | 5666 |
| `/api/cookies` | GET | [server](../modules/server.md) | `cookies_status` | 5180 |
| `/api/cookies` | POST | [server](../modules/server.md) | `import_cookies` | 5206 |
| `/api/disk` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `api_disk` | 82 |
| `/api/disk` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `api_disk` | 90 |
| `/api/frames` | GET | [server](../modules/server.md) | `list_frames` | 5529 |
| `/api/fs/list-dirs` | GET | [server](../modules/server.md) | `api_fs_list_dirs` | 2995 |
| `/api/fs/pick-dir` | POST | [server](../modules/server.md) | `api_fs_pick_dir` | 3049 |
| `/api/fs/pick-dirs` | POST | [server](../modules/server.md) | `api_fs_pick_dirs` | 3123 |
| `/api/hg/baike-info` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_baike_info` | 203 |
| `/api/hg/baike-info` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_baike_info` | 211 |
| `/api/hg/baike-search` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_baike_search` | 188 |
| `/api/hg/baike-search` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_baike_search` | 196 |
| `/api/hg/cancel` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_cancel` | 319 |
| `/api/hg/cancel` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_cancel` | 327 |
| `/api/hg/catalog` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_catalog` | 457 |
| `/api/hg/catalog` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_catalog` | 465 |
| `/api/hg/downloads/cancel` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_dl_cancel_one` | 341 |
| `/api/hg/downloads/cancel` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_dl_cancel_one` | 349 |
| `/api/hg/downloads/clear-finished` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_dl_clear_finished` | 330 |
| `/api/hg/downloads/clear-finished` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_dl_clear_finished` | 338 |
| `/api/hg/downloads/open-folder` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_dl_open_folder` | 387 |
| `/api/hg/downloads/open-folder` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_dl_open_folder` | 395 |
| `/api/hg/downloads/remove` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_dl_remove` | 357 |
| `/api/hg/downloads/remove` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_dl_remove` | 365 |
| `/api/hg/downloads/retry` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_dl_retry` | 372 |
| `/api/hg/downloads/retry` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_dl_retry` | 380 |
| `/api/hg/feed` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_feed` | 475 |
| `/api/hg/feed` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_feed` | 483 |
| `/api/hg/genres` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_genres` | 446 |
| `/api/hg/genres` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_genres` | 454 |
| `/api/hg/img` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_img` | 672 |
| `/api/hg/img` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_img` | 680 |
| `/api/hg/library` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library` | 549 |
| `/api/hg/library` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_library` | 557 |
| `/api/hg/library/delete` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library_delete` | 744 |
| `/api/hg/library/delete` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_library_delete` | 769 |
| `/api/hg/library/open` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library_open` | 734 |
| `/api/hg/library/open` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_library_open` | 759 |
| `/api/hg/library/preview` ⚠️ | GET|HEAD | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library_preview` | 647 |
| `/api/hg/library/preview` ⚠️ | GET|HEAD | [routes_hg](../modules/routes_hg.md) | `hg_library_preview` | 655 |
| `/api/hg/library/seasons/decline` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_seasons_decline` | 782 |
| `/api/hg/library/seasons/decline` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_seasons_decline` | 807 |
| `/api/hg/library/seasons/discover` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_seasons_discover` | 795 |
| `/api/hg/library/seasons/discover` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_seasons_discover` | 820 |
| `/api/hg/library/update` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library_update` | 769 |
| `/api/hg/library/update` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_library_update` | 794 |
| `/api/hg/library/update-info` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library_update_info` | 757 |
| `/api/hg/library/update-info` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_library_update_info` | 782 |
| `/api/hg/library/watchlist` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_library_watchlist` | 815 |
| `/api/hg/library/watchlist` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_library_watchlist` | 840 |
| `/api/hg/license/key` ⚠️ | DELETE | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_license_key_clear` | 965 |
| `/api/hg/license/key` ⚠️ | DELETE | [routes_hg](../modules/routes_hg.md) | `hg_license_key_clear` | 990 |
| `/api/hg/license/key` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_license_key` | 949 |
| `/api/hg/license/key` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_license_key` | 974 |
| `/api/hg/license/prove` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_license_prove` | 976 |
| `/api/hg/license/prove` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_license_prove` | 1001 |
| `/api/hg/license/status` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_license_status` | 937 |
| `/api/hg/license/status` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_license_status` | 962 |
| `/api/hg/merge` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_merge` | 710 |
| `/api/hg/merge` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_merge` | 735 |
| `/api/hg/merge-queue` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_merge_queue` | 722 |
| `/api/hg/merge-queue` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_merge_queue` | 747 |
| `/api/hg/merge-queue/clear` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_merge_queue_clear` | 728 |
| `/api/hg/merge-queue/clear` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_merge_queue_clear` | 753 |
| `/api/hg/ping` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_ping` | 120 |
| `/api/hg/ping` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_ping` | 128 |
| `/api/hg/playback/stream` ⚠️ | GET|HEAD | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_playback_stream` | 631 |
| `/api/hg/playback/stream` ⚠️ | GET|HEAD | [routes_hg](../modules/routes_hg.md) | `hg_playback_stream` | 639 |
| `/api/hg/poster` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_poster` | 693 |
| `/api/hg/poster` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_poster` | 701 |
| `/api/hg/preview` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_preview` | 560 |
| `/api/hg/preview` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_preview` | 568 |
| `/api/hg/preview/job` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_preview_job` | 619 |
| `/api/hg/preview/job` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_preview_job` | 627 |
| `/api/hg/preview/start` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_preview_start` | 598 |
| `/api/hg/preview/start` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_preview_start` | 606 |
| `/api/hg/rank` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_rank` | 415 |
| `/api/hg/rank` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_rank` | 423 |
| `/api/hg/rank-episodes` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_rank_episodes` | 521 |
| `/api/hg/rank-episodes` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_rank_episodes` | 529 |
| `/api/hg/resolve` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_resolve` | 171 |
| `/api/hg/resolve` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_resolve` | 179 |
| `/api/hg/search` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_search` | 158 |
| `/api/hg/search` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_search` | 166 |
| `/api/hg/series/{series_id}` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_series` | 273 |
| `/api/hg/series/{series_id}` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_series` | 281 |
| `/api/hg/series/{series_id}/qualities` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_series_qualities` | 296 |
| `/api/hg/series/{series_id}/qualities` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_series_qualities` | 304 |
| `/api/hg/series/{series_id}/seasons` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_series_seasons` | 284 |
| `/api/hg/series/{series_id}/seasons` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_series_seasons` | 292 |
| `/api/hg/settings` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_settings` | 128 |
| `/api/hg/settings` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_settings` | 136 |
| `/api/hg/settings` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_settings_update` | 140 |
| `/api/hg/settings` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_settings_update` | 148 |
| `/api/hg/status` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_status` | 308 |
| `/api/hg/status` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_status` | 316 |
| `/api/hg/submit` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_submit` | 399 |
| `/api/hg/submit` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_submit` | 407 |
| `/api/hg/translate-titles` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_translate_titles` | 537 |
| `/api/hg/translate-titles` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `hg_translate_titles` | 545 |
| `/api/hg/web-search` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `hg_web_search` | 250 |
| `/api/hg/web-search` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `hg_web_search` | 258 |
| `/api/jobs` | GET | [server](../modules/server.md) | `list_jobs` | 5252 |
| `/api/jobs` | POST | [server](../modules/server.md) | `create_job` | 2441 |
| `/api/jobs/group` | POST | [server](../modules/server.md) | `jobs_group` | 2532 |
| `/api/jobs/local` | POST | [server](../modules/server.md) | `create_local_job_upload` | 3189 |
| `/api/jobs/local-batch` | POST | [server](../modules/server.md) | `create_local_job_batch` | 2912 |
| `/api/jobs/local-path` | POST | [server](../modules/server.md) | `create_local_job_path` | 2841 |
| `/api/jobs/{job_id}` | DELETE | [server](../modules/server.md) | `delete_job` | 6329 |
| `/api/jobs/{job_id}` | GET | [server](../modules/server.md) | `job_detail` | 5266 |
| `/api/jobs/{job_id}/apply-alt` | POST | [server](../modules/server.md) | `apply_alt_pick` | 5055 |
| `/api/jobs/{job_id}/asr-engine` | POST | [server](../modules/server.md) | `set_asr_engine` | 4515 |
| `/api/jobs/{job_id}/asr-select` | POST | [server](../modules/server.md) | `select_asr_source` | 4831 |
| `/api/jobs/{job_id}/asr-sources` | GET | [server](../modules/server.md) | `list_asr_sources` | 4813 |
| `/api/jobs/{job_id}/assemble` | POST | [server](../modules/server.md) | `assemble_job` | 6182 |
| `/api/jobs/{job_id}/audio` | DELETE | [server](../modules/server.md) | `delete_audio` | 6014 |
| `/api/jobs/{job_id}/audio` | POST | [server](../modules/server.md) | `upload_audio` | 5980 |
| `/api/jobs/{job_id}/context-studio` | GET | [server](../modules/server.md) | `get_context_studio` | 4919 |
| `/api/jobs/{job_id}/context-studio` | POST | [server](../modules/server.md) | `run_context_studio_api` | 4975 |
| `/api/jobs/{job_id}/file/{path:path}` | GET | [server](../modules/server.md) | `job_file` | 6276 |
| `/api/jobs/{job_id}/hardsub-asr` | GET | [server](../modules/server.md) | `get_hardsub_asr` | 5144 |
| `/api/jobs/{job_id}/hardsub-asr` | POST | [server](../modules/server.md) | `run_hardsub_asr_api` | 5114 |
| `/api/jobs/{job_id}/mark-done` | POST | [server](../modules/server.md) | `mark_job_done` | 3933 |
| `/api/jobs/{job_id}/merge-parts` | POST | [server](../modules/server.md) | `api_merge_job_parts` | 6237 |
| `/api/jobs/{job_id}/mux` | POST | [server](../modules/server.md) | `mux_job` | 6147 |
| `/api/jobs/{job_id}/reveal` | POST | [server](../modules/server.md) | `reveal_job` | 6248 |
| `/api/jobs/{job_id}/run-all` | POST | [server](../modules/server.md) | `run_all` | 4196 |
| `/api/jobs/{job_id}/run/{stage}` | POST | [server](../modules/server.md) | `run_stage` | 3849 |
| `/api/jobs/{job_id}/script-clean-spam` | POST | [server](../modules/server.md) | `clean_script_spam` | 4142 |
| `/api/jobs/{job_id}/script-line` | POST | [server](../modules/server.md) | `edit_script_line` | 4038 |
| `/api/jobs/{job_id}/source` | POST | [server](../modules/server.md) | `upload_source` | 5902 |
| `/api/jobs/{job_id}/source-path` | POST | [server](../modules/server.md) | `import_source_path` | 5940 |
| `/api/jobs/{job_id}/split-parts` | POST | [server](../modules/server.md) | `api_split_job_parts` | 6226 |
| `/api/jobs/{job_id}/split-plan` | GET | [server](../modules/server.md) | `get_split_plan` | 6204 |
| `/api/jobs/{job_id}/srt/{lang}` | GET | [server](../modules/server.md) | `job_srt` | 5867 |
| `/api/jobs/{job_id}/start` | POST | [server](../modules/server.md) | `start_job` | 3227 |
| `/api/jobs/{job_id}/stop` | POST | [server](../modules/server.md) | `stop_job` | 3912 |
| `/api/jobs/{job_id}/translate` | POST | [server](../modules/server.md) | `retranslate_job` | 6075 |
| `/api/jobs/{job_id}/translate-alts` | GET | [server](../modules/server.md) | `get_translate_alts` | 5010 |
| `/api/jobs/{job_id}/translate-alts` | POST | [server](../modules/server.md) | `run_translate_alts_api` | 5029 |
| `/api/jobs/{job_id}/translate-fill` | POST | [server](../modules/server.md) | `translate_fill` | 3991 |
| `/api/jobs/{job_id}/tts` | POST | [server](../modules/server.md) | `regen_tts` | 5756 |
| `/api/jobs/{job_id}/tts-clip` | POST | [server](../modules/server.md) | `regen_clip` | 5850 |
| `/api/jobs/{job_id}/tts-voice` | POST | [server](../modules/server.md) | `set_tts_voice` | 4181 |
| `/api/jobs/{job_id}/tts-wav-ok` | GET | [server](../modules/server.md) | `tts_wav_ok` | 5740 |
| `/api/jobs/{job_id}/video` | GET|HEAD | [server](../modules/server.md) | `job_video` | 5437 |
| `/api/llm/models` | GET | [server](../modules/server.md) | `get_available_llm_models` | 6571 |
| `/api/meta/generate` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_generate` | 833 |
| `/api/meta/generate` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `meta_generate` | 858 |
| `/api/meta/generate-title` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_generate_title` | 852 |
| `/api/meta/generate-title` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `meta_generate_title` | 877 |
| `/api/meta/series-info` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_series_info` | 921 |
| `/api/meta/series-info` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `meta_series_info` | 946 |
| `/api/meta/thumbnail` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_thumbnail_get` | 912 |
| `/api/meta/thumbnail` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `meta_thumbnail_get` | 937 |
| `/api/meta/thumbnail` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_thumbnail` | 882 |
| `/api/meta/thumbnail` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `meta_thumbnail` | 907 |
| `/api/models` | GET | [server](../modules/server.md) | `get_available_llm_models` | 6571 |
| `/api/queue/group` | POST | [server](../modules/server.md) | `jobs_group` | 2532 |
| `/api/queue/jobs` | GET | [server](../modules/server.md) | `api_queue_jobs_state` | 2803 |
| `/api/queue/jobs` | POST | [server](../modules/server.md) | `api_queue_jobs_add` | 2648 |
| `/api/queue/jobs/clear` | POST | [server](../modules/server.md) | `api_queue_jobs_clear` | 2836 |
| `/api/queue/jobs/group` | POST | [server](../modules/server.md) | `api_queue_jobs_add_group` | 2665 |
| `/api/queue/jobs/move` | POST | [server](../modules/server.md) | `api_queue_jobs_move` | 2774 |
| `/api/queue/jobs/opts` | POST | [server](../modules/server.md) | `api_queue_jobs_opts` | 2681 |
| `/api/queue/jobs/remove` | POST | [server](../modules/server.md) | `api_queue_jobs_remove` | 2702 |
| `/api/queue/jobs/reorder` | POST | [server](../modules/server.md) | `api_queue_jobs_reorder` | 2790 |
| `/api/queue/jobs/sort` | POST | [server](../modules/server.md) | `api_queue_jobs_sort` | 2765 |
| `/api/queue/jobs/stop` | POST | [server](../modules/server.md) | `api_queue_jobs_stop` | 2831 |
| `/api/settings` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `get_all_settings` | 47 |
| `/api/settings` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `update_settings` | 107 |
| `/api/settings/test-llm` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `test_llm_conn` | 190 |
| `/api/settings/test-telegram` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `test_telegram_msg` | 154 |
| `/api/uploader/clear-done` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `clear_done_uploads` | 398 |
| `/api/uploader/clear-skipped` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `uploader_clear_skipped` | 449 |
| `/api/uploader/enqueue` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `enqueue_upload` | 329 |
| `/api/uploader/launch` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `launch_yt_uploader_process` | 408 |
| `/api/uploader/move` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `uploader_move_item` | 455 |
| `/api/uploader/remove` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `remove_upload_item` | 376 |
| `/api/uploader/settings` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `uploader_save_settings` | 461 |
| `/api/uploader/skip` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `uploader_skip_item` | 437 |
| `/api/uploader/skip-current` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `uploader_skip_current` | 443 |
| `/api/uploader/status` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `get_uploader_status` | 293 |
| `/api/voice-sample` | GET | [server](../modules/server.md) | `voice_sample` | 5699 |
| `/api/voices` | GET | [server](../modules/server.md) | `list_voices` | 5521 |
| `/api/x` | GET | [scripts.check_batch2](../modules/scripts.check_batch2.md) | `_x` | 60 |
| `/auto-publish/config` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_get_config` | 472 |
| `/auto-publish/config` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_save_config` | 479 |
| `/auto-publish/scan` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_scan` | 515 |
| `/auto-publish/state` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_status` | 527 |
| `/auto-publish/status` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_status` | 527 |
| `/auto-publish/trigger` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `auto_publish_trigger` | 487 |
| `/canva/auth-url` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_auth_url` | 551 |
| `/canva/callback` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_callback` | 562 |
| `/canva/config` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_save_config` | 590 |
| `/canva/create` | POST | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_create` | 602 |
| `/canva/status` | GET | [http_routes.routes_uploader_settings](../modules/http_routes.routes_uploader_settings.md) | `canva_status` | 538 |
| `/film` | GET | [routes_ui](../modules/routes_ui.md) | `ui_films` | 92 |
| `/films` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `list_films` | 39 |
| `/films` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `list_films` | 39 |
| `/films` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui_films` | 92 |
| `/films.csv` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `export_films_csv` | 68 |
| `/films.csv` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `export_films_csv` | 68 |
| `/films/check-block` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `check_block_films` | 133 |
| `/films/check-block` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `check_block_films` | 133 |
| `/films/check-block-all` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `check_block_all` | 146 |
| `/films/check-block-all` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `check_block_all` | 146 |
| `/films/delete` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `delete_films` | 110 |
| `/films/delete` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `delete_films` | 110 |
| `/films/purge-missing` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `purge_missing` | 126 |
| `/films/purge-missing` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `purge_missing` | 126 |
| `/films/sync` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `sync_films` | 101 |
| `/films/sync` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `sync_films` | 101 |
| `/films/ui` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `films_ui` | 31 |
| `/films/ui` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `films_ui` | 31 |
| `/films/ui` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui_films` | 92 |
| `/films/{job_id}` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `get_film` | 93 |
| `/films/{job_id}` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `get_film` | 93 |
| `/hongguo` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui_hongguo` | 84 |
| `/hongguo` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui_hongguo` | 78 |
| `/hongguo2` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui_hongguo2` | 89 |
| `/hongguo2` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui_hongguo2` | 84 |
| `/index3.html` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui3` | 59 |
| `/index3.html` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui3` | 64 |
| `/index4.html` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui4` | 65 |
| `/index4.html` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui4` | 71 |
| `/library` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `get_library` | 160 |
| `/library` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `get_library` | 160 |
| `/library/accounts` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_accounts` | 169 |
| `/library/accounts` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `library_accounts` | 169 |
| `/library/action` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_action` | 178 |
| `/library/action` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_action` | 178 |
| `/library/clear-samples` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_clear_samples` | 207 |
| `/library/clear-samples` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_clear_samples` | 207 |
| `/library/cut-sample` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_cut_sample` | 216 |
| `/library/cut-sample` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_cut_sample` | 216 |
| `/library/enqueue-test` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_enqueue_test` | 227 |
| `/library/enqueue-test` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_enqueue_test` | 227 |
| `/library/scan-queue` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_scan_queue` | 249 |
| `/library/scan-queue` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_scan_queue` | 249 |
| `/library/set-block-status` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_set_block_status` | 198 |
| `/library/set-block-status` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_set_block_status` | 198 |
| `/library/test-url` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `library_test_url` | 239 |
| `/library/test-url` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `library_test_url` | 239 |
| `/library/ui` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `films_ui` | 31 |
| `/library/ui` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `films_ui` | 31 |
| `/meta/generate` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_generate` | 833 |
| `/meta/generate` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `meta_generate` | 858 |
| `/meta/generate-title` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_generate_title` | 852 |
| `/meta/generate-title` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `meta_generate_title` | 877 |
| `/meta/series-info` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_series_info` | 921 |
| `/meta/series-info` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `meta_series_info` | 946 |
| `/meta/thumbnail` ⚠️ | GET | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_thumbnail_get` | 912 |
| `/meta/thumbnail` ⚠️ | GET | [routes_hg](../modules/routes_hg.md) | `meta_thumbnail_get` | 937 |
| `/meta/thumbnail` ⚠️ | POST | [http_routes.routes_hg](../modules/http_routes.routes_hg.md) | `meta_thumbnail` | 882 |
| `/meta/thumbnail` ⚠️ | POST | [routes_hg](../modules/routes_hg.md) | `meta_thumbnail` | 907 |
| `/studio` | GET | [routes_ui](../modules/routes_ui.md) | `ui_studio` | 99 |
| `/studio/ui` | GET | [routes_ui](../modules/routes_ui.md) | `ui_studio` | 99 |
| `/test-channel/auth-url` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_auth_url` | 278 |
| `/test-channel/auth-url` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `tc_auth_url` | 278 |
| `/test-channel/batch-progress` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_batch_progress` | 354 |
| `/test-channel/batch-progress` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `tc_batch_progress` | 354 |
| `/test-channel/batch-start` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_batch_start` | 344 |
| `/test-channel/batch-start` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `tc_batch_start` | 344 |
| `/test-channel/callback` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_callback` | 289 |
| `/test-channel/callback` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `tc_callback` | 289 |
| `/test-channel/disconnect` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_disconnect` | 323 |
| `/test-channel/disconnect` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `tc_disconnect` | 323 |
| `/test-channel/finish-auth` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_finish_auth` | 311 |
| `/test-channel/finish-auth` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `tc_finish_auth` | 311 |
| `/test-channel/recheck-health` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_recheck_health` | 272 |
| `/test-channel/recheck-health` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `tc_recheck_health` | 272 |
| `/test-channel/recheck-one` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_recheck_one` | 359 |
| `/test-channel/recheck-one` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `tc_recheck_one` | 359 |
| `/test-channel/recheck-pending` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_recheck_pending` | 366 |
| `/test-channel/recheck-pending` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `tc_recheck_pending` | 366 |
| `/test-channel/reset-quota` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_reset_quota` | 267 |
| `/test-channel/reset-quota` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `tc_reset_quota` | 267 |
| `/test-channel/status` ⚠️ | GET | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_status` | 262 |
| `/test-channel/status` ⚠️ | GET | [routes_films](../modules/routes_films.md) | `tc_status` | 262 |
| `/test-channel/test-one` ⚠️ | POST | [http_routes.routes_films](../modules/http_routes.routes_films.md) | `tc_test_one` | 329 |
| `/test-channel/test-one` ⚠️ | POST | [routes_films](../modules/routes_films.md) | `tc_test_one` | 329 |
| `/ui` | GET | [scripts.check_batch2](../modules/scripts.check_batch2.md) | `_ui` | 65 |
| `/ui-hg` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui_hongguo` | 84 |
| `/ui-hg` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui_hongguo` | 78 |
| `/ui3` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui3` | 59 |
| `/ui3` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui3` | 64 |
| `/ui4` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui4` | 65 |
| `/ui4` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui4` | 71 |
| `/v5-map` ⚠️ | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui_v5_map` | 100 |
| `/v5-map` ⚠️ | GET | [routes_ui](../modules/routes_ui.md) | `ui_v5_map` | 105 |
| `/workflow` | GET | [http_routes.routes_ui](../modules/http_routes.routes_ui.md) | `ui_workflow` | 95 |
