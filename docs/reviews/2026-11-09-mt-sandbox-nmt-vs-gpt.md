# NMT chính vs GPT rà — sandbox 120 cues

- **Job:** `D:\PinelineV2_tmp\mt_sandbox_job`
- **NMT:** base HachimiMT + hard-lock (`script.nmt_primary.json` tái tạo)
- **GPT:** `chatgpt/gpt-5-6-mini` run_review (+ polish sau) → `script.json`

- Tổng: **120** câu · Giữ nguyên: **82** · Đổi: **38** (32%)
- Tag: `{'xưng hô': 27, 'diễn đạt': 6, 'rút/dài': 3, 'mất tên NV': 1, 'thêm tên NV': 2}`

## Toàn bộ câu bị đổi (NMT → GPT)

### i=0 · xưng hô · sec≈4.32
- **ZH:** 殿主没想到三百年前那一战竟真把你伤成这样，
- **NMT:** Điện chủ không ngờ trận chiến ba trăm năm trước lại thật sự làm ngươi bị thương như vậy
- **GPT:** Điện chủ không ngờ trận chiến ba trăm năm trước lại thật sự làm cậu bị thương như vậy

### i=2 · xưng hô · sec≈1.84
- **ZH:** 殿主如今的你寿元将近，
- **NMT:** Điện chủ bây giờ thọ nguyên của ngươi sắp hết,
- **GPT:** Điện chủ bây giờ thọ nguyên của cậu sắp hết,

### i=6 · xưng hô · sec≈4.48
- **ZH:** 至于你石像殿交出所有法宝。
- **NMT:** Còn về việc Thạch Tượng Điện ngươi giao ra tất cả pháp bảo.
- **GPT:** Còn về việc Thạch Tượng Điện cậu giao ra tất cả pháp bảo.

### i=8 · xưng hô · sec≈1.76
- **ZH:** 哎呦，我了个大操，
- **NMT:** Ôi chao, ta làm cái quái gì vậy
- **GPT:** Ôi chao, tôi làm cái quái gì vậy

### i=19 · diễn đạt · sec≈2.54
- **ZH:** 眼前这俩老阴逼正拿刀对着我呀，
- **NMT:** Hai lão già âm hiểm trước mắt đang chĩa dao vào ta,
- **GPT:** Hai lão già âm hiểm trước mắt đang chĩa dao vào tôi,

### i=20 · xưng hô · sec≈1.23
- **ZH:** 华外，这是要嘎我的命吗？完了，
- **NMT:** Hoa Ngoại, đây là muốn giết mạng ta sao? Xong rồi,
- **GPT:** Hoa Ngoại, đây là muốn giết mạng tôi sao? Xong rồi,

### i=29 · diễn đạt · sec≈1.84
- **ZH:** 底下这俩是我的手下，
- **NMT:** Hai tên phía dưới này là thủ hạ của ta,
- **GPT:** Hai tên phía dưới này là thủ hạ của tôi,

### i=31 · diễn đạt · sec≈0.81
- **ZH:** 就为了今天干掉我。
- **NMT:** Chỉ để hôm nay giết ta.
- **GPT:** Chỉ để hôm nay giết tôi.

### i=35 · xưng hô · sec≈0.8
- **ZH:** 我他妈穿成一。
- **NMT:** Mẹ kiếp, ta mặc thành một.
- **GPT:** Mẹ kiếp, tôi mặc thành một.

### i=36 · xưng hô · sec≈2.64
- **ZH:** 我他妈穿成一个马上要被手下乱刀砍死的老头儿，
- **NMT:** Mẹ kiếp, ta xuyên thành một lão già sắp bị thủ hạ chém chết rồi
- **GPT:** Mẹ kiếp, tôi xuyên thành một lão già sắp bị thủ hạ chém chết rồi

### i=38 · xưng hô · sec≈1.36
- **ZH:** 我的金手指呢？
- **NMT:** Kim thủ chỉ của ta đâu?
- **GPT:** Kim thủ chỉ của tôi đâu?

### i=42 · xưng hô · sec≈1.76
- **ZH:** 系统你在吗？妈的，
- **NMT:** Hệ thống ngươi có ở đây không? Mẹ kiếp,
- **GPT:** Hệ thống cậu có ở đây không? Mẹ kiếp,

### i=44 · xưng hô · sec≈1.31
- **ZH:** 我就纯粹是个倒霉蛋，
- **NMT:** Ta thuần túy là một kẻ xui xẻo
- **GPT:** Tôi thuần túy là một kẻ xui xẻo

### i=51 · xưng hô · sec≈1.28
- **ZH:** 我是写小说的，
- **NMT:** Ta viết tiểu thuyết
- **GPT:** Tôi viết tiểu thuyết

### i=52 · xưng hô · sec≈1.28
- **ZH:** 我太懂套路了。
- **NMT:** Ta quá hiểu cách rồi.
- **GPT:** Tôi quá hiểu cách rồi.

### i=59 · rút/dài · sec≈1.84
- **ZH:** 这他妈就叫主角光环。
- **NMT:** Cái này mẹ nó gọi là hào quang nhân vật chính.
- **GPT:** Đó là hào quang nhân vật chính!

### i=62 · xưng hô · sec≈1.04
- **ZH:** 你倒是出啊，
- **NMT:** Ngươi ra đi chứ
- **GPT:** Cậu ra đi chứ

### i=70 · diễn đạt · sec≈1.44
- **ZH:** 才能种下怀疑的种子。
- **NMT:** Mới có thể gieo xuống hạt giống nghi ngờ.
- **GPT:** Mới có thể gieo mầm nghi ngờ.

### i=76 · xưng hô · sec≈2.32
- **ZH:** 你的修为我们早就查明白了。
- **NMT:** Tu vi của ngươi chúng ta đã sớm điều tra rõ.
- **GPT:** Tu vi của cậu chúng ta đã sớm điều tra rõ.

### i=78 · xưng hô · sec≈3.44
- **ZH:** 你拿什么跟我们斗？就是。
- **NMT:** Ngươi lấy gì đấu với chúng ta? Đúng vậy.
- **GPT:** Cậu lấy gì đấu với chúng ta? Đúng vậy.

### i=79 · xưng hô · sec≈2.0
- **ZH:** 要是三百年前的你，
- **NMT:** Nếu là ngươi ba trăm năm trước,
- **GPT:** Nếu là cậu ba trăm năm trước,

### i=81 · xưng hô · sec≈1.6
- **ZH:** 但现在的你嘛，哼，店主。
- **NMT:** Nhưng bây giờ là ngươi, hừ, chủ tiệm.
- **GPT:** Nhưng bây giờ là cậu, hừ, chủ tiệm.

### i=82 · xưng hô · sec≈2.08
- **ZH:** 哼，殿主最后再叫你一声殿主。
- **NMT:** Hừ, điện chủ cuối cùng lại gọi ngươi một tiếng Điện Chủ.
- **GPT:** Hừ, điện chủ cuối cùng lại gọi cậu một tiếng Điện Chủ.

### i=83 · xưng hô · sec≈0.24
- **ZH:** 其实我一直不相信你是天下第一，
- **NMT:** Kỳ thật ta vẫn luôn không tin ngươi là thiên hạ đệ nhất,
- **GPT:** Kỳ thật tôi vẫn luôn không tin cậu là thiên hạ đệ nhất,

### i=84 · xưng hô · sec≈2.56
- **ZH:** 今天我就要亲手把你斩于剑下。
- **NMT:** Hôm nay ta sẽ tự tay chém ngươi dưới kiếm.
- **GPT:** Hôm nay tôi sẽ tự tay chém cậu dưới kiếm.

### i=85 · mất tên NV · sec≈1.36
- **ZH:** 二位护法，
- **NMT:** Hai vị hộ pháp,
- **GPT:** Hai vị Hộ pháp,

### i=86 · rút/dài, thêm tên NV · sec≈3.52
- **ZH:** 这么看来今天你们是吃定本座了，
- **NMT:** Xem ra hôm nay các ngươi đã nắm chắc bổn tọa rồi
- **GPT:** Xem ra hôm nay Hai vị hộ pháp đã chắc mẩm sẽ hạ được Bản tọa rồi.

### i=88 · xưng hô · sec≈0.48
- **ZH:** 你做了明白就好，
- **NMT:** Ngươi hiểu rõ là tốt rồi,
- **GPT:** Cậu hiểu rõ là tốt rồi,

### i=89 · xưng hô · sec≈1.52
- **ZH:** 只要悄悄宰了你，
- **NMT:** Chỉ cần lặng lẽ giết ngươi,
- **GPT:** Chỉ cần lặng lẽ giết cậu,

### i=91 · xưng hô · sec≈4.51
- **ZH:** 还有你攒下的所有神通道法和逆天法宝也全归我们。
- **NMT:** Còn tất cả thần thông đạo pháp và nghịch thiên pháp bảo mà ngươi tích góp được cũng đều thuộc về chúng ta.
- **GPT:** Còn tất cả thần thông đạo pháp và nghịch thiên pháp bảo mà cậu tích góp được cũng đều thuộc về chúng ta.

### i=92 · diễn đạt · sec≈0.86
- **ZH:** 哈哈哈哈哈哈。
- **NMT:** Ha ha haha.
- **GPT:** Haha

### i=94 · xưng hô · sec≈3.23
- **ZH:** 确实有尾气跟你们斗了。
- **NMT:** Đúng là có khí thế chiến đấu với các ngươi rồi.
- **GPT:** Đúng là có khí thế chiến đấu với các cậu rồi.

### i=97 · xưng hô · sec≈1.92
- **ZH:** 你们俩日后怎么共展，
- **NMT:** Hai người các ngươi sau này cùng triển khai thế nào,
- **GPT:** Hai người các cậu sau này cùng triển khai thế nào,

### i=103 · xưng hô · sec≈1.89
- **ZH:** 你的离间计对我二人没用，
- **NMT:** Ly gián kế của ngươi vô dụng với hai người ta
- **GPT:** Ly gián kế của cậu vô dụng với hai người ta

### i=111 · thêm tên NV · sec≈2.4
- **ZH:** 万界无敌系统正式激活，
- **NMT:** Hệ thống Vô Địch Vạn Giới chính thức kích hoạt,
- **GPT:** Vạn Giới Vô Địch Hệ Thống chính thức kích hoạt,

### i=117 · diễn đạt · sec≈1.1
- **ZH:** 恭喜宿主获得至尊新手大礼包，
- **NMT:** Chúc mừng ký chủ đạt được gói quà tân thủ Chí Tôn
- **GPT:** Chúc mừng ký chủ đạt được Gói quà tân thủ Chí Tôn

### i=118 · rút/dài · sec≈4.06
- **ZH:** 是否选择开启开启条件接受系统主线任务？
- **NMT:** Liệu có chọn mở điều kiện để tiếp nhận nhiệm vụ chính tuyến của hệ thống không?
- **GPT:** Mở không? Điều kiện: nhận nhiệm vụ chính tuyến.

### i=119 · xưng hô · sec≈0.92
- **ZH:** 老子特么终于等到你了，
- **NMT:** Lão tử rốt cuộc cũng đợi được ngươi rồi
- **GPT:** Lão tử rốt cuộc cũng đợi được cậu rồi

## Mẫu câu NMT giữ nguyên (tối đa 15)

- i=1: `不枉我们苦苦等到今天。` → `Không uổng công chúng ta khổ sở đợi đến hôm nay.`
- i=3: `修为实力实不存一，` → `Tu vi thực lực không còn một,`
- i=4: `这殿主之位也该让让了。` → `Vị trí điện chủ này cũng nên nhường nhịn rồi.`
- i=5: `诸位也该让让了。` → `Chư vị cũng nên nhường nhịn rồi.`
- i=7: `然后就随历代殿主魂归九泉之下吧。` → `Sau đó cứ theo các đời điện chủ hồn quy về dưới chín suối đi.`
- i=9: `这特么什么情况？` → `Chuyện quái gì thế này?`
- i=10: `老子不是正在熬夜码字吗？` → `Lão tử không phải đang thức đêm gõ chữ sao?`
- i=11: `怎么眼睛一闭一睁就跑这个鬼地方来了？` → `Sao vừa nhắm mắt đã chạy đến cái nơi quỷ quái này rồi?`
- i=12: `这打电、` → `Cái gọi điện này`
- i=13: `这杀气等等，` → `Sát khí này...`
- i=14: `这破椅子上。` → `Trên chiếc ghế rách nát này.`
- i=15: `等等，这破椅子上怎么全是骷髅头？` → `Khoan đã, trên chiếc ghế rách nát này sao toàn là đầu lâu vậy?`
- i=16: `坐着不硌屁股吗？` → `Ngồi không cấn mông sao?`
- i=17: `不对不对，` → `Không đúng không đúng,`
- i=18: `现在不是吐槽椅子的时候。` → `Bây giờ không phải lúc để chê bai cái ghế.`