<div align="center">

<h1>TadClip · ตัดคลิป</h1>

<p><b>ส่งคลิปพูดหน้ากล้องดิบๆ มา 1 คลิป ได้รีลที่ตัดเสร็จ พร้อมโพสต์</b></p>

<p>ตัดต่อคลิปพูดภาษาไทยด้วย AI บน Mac ของคุณเอง ผ่าน Claude หรือ Codex</p>

[![สไตล์เริ่มต้น: ClubGig](https://img.shields.io/badge/default-ClubGig-87203F?style=flat)](recipes/clubgig/README.md)
[![Fork of ghost-editor](https://img.shields.io/badge/fork%20of-kurbaitaev%2Fghost--editor-black?style=flat&logo=github)](https://github.com/kurbaitaev/ghost-editor)

<img src="docs/media/clubgig/same-take.gif" width="100%" alt="คลิปเดียวกัน 3 แบบเล่นพร้อมกัน: ซ้าย คลิปดิบ กลาง ตัดแบบ ClubGig ขวา สไตล์ครีเอเตอร์ซ้อนบน ClubGig">

<sub>คลิปดิบ · ClubGig (ค่าเริ่มต้น) · สไตล์ครีเอเตอร์ซ้อนบน ClubGig</sub>

</div>

## เริ่มใช้งาน

**ต้องมี:** Mac ชิป Apple (M1 ขึ้นไป) กับแอป [Claude](https://claude.com/claude-code) (แพ็กเกจเสียเงิน) หรือ [Codex](https://github.com/openai/codex) ไม่ต้องมีบัญชี GitHub

**1. ติดตั้ง** วางบรรทัดนี้ใน Terminal (กด ⌘Space พิมพ์ Terminal แล้วกด Enter) หรือวางในแชต Claude / Codex ให้มันรันให้

```bash
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
```

ใช้เวลาราว 10 นาที เน็ตช้าอาจถึง 30 ไม่ถามรหัสผ่านเครื่อง ถ้าเน็ตหลุด วางบรรทัดเดิมอีกครั้ง ส่วนที่เสร็จแล้วจะข้ามให้

**2. ตัดคลิป** ติดตั้งเสร็จ หน้า TadClip จะเปิดขึ้นเอง เลือกคลิป แล้วกด **ตัดต่อให้หน่อย** รอราว 30-40 นาทีได้คลิปตัวอย่าง ดูแล้วสั่งแก้ได้ พอใจแล้วกด OK ได้ไฟล์จริง
ครั้งต่อไป ดับเบิลคลิกโฟลเดอร์ **TadClip** บนเดสก์ท็อป แล้วเปิด **TadClip.app**

**3. มีปัญหา** วางบรรทัดติดตั้งอีกครั้ง หรือบอก Claude ว่า **"เก็บบันทึก TadClip"** แล้วส่งโฟลเดอร์บันทึกให้เรา (คีย์ไม่ติดไปด้วย) · คู่มือละเอียด: [docs/INSTALL.md](docs/INSTALL.md)

## สั่งในแชตก็ได้

ติดตั้งเสร็จ ปิดแล้วเปิดแอป Claude ใหม่หนึ่งครั้ง เปิดแชตใหม่ แล้วพิมพ์

> ตัดต่อคลิปนี้ ~/Downloads/my-video.mov

| พิมพ์ว่า | TadClip ทำ |
|---|---|
| `ตัดต่อคลิปนี้` | ตัดเป็นสไตล์ **ClubGig** ข้อความเด้งที่ช่วงอก ภาพสต็อกปัดเข้า ปุ่ม LINE ตอนท้าย |
| `ตัดต่อคลิปนี้ให้เป็นสไตล์ @creator` | ดูรีลของครีเอเตอร์คนนั้น เอารูปแบบมาซ้อนบน ClubGig แล้วตัด |
| ส่งลิงก์คลิปไวรัล ยังไม่มีคลิป | เขียนสคริปต์ภาษาไทยให้คนจริงไปถ่าย แล้วตัดคลิปที่ถ่ายมา |
| ชื่อสไตล์ เช่น `Seoul list` | ใช้สไตล์นั้น |

## ใส่คีย์ (ไม่บังคับ)

ไม่มีคีย์ก็ใช้ได้ ถ้าอยากให้คลิปตรงใจขึ้น บอก Claude ว่า "เปิดไฟล์คีย์ TadClip" วางคีย์ต่อจาก `=` แล้วกด ⌘S **วางคีย์ในไฟล์นี้เท่านั้น ห้ามวางในแชต**

| คีย์ (ฟรี) | ขอได้ที่ | ได้อะไรเพิ่ม |
|---|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | ถอดเสียงไทยแม่นขึ้น ตรวจภาพประกอบให้ตรงกับประโยค (เสียงและภาพส่งไป Google) |
| `PEXELS_API_KEY` | [pexels.com/api/key](https://www.pexels.com/api/key/) | ฟุตเทจสต็อกมากขึ้น |

## คลิปดิบเข้า รีลออก

<img src="docs/media/clubgig/raw-vs-v2.gif" width="100%" alt="ซ้าย คลิปดิบจาก iPhone ที่มีนับถอยหลังและพูดผิด ขวา รีล ClubGig ที่ตัดเสร็จ มีการ์ดคำถามบนภาพสต็อก และข้อความไทยเด้งที่ช่วงอก">

<p align="center"><sub>ตัวอย่าง: คลิปดิบ 2:14 นาที เหลือรีล 1:33 เลือกเทคที่ดีที่สุดของแต่ละประโยค ตัดช่วงเงียบ คุณดูคลิปตัวอย่างก่อนทุกครั้ง</sub></p>

## เอฟเฟกต์และสไตล์

<img src="docs/media/effects-grid.gif" width="100%" alt="เอฟเฟกต์ 18 แบบเล่นพร้อมกัน เช่น แผนที่เส้นทาง ตัวเลขวิ่ง ภาพซ้อนกอง กระดานวาดมือ ตัวอักษรเคลื่อนไหว">

สั่งเป็นชื่อได้เลย: Clean OS, Seoul list, RESULT, Face RESULT, stan style, วิดีโออธิบาย (animated explainer), POV montage, Kinetic doc,
Whiteboard, Step Deck, Product page, Tactile paper, Caption News, News Package, Telestrator, Halftone Dossier, Swiss Grid, Data Story,
Hologram HUD และพรีเซ็ตคำเดียว 7 แบบ (`clean` `editorial` `meme` `cinematic` `launch` `kinetic` `pop`)

**ก๊อปสไตล์ครีเอเตอร์:** ใช้วิธีของ [Hypit](https://github.com/hypit-ai/hypit) อ่านว่าคลิปเขาดึงคนดูไว้ด้วยอะไร แล้วเอามาแค่จังหวะ ตำแหน่ง ตัวอักษร
และระดับเสียง **ไม่เอา**หน้า คำพูด โลโก้ เพลง หรือฟุตเทจของเขา

<details>
<summary><b>คำถาม</b></summary>

**ขายได้ไหม** ไม่ได้ ใช้กับงานของตัวเองได้ รวมถึงงานรับจ้าง แต่สัญญาอนุญาตของ Hypit ห้ามขายหรือรวมไปขาย ทั้งตัวนี้และงานที่ดัดแปลงจากมัน
ถ้าไม่มีสัญญาอนุญาตเชิงพาณิชย์

**ข้อมูลไปไหน** ตัดต่อและเรนเดอร์บนเครื่องคุณ ข้อความและภาพบางส่วนส่งให้ Claude / Codex คิดงาน และส่งให้ Google ถ้าใส่คีย์ Gemini

**Windows ได้ไหม** ตอนนี้ยังใช้ได้แค่ Mac ชิป Apple

สำหรับนักพัฒนา: [ทำงานยังไง](docs/HOW-IT-WORKS.md) · [ชิ้นส่วนทั้งหมด](docs/PLAYBOOK.md) · [สูตร ClubGig](recipes/clubgig/README.md) · [SKILL.md](SKILL.md) · [สัญญาอนุญาต](docs/THIRD_PARTY/README.md)
</details>

---

<p align="center">ต่อยอดจาก <a href="https://github.com/kurbaitaev/ghost-editor">ghost-editor</a> ของ <a href="https://github.com/kurbaitaev">@kurbaitaev</a> (MIT) คู่มือของ Hypit อยู่ภายใต้ <a href="vendor/hypit/LICENSE">Hypit Open Source License</a><br>
ClubGig เป็นแบรนด์นำร่อง คลิปตัวอย่างและโลโก้เป็นของ Clubgig ใช้โดยได้รับอนุญาต และไม่อยู่ในสัญญาอนุญาตของ repo นี้</p>
