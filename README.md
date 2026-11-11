<div align="center">

<h1>TadClip · ตัดคลิป</h1>

<p><b>ส่งคลิปพูดหน้ากล้องดิบๆ มา 1 คลิป ได้รีลที่ตัดเสร็จ พร้อมโพสต์</b></p>

<p>ตัดต่อคลิปพูดภาษาไทยด้วย AI บน Mac หรือ Windows ของคุณเอง ผ่าน Claude หรือ Codex</p>

[![สไตล์เริ่มต้น: ClubGig](https://img.shields.io/badge/default-ClubGig-87203F?style=flat)](recipes/clubgig/README.md)
[![Fork of ghost-editor](https://img.shields.io/badge/fork%20of-kurbaitaev%2Fghost--editor-black?style=flat&logo=github)](https://github.com/kurbaitaev/ghost-editor)

<img src="docs/media/clubgig/same-take.gif" width="100%" alt="คลิปเดียวกัน 3 แบบเล่นพร้อมกัน: ซ้าย คลิปดิบ กลาง ตัดแบบ ClubGig ขวา สไตล์ครีเอเตอร์ซ้อนบน ClubGig">

<sub>คลิปดิบ · ClubGig (ค่าเริ่มต้น) · สไตล์ครีเอเตอร์ซ้อนบน ClubGig</sub>

</div>

## ติดตั้ง

ต้องมีแอป [Claude](https://claude.com/claude-code) (แพ็กเกจเสียเงิน) หรือ [Codex](https://github.com/openai/codex) ไม่ต้องมีบัญชี GitHub ไม่ถามรหัสผ่านเครื่อง ใช้เวลาราว 10 นาที (เน็ตช้าอาจถึง 30) เน็ตหลุดก็วางบรรทัดเดิมอีกครั้ง

**Mac** (ชิป Apple M1 ขึ้นไป): กด ⌘Space พิมพ์ Terminal กด Enter แล้ววาง

```bash
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
```

**Windows** (10 เวอร์ชัน 1809 ขึ้นไป หรือ 11 แบบ 64 บิต ชิป Intel/AMD RAM 8 GB ขึ้นไป · ทดลอง): กดปุ่ม Windows พิมพ์ PowerShell กด Enter แล้ววาง

```powershell
irm https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.ps1 | iex
```

ไม่ต้องใช้สิทธิ์ผู้ดูแลเครื่อง ติดตั้ง Claude Code ให้ถ้ายังไม่มี บน Windows ตัดคลิปช้ากว่า Mac ราว 3-6 เท่า

## ใช้งาน

1. ติดตั้งเสร็จ หน้า TadClip เปิดขึ้นเอง (ครั้งต่อไป: Mac เปิด **TadClip.app** ในโฟลเดอร์ TadClip บนเดสก์ท็อป · Windows ดับเบิลคลิก **TadClip** บนเดสก์ท็อป)
2. กด **เข้าสู่ระบบ Claude** เลือกคลิป แล้วกด **ตัดต่อให้หน่อย** ราว 30-40 นาทีได้คลิปตัวอย่าง สั่งแก้ได้ พอใจกด OK ได้ไฟล์จริง หลายคลิปกด **ตัดแยกทีละคลิป**
3. หรือพิมพ์ในแชต Claude: `ตัดต่อคลิปนี้ ~/Downloads/my-video.mov` · `ตัดต่อคลิปนี้ให้เป็นสไตล์ @creator` · `วิเคราะห์คลิปนี้` + ลิงก์ · `วิเคราะห์คู่แข่ง @a @b`

**ก่อนเข้าคลาส:** ทำตาม [docs/BEFORE-CLASS.th.md](docs/BEFORE-CLASS.th.md) แล้วพิมพ์ในแชต Claude ว่า **"เช็กความพร้อม TadClip"**

**มีปัญหา:** วางบรรทัดติดตั้งอีกครั้ง หรือบอก Claude ว่า **"เก็บบันทึก TadClip"** แล้วส่งโฟลเดอร์บันทึกให้เรา (คีย์ไม่ติดไปด้วย) · [คู่มือละเอียด](docs/INSTALL.md) · [เวอร์ชันก่อนหน้า](CHANGELOG.md)

**คีย์ฟรี (ไม่บังคับ):** บอก Claude ว่า "เปิดไฟล์คีย์ TadClip" แล้ววางคีย์ในไฟล์นั้นเท่านั้น ห้ามวางในแชต · `GEMINI_API_KEY` ([ขอที่นี่](https://aistudio.google.com/apikey)) ถอดเสียงแม่นขึ้น ตรวจภาพประกอบ (ส่งเสียงและภาพไป Google) · `PEXELS_API_KEY` ([ขอที่นี่](https://www.pexels.com/api/key/)) ฟุตเทจสต็อกมากขึ้น

## คลิปดิบเข้า รีลออก

<img src="docs/media/clubgig/raw-vs-v2.gif" width="100%" alt="ซ้าย คลิปดิบจาก iPhone ที่มีนับถอยหลังและพูดผิด ขวา รีล ClubGig ที่ตัดเสร็จ มีการ์ดคำถามบนภาพสต็อก และข้อความไทยเด้งที่ช่วงอก">

<p align="center"><sub>คลิปดิบ 2:14 นาที เหลือรีล 1:33 เลือกเทคที่ดีที่สุดของแต่ละประโยค ตัดช่วงเงียบ คุณดูคลิปตัวอย่างก่อนทุกครั้ง</sub></p>

## สไตล์และเอฟเฟกต์

<img src="docs/media/styles-grid.gif" width="100%" alt="สไตล์ตัดต่อหลายแบบเล่นพร้อมกันเป็นช่องแนวตั้ง มีชื่อสไตล์ใต้แต่ละช่อง">

<img src="docs/media/effects-grid.gif" width="100%" alt="เอฟเฟกต์ 18 แบบเล่นพร้อมกัน เช่น แผนที่เส้นทาง ตัวเลขวิ่ง ภาพซ้อนกอง กระดานวาดมือ ตัวอักษรเคลื่อนไหว">

สั่งเป็นชื่อได้เลย เช่น Seoul list, Clean OS, RESULT, Whiteboard, Kinetic doc ([ทั้งหมด](docs/PLAYBOOK.md)) ก๊อปสไตล์ครีเอเตอร์เอามาแค่จังหวะ ตำแหน่ง ตัวอักษร และโครงเรื่อง **ไม่เอา**หน้า คำพูด โลโก้ เพลง หรือฟุตเทจของเขา

<details>
<summary><b>คำถาม</b></summary>

**ข้อมูลไปไหน** ตัดต่อและเรนเดอร์บนเครื่องคุณ ข้อความและภาพบางส่วนส่งให้ Claude / Codex คิดงาน และส่งให้ Google ถ้าใส่คีย์ Gemini

**Windows ยังไม่ได้อะไร** ปุ่ม ฟัง ต้องเพิ่มเสียงภาษาไทยก่อน (Settings > Time & language > Speech > Add voices > ไทย) อ่านตัวอักษรไทยในรูปโลโก้ต้องเพิ่มภาษาไทยใน Windows และยังใช้โลโก้ SVG ไม่ได้ (ใช้ PNG แทน)

สำหรับนักพัฒนา: [ทำงานยังไง](docs/HOW-IT-WORKS.md) · [สูตร ClubGig](recipes/clubgig/README.md) · [SKILL.md](SKILL.md) · [สัญญาอนุญาต](docs/THIRD_PARTY/README.md)
</details>

---

<p align="center">ต่อยอดจาก <a href="https://github.com/kurbaitaev/ghost-editor">ghost-editor</a> ของ <a href="https://github.com/kurbaitaev">@kurbaitaev</a> (MIT)<br>
ClubGig เป็นแบรนด์นำร่อง คลิปตัวอย่างและโลโก้เป็นของ Clubgig ใช้โดยได้รับอนุญาต และไม่อยู่ในสัญญาอนุญาตของ repo นี้</p>
