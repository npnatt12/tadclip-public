# Installing TadClip · วิธีติดตั้ง TadClip

About 15 minutes, most of it downloads. Works in Claude Code and Codex.

ใช้เวลาประมาณ 15 นาที ส่วนใหญ่คือรอดาวน์โหลด ใช้ได้ทั้ง Claude Code และ Codex

## Before you start · ก่อนเริ่ม

| You need · สิ่งที่ต้องมี | Details · รายละเอียด |
|---|---|
| A Mac with Apple silicon · Mac ชิป Apple (M1 ขึ้นไป) | Linux and Intel Macs are untested · ยังไม่ได้ทดสอบบน Linux และ Mac ชิป Intel |
| Claude Code or Codex · Claude Code หรือ Codex | [Claude Code](https://claude.com/claude-code) · [Codex](https://github.com/openai/codex). Install it first · ลงตัวนี้ก่อน |

## Step 1: Install · ขั้นที่ 1: ติดตั้ง

Paste this into Claude Code or Codex:

วางข้อความนี้ใน Claude Code หรือ Codex:

```text
ติดตั้ง TadClip ให้หน่อย ทำตามส่วน "For the agent doing the install" ใน https://raw.githubusercontent.com/npnatt12/tadclip-public/main/docs/INSTALL.md
```

It installs everything into your home folder. It does not ask for your Mac password, and you don't need Terminal, Homebrew or Apple's developer tools. Click Yes when it asks to run a command.

agent จะลงทุกอย่างไว้ในโฟลเดอร์ของคุณเอง ไม่ถามรหัสผ่านเครื่อง Mac ไม่ต้องเปิด Terminal และไม่ต้องลง Homebrew หรือ developer tools ของ Apple ถ้าขึ้นถามว่าจะให้รันคำสั่งไหม ให้กด Yes

No Claude Code or Codex? Open Terminal (⌘Space, type Terminal, Enter) and paste this line instead:

ถ้าไม่มี Claude Code หรือ Codex ให้เปิด Terminal (กด ⌘Space พิมพ์ Terminal แล้วกด Enter) แล้ววางบรรทัดนี้แทน:

```bash
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
```

## Step 2: Open the key file · ขั้นที่ 2: เปิดไฟล์คีย์

The installer does this for you. To open it again, ask your agent to "open the TadClip key file", or paste this into Terminal:

ตัวติดตั้งจะเปิดให้เอง ถ้าอยากเปิดอีกครั้ง บอก agent ว่า "เปิดไฟล์คีย์ TadClip" หรือวางบรรทัดนี้ใน Terminal:

```bash
open -e ~/.claude/skills/tadclip/.env
```

Keep the file open for step 3. **Paste keys into this file, never into the chat.** It stays on your Mac.

เปิดไฟล์ค้างไว้สำหรับขั้นที่ 3 **วางคีย์ในไฟล์นี้เท่านั้น ห้ามวางในแชต** ไฟล์นี้อยู่ในเครื่องของคุณ ไม่ถูกส่งขึ้นไปไหน

## Step 3: Get your free key · ขั้นที่ 3: ขอคีย์ฟรี

**Gemini** (Thai transcript and B-roll checks · ถอดเสียงภาษาไทยและตรวจ B-roll)

1. Open **https://aistudio.google.com/apikey** and sign in with Google.<br>เปิดลิงก์แล้วล็อกอินด้วยบัญชี Google
2. Click **Create API key**, then copy it.<br>กด **Create API key** แล้วคัดลอกคีย์
3. Paste it right after `GEMINI_API_KEY=`, with no spaces or quotes.<br>วางต่อจาก `GEMINI_API_KEY=` ไม่ต้องเว้นวรรค ไม่ต้องใส่เครื่องหมายคำพูด

**Pexels** (optional: more stock footage. Without it TadClip uses Mixkit and Wikimedia · ไม่บังคับ: ได้ฟุตเทจสต็อกเพิ่ม ถ้าไม่ใส่ TadClip จะใช้ Mixkit และ Wikimedia แทน)

1. Open **https://www.pexels.com/api/key/** and log in, or create a free account.<br>เปิดลิงก์แล้วล็อกอิน หรือสมัครบัญชีฟรี
2. If it asks about your project, fill in the short form.<br>ถ้าถามเรื่องโปรเจกต์ ก็กรอกสั้นๆ ได้เลย
3. Copy your key and paste it right after `PEXELS_API_KEY=`.<br>คัดลอกคีย์ แล้ววางต่อจาก `PEXELS_API_KEY=`

Save the file (⌘S) and close it. It should look like this, with your own key:

กด ⌘S เพื่อเซฟแล้วปิดไฟล์ หน้าตาจะเป็นแบบนี้ แต่เป็นคีย์ของคุณเอง:

```text
GEMINI_API_KEY=your-gemini-key
PEXELS_API_KEY=
```

## Step 4: Check it · ขั้นที่ 4: เช็กความพร้อม

Tell your agent "run the TadClip doctor", or paste this into Terminal:

บอก agent ว่า "run the TadClip doctor" หรือวางบรรทัดนี้ใน Terminal:

```bash
bash ~/.claude/skills/tadclip/scripts/doctor.sh
```

You're ready when it ends with `0 missing`. Lines marked `opt` are optional.

ถ้าบรรทัดสุดท้ายขึ้น `0 missing` แปลว่าพร้อมใช้ บรรทัดที่ขึ้นว่า `opt` ไม่ต้องทำก็ได้

## Step 5: Edit your first reel · ขั้นที่ 5: ตัดคลิปแรก

Start a new session so your agent sees the skill, then say:

เปิดเซสชันใหม่เพื่อให้ agent เห็นสกิล แล้วสั่งแบบนี้:

> ตัดต่อคลิปนี้ ~/Downloads/my-video.mov

ClubGig is the default. To copy a creator's style:

สไตล์เริ่มต้นคือ ClubGig ถ้าอยากได้สไตล์ของครีเอเตอร์คนไหน สั่งแบบนี้:

> ตัดต่อคลิปนี้ให้เป็นสไตล์ @someone ให้หน่อย ~/Downloads/my-video.mov

For a brand other than Clubgig, you'll be asked once for its logo and LINE handle.

ถ้าใช้แบรนด์อื่นที่ไม่ใช่ Clubgig ระบบจะถามโลโก้กับ LINE ของแบรนด์นั้นครั้งเดียว

**On Codex · ถ้าใช้ Codex:** the edit runs in your session instead of in helper agents. `@someone` needs a logged-in browser, so if your agent can't reach one, paste links to 3 of their reels.

งานตัดต่อจะรันในเซสชันเดียวกันเลย ไม่ได้แยกไปให้ helper agent ส่วน `@someone` ต้องใช้เบราว์เซอร์ที่ล็อกอินไว้ ถ้า agent เข้าไม่ได้ ให้วางลิงก์รีลของคนนั้น 3 ลิงก์แทน

## If something goes wrong · ถ้ามีปัญหา

| What you see · สิ่งที่เห็น | What to do · วิธีแก้ |
|---|---|
| `503` or `504` from Gemini | Google is busy, your key is fine. Try again later.<br>Google ยุ่งอยู่ คีย์ไม่มีปัญหา ลองใหม่ทีหลัง |
| `429` from Gemini | The free daily limit is used up. It was 20 requests a day when we measured it, resetting at 15:00 Bangkok time ([current limits](https://ai.google.dev/gemini-api/docs/rate-limits)).<br>ใช้โควตาฟรีของวันนี้หมดแล้ว ตอนที่เราวัดได้ 20 ครั้งต่อวัน รีเซ็ตตอน 15:00 น. เวลาไทย |
| `MISS GEMINI_API_KEY` | The key isn't in the file, or the file wasn't saved. Repeat steps 2 and 3.<br>ยังไม่มีคีย์ในไฟล์ หรือยังไม่ได้เซฟ ทำขั้นที่ 2 และ 3 อีกครั้ง |
| The agent doesn't know TadClip<br>agent ไม่รู้จัก TadClip | Start a new session.<br>เปิดเซสชันใหม่ |
| Any other `MISS` line<br>บรรทัด `MISS` อื่นๆ | It prints its own fix. Run it, or paste the install line again: it's safe to repeat.<br>บรรทัดนั้นจะบอกวิธีแก้ไว้ ทำตามนั้น หรือวางบรรทัดติดตั้งอีกครั้งก็ได้ ทำซ้ำได้ไม่มีผลเสีย |

**Update to the latest version · อัปเดตเวอร์ชันล่าสุด:** paste the install line again · วางบรรทัดติดตั้งเดิมอีกครั้ง

**Privacy · ความเป็นส่วนตัว:** the speaker's audio and frames go to Google for the transcript and checks. On the free tier, Google may use them to improve its products ([terms](https://ai.google.dev/gemini-api/terms)). Get the speaker's OK before you edit someone else's recording.

เสียงและภาพของคนในคลิปจะถูกส่งไปที่ Google เพื่อถอดเสียงและตรวจคลิป ถ้าใช้คีย์ฟรี Google อาจนำไปปรับปรุงผลิตภัณฑ์ของเขาได้ ([ข้อกำหนด](https://ai.google.dev/gemini-api/terms)) ถ้าจะตัดคลิปของคนอื่น ขออนุญาตเจ้าตัวก่อน

---

## For the agent doing the install

Tell the user in plain words what you're installing and why. Never ask for keys in the chat.

1. **Run the installer yourself** (don't send the user to Terminal): `TADCLIP_NO_OPEN=1 bash -c "$(curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh)"`. It needs no password and no developer tools. It takes about 15 minutes, so give it a long timeout or run it in the background; if it gets cut off, run it again, it picks up where it stopped. It installs into ~/.claude/skills/tadclip on every agent: some scripts look for files there.
2. **What it did:** It installs the tools (ffmpeg, Node 22, uv, Python packages, whisper, the Thai transcription venv), downloads the sounds, music and emoji, installs the `reel-helper` agent, links the skill into `~/.codex/skills` when Codex is there, and creates `.env` from `.env.example`. Everything goes in `~/.local` without Homebrew, so it never asks for the Mac password or Apple's developer tools.
3. **Keys.** Run `open -e ~/.claude/skills/tadclip/.env` and walk the user through step 3 above. Tell them audio and frames go to Google. Wait until they say they've saved it.
4. **Run `doctor.sh`** until it ends with `0 missing`. A Gemini 503 is Google being busy, not a bad key: say so and carry on.
5. **People rules.** Ask whether they have rules for who or what may appear in B-roll. If they do, write them into `people-rules.json` in the format of `people-rules.example.json`. If not, leave it as it is, and never add rules they didn't ask for.
6. **Optional extras (ask first; each is one command, and its weights go to `~/.cache`):**
   - `ELEVENLABS_API_KEY` in `.env`, from https://elevenlabs.io/app/developers/api-keys: only the vector explainer's narrator.
   - `APIFY_TOKEN` exported in the shell, from https://console.apify.com/settings/integrations: only Google Images search.
   - `bash scripts/setup_looks.sh`: film-stock looks (generates the LUTs, ~1 GB venv, a minute).
   - `bash scripts/setup_matte.sh`: the clean person cut-out for words behind the speaker (~2.4 GB with the model).
   - `bash scripts/setup_audioqa.sh`: pause detection on noisy recordings and voice super-resolution (~1.9 GB).
   - `bash scripts/setup_captions.sh`: only to add a new font to the caption templates.
7. **Tell the user it's ready.** They need a new session for the skill to show up. Their first reel is one sentence, as in step 5.

**Any other agent** (untested): tell it "Follow `~/.claude/skills/tadclip/SKILL.md` to edit this recording." Every step is a plain shell command.
