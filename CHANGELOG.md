# TadClip: versions · เวอร์ชัน

Install a given version (to go back if a new one breaks) · ติดตั้งเวอร์ชันที่ต้องการ (ถ้าเวอร์ชันใหม่มีปัญหา):

```
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | TADCLIP_REF=v0.1.0 bash
```

## v0.4.1 (2026-11-12)

- **เช็กความพร้อมบน Windows ได้แล้ว:** เอกสารก่อนเรียน ([docs/BEFORE-CLASS.th.md](docs/BEFORE-CLASS.th.md)) มีบรรทัดสำหรับ PowerShell
  ได้บรรทัด TADCLIP READY ✓ ไว้ส่งในกลุ่ม LINE เหมือน Mac · Windows ready check: one PowerShell line in the pre-class sheet.
- **เอกสารก่อนเรียนครบทั้ง Mac และ Windows:** วิธีเช็กเครื่อง ส่งคลิปเข้าคอมฯ โดยไม่ใช้ AirDrop และในคลาสต้องดับเบิลคลิกอะไร
  · The pre-class sheet covers Mac and Windows: the machine check, getting clips onto a PC, what to double-click.
- **ติดตั้งเร็วขึ้น:** เพลงดาวน์โหลดจากชุด music-v1 ของ TadClip เอง (ส่วนเสียง เพลง อีโมจิ ใช้ 2 นาที จากเดิม 13 นาที)
  · Faster install: music comes from TadClip's own music-v1 release (the sounds, music and emoji step: 2 min, was 13).

## v0.4.0 (2026-11-12)

- **เสียงและเพลงเป็นของ TadClip เอง ใช้ในงานขายได้:** เสียงประกอบ 48 เสียง TadClip สร้างเองด้วยโค้ด อีก 30 เสียงและเพลง 23 เพลงเป็น
  CC0 (สาธารณสมบัติ) ไม่ต้องให้เครดิต · Sounds and music are now TadClip's own (48 synthesized SFX) or CC0 (30 recorded SFX,
  23 FreePD music beds): fine in paid work, no credit needed. Install downloads less (the SFX come with the code).
- **สไตล์ใหม่ 15 แบบ สั่งชื่อได้เลย:** Paper collage, Vox, New background, Animated film, Chalkboard, Life in weeks,
  Notes + bubble, Cinematic doc, Split demo, 3-step lesson, Screen callouts, Paper explainer, Motion light, Boxed UI,
  Board + face · 15 new named styles.
- **ไม่มีคีย์ Pexels ก็ยังได้ภาพประกอบ** จาก Wikimedia Commons (เฉพาะที่ใช้ได้เชิงพาณิชย์) · Without a Pexels key, stock
  comes from Wikimedia Commons (CC0 / public domain / CC BY only).
- **โลโก้ SVG ใช้ได้แล้ว** ทั้ง Mac และ Windows พื้นใสเหมือนไฟล์ · SVG logos work on Mac and Windows, transparent.
- **Windows ชื่อผู้ใช้ภาษาไทย:** ไอคอนบนเดสก์ท็อปเปิด TadClip ได้ อีโมจิเคลื่อนไหวดาวน์โหลดครบ · Windows with a Thai user
  name: the Desktop icon opens TadClip; all animated emoji download.

## v0.3.0 (2026-11-11)

- **ใช้บน Windows ได้แล้ว (ทดลอง):** Windows 10 (1809 ขึ้นไป) / 11 แบบ 64 บิต ชิป Intel หรือ AMD วางบรรทัดเดียวใน PowerShell
  ไม่ต้องใช้สิทธิ์ผู้ดูแลเครื่อง · TadClip on Windows (preview): one line in PowerShell, no admin:
  `irm https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.ps1 | iex`
- ทดสอบบนเครื่อง Windows ใหม่ ชื่อผู้ใช้ภาษาไทย: ติดตั้งครบใน 7-8 นาที ถอดเสียงไทยได้คำตรงกับ Mac ทุกคำ (FLEURS 40 คลิป) คลิปที่ได้ตรงกับ Mac
  · Tested on a fresh Windows account with a Thai name: installs in 7-8 min; Thai speech word-for-word the same as the Mac
  (FLEURS, 40 clips); renders match the Mac.
- ยังไม่ได้ลองบนโน้ตบุ๊กจริง: เสียงแจ้งเตือน ปุ่ม ฟัง (ต้องเพิ่มเสียงภาษาไทยใน Windows) อ่านตัวอักษรไทยในรูป · Not yet tried on a real
  laptop: the notification sound, ฟัง (needs Windows' Thai voice), reading Thai text in images.

## v0.2.0 (2026-11-12)

- **คำแนะนำทีละขั้นบนหน้า TadClip:** ใช้ครั้งแรก หน้าจอจะหรี่ลงแล้วชี้ปุ่มที่ต้องกดทีละขั้น ขั้นละหนึ่งประโยค กด "ฟัง" ให้อ่านออกเสียงได้
  ข้ามได้ และกดปุ่ม ? เพื่อดูใหม่ · Step-by-step tips: the page dims and points at the one button to press, one
  sentence at a time, read aloud with ฟัง; skip any time, "?" shows them again.
- **ตัวอย่างคำสั่ง:** กดตัวอย่างใต้ช่อง "อยากได้แบบไหน" แทนการพิมพ์ ("ซับตัวใหญ่", "ไม่ใส่เพลง"…) · Tap-to-fill wish examples.
- **แบรนด์ของคุณบนหัวหน้าเว็บ:** ใส่แบรนด์แล้ว หัวหน้า TadClip ขึ้นโลโก้และชื่อร้านของคุณ · Your logo and name in the page header.
- แก้: ดิสก์เต็มทำให้หน้า TadClip ปิดเอง · Fix: a full disk ended the page's server.
- **หลายคลิปพร้อมกัน:** เลือกหลายคลิปแล้วกด "ตัดแยกทีละคลิป" TadClip ตัดต่อทีละคลิปจนได้ไฟล์จริงทุกคลิป ถ้าโควตา Claude
  ใน 5 ชั่วโมงใกล้เต็ม จะรอให้โควตากลับมาแล้วทำต่อเอง คลิปที่เสร็จแล้วเปิดมาสั่งแก้ทีหลังได้
  · Several clips: each is edited to a final file in turn, waiting for Claude's 5-hour usage window when it's nearly full.
- **โควตา Claude หมดกลางทาง:** หน้าจอบอกเวลาที่จะทำต่อ และทำต่อเองไม่ต้องกดอะไร
  · Usage limit: the page says when it carries on, and it does so by itself.
- **ตรวจเครื่องก่อนติดตั้ง:** ถ้าเครื่องไม่ใช่ Mac ชิป Apple, macOS ต่ำกว่า 14 หรือพื้นที่ว่างไม่ถึง 8 GB จะบอกทันทีเป็นภาษาไทย
  ก่อนดาวน์โหลดอะไร · Install stops in the first second on a Mac that can't run TadClip.
- แก้: คลิปที่ยังคัดลอกไม่เสร็จทำให้หน้า TadClip ปิดเอง · Fix: a clip still copying in crashed the page's server.
- ติดตั้งเวอร์ชันที่ต้องการได้ (`TADCLIP_REF`) · Install a given version.
- **เช็กความพร้อมก่อนเรียน:** พิมพ์ "เช็กความพร้อม TadClip" (หรือรัน `scripts/ready.sh`) ได้บรรทัด TADCLIP READY ✓ ไว้ส่งในกลุ่ม
  LINE ของคลาส · ขั้นตอนก่อนเรียน: [docs/BEFORE-CLASS.th.md](docs/BEFORE-CLASS.th.md)
  · Ready check before a class: a READY line to paste in the class LINE group, and a one-page Thai pre-class sheet.

## v0.1.0 (2026-11-10)

The pilot release: brand kit and brand intake, the format engine (creator styles, video teardown, competitor
analysis), the TadClip app, one-line install.
