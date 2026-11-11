# TadClip: versions · เวอร์ชัน

Install a given version (to go back if a new one breaks) · ติดตั้งเวอร์ชันที่ต้องการ (ถ้าเวอร์ชันใหม่มีปัญหา):

```
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | TADCLIP_REF=v0.1.0 bash
```

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
