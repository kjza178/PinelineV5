# -*- coding: utf-8 -*-
"""Dump filled YouTube title prompt (generate_youtube_titles) for review."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import agents.meta_studio as m  # noqa: E402

OUT = Path(__file__).with_name("title_youtube_prompt_filled.txt")

series_name = "Võ Đạo Cộng Điểm: Lão Lục Thời Loạn Thành Thánh"
season = 1
title_zh = "武道加点：乱世老六成圣"
summary = (
    "Nô lệ khai khoáng Hứa Hoa thức tỉnh hệ thống cộng điểm võ đạo, "
    "từ Lão Lục thành thánh."
)
job_id = "50ba645d468b"
episode_info = ""
count = 5

clean_name = m.clean_series_name(series_name, fallback="Phim Hay")
story_info = m.get_film_story_info(
    job_id=job_id,
    title_zh=title_zh,
    title_vi=series_name,
    summary=summary,
    episode_info=episode_info,
)
zh_name = story_info.get("title_zh") or title_zh or ""
tom_tat = story_info.get("story") or summary or episode_info or clean_name
phan_label = f"Phần {season}" if season else "Phần 1"

# Mirror source in meta_studio.generate_youtube_titles (keep in sync when editing).
prompt = f"""Bạn là biên tập tiêu đề YouTube cho kênh Donghua / Manhua thuyết minh tiếng Việt (CTR cao, vẫn trung thực với phim).

# DỮ LIỆU PHIM (NGUỒN SỰ THẬT — BÁM SÁT, KHÔNG BỊA PHIM KHÁC)
- Tên gốc ZH: {zh_name or clean_name}
- Tên VI: {clean_name}
- Nhãn phần: {phan_label}
- Tóm tắt Baike / giới thiệu:
\"\"\"
{tom_tat}
\"\"\"

# NHIỆM VỤ
Viết đúng {count} tiêu đề YouTube tiếng Việt. Mỗi tiêu đề phải khiến người lướt feed DỪNG LẠI vì tò mò về ĐÚNG bộ phim này.

# QUY TẮC VÀNG (bắt buộc)
1. Chỉ dùng tên riêng / hệ thống / biến cố CÓ TRONG tóm tắt hoặc tên phim. CẤM copy khuôn mẫu phim khác (vd Thôn Thiên Hồ, Ngũ Hệ Ngụy Linh Căn nếu không có trong nguồn).
2. Mỗi tiêu đề = 1 GÓC MÓC KHÁC NHAU (không paraphrase cùng 1 câu 5 lần).
3. Độ dài 55–85 ký tự (ưu tiên ~70). Dễ đọc trên điện thoại. Không Title Case cứng từng chữ — viết tiếng Việt tự nhiên, chỉ viết hoa tên riêng / đầu câu / nhãn phần.
4. Có `{phan_label}` (đầu dạng `{phan_label} | …` hoặc cuối `… | {phan_label}`).
5. Chỉ tiếng Việt — không chữ Hán, không pinyin, không emoji, không ** markdown.
6. CẤM cụm sáo rỗng: «nghịch thiên cải mệnh», «khiến kẻ thù kinh hãi», «siêu phẩm», «đỉnh cao trả thù» nếu không gắn tên riêng/biến cố cụ thể.
7. Ưu tiên: tên nhân vật / hệ thống / thân phận cụ thể + 1 cú twist ngắn (tưởng… hóa ra… / từ A thành B / bị X → có Y).

# 5 GÓC BẮT BUỘC (mỗi góc 1 tiêu đề)
1. Tên phim (đã trau) + biến cố mở đầu rõ nhất trong tóm tắt
2. Tương phản thân phận (thấp → cao / nô lệ → thánh…) dùng đúng từ nguồn
3. «Tưởng… / Ai ngờ…» bám đúng twist của phim
4. Hệ thống / năng lực / bàn tay vàng ĐÚNG TÊN trong tóm tắt
5. Câu hỏi hoặc hệ quả khiến muốn bấm (vẫn có tên riêng, không clickbait bịa)

# VÍ DỤ CẤU TRÚC TỐT (chỉ học nhịp — ĐỪNG chép nội dung nếu không thuộc phim)
- «Phần 1 | Võ Đạo Cộng Điểm: Nô Lệ Khai Khoáng Thức Tỉnh Hệ Thống, Lão Lục Thành Thánh»
- «Xuyên Không Thành Nô Lệ, Hứa Hoa Cộng Điểm Quyền Đao Cho Đến Khi Cả Giới Võ Khiếp»

# ĐẦU RA
Chỉ JSON hợp lệ:
{{"series_name_refined":"<tên VI ngắn đẹp>","titles":["...","...","...","...","..."],"best":"<1 trong titles>","reason":"<1 câu vì sao best đúng cốt truyện>"}}"""

OUT.write_text(prompt, encoding="utf-8")
print(f"WROTE {OUT}")
print(f"zh={zh_name!r}")
print(f"vi={clean_name!r}")
print(f"tom_tat_chars={len(tom_tat)}")
