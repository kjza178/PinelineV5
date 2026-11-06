import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, r"Z:\PinelineV2")
from test_channel import get_read_service

yt = get_read_service()
if not yt:
    print("Cannot get read service")
    sys.exit(1)

ch_resp = yt.channels().list(mine=True, part="contentDetails,statistics,snippet").execute()
items = ch_resp.get("items", [])
if not items:
    print("No channel found")
    sys.exit(1)

ch = items[0]
title = ch["snippet"]["title"]
stats = ch.get("statistics", {})
uploads_pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]

print(f"Channel Title: {title}")
print(f"Public video count: {stats.get('videoCount')}")
print(f"Uploads Playlist ID: {uploads_pl}")

pl_resp = yt.playlistItems().list(playlistId=uploads_pl, part="snippet,contentDetails", maxResults=50).execute()
pl_items = pl_resp.get("items", [])
print(f"Total uploaded items fetched: {len(pl_items)}")

now_utc = datetime.now(timezone.utc)
today_utc_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
today_vn_start = (now_utc + timedelta(hours=7)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=7)

count_today_utc = 0
count_today_vn = 0

print("\n--- Recent Videos ---")
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

total_today_vn = 0
total_today_utc = 0
total_all_time = 0
page_token = None

while True:
    pl_req = yt.playlistItems().list(
        playlistId=uploads_pl,
        part="snippet,contentDetails",
        maxResults=50,
        pageToken=page_token
    )
    pl_resp = pl_req.execute()
    items = pl_resp.get("items", [])
    if not items:
        break
        
    for it in items:
        total_all_time += 1
        pub_at_str = it["snippet"].get("publishedAt", "")
        pub_dt = datetime.fromisoformat(pub_at_str.replace("Z", "+00:00"))
        if pub_dt >= today_vn_start:
            total_today_vn += 1
        if pub_dt >= today_utc_start:
            total_today_utc += 1

    page_token = pl_resp.get("nextPageToken")
    if not page_token:
        break

print("--------------------------------------------------")
print(f"-> Chinh xac so video upload hom nay (theo gio Viet Nam): {total_today_vn} video")
print(f"-> Chinh xac so video upload hom nay (theo chu ky UTC YouTube): {total_today_utc} video")
print(f"-> Tong tat ca video (ca Unlisted / Private) tren kenh: {total_all_time} video")
