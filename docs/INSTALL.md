# Installing TadClip · วิธีติดตั้ง TadClip

About 10 minutes, up to 30 on a slow connection (a few GB to download). If the internet drops, run it again: it picks up where it stopped. Works in Claude Code and Codex.

ใช้เวลาประมาณ 10 นาที เน็ตช้าอาจถึง 30 นาที ส่วนใหญ่คือรอดาวน์โหลด ถ้าเน็ตหลุดกลางทาง สั่งติดตั้งเดิมอีกครั้งได้ ส่วนที่เสร็จแล้วจะข้ามไปเอง ใช้ได้ทั้ง Claude Code และ Codex

## Before you start · ก่อนเริ่ม

| You need · สิ่งที่ต้องมี | Details · รายละเอียด |
|---|---|
| A Mac with Apple silicon · Mac ชิป Apple (M1 ขึ้นไป) | Linux and Intel Macs are untested · ยังไม่ได้ทดสอบบน Linux และ Mac ชิป Intel |
| Claude Code or Codex · Claude Code หรือ Codex | [Claude Code](https://claude.com/claude-code) · [Codex](https://github.com/openai/codex). Install it first · ลงตัวนี้ก่อน |

## Step 1: Install · ขั้นที่ 1: ติดตั้ง

One line. Paste it into Terminal (⌘Space, type Terminal, Enter), or into Claude Code or Codex, which run it for you:

บรรทัดเดียว วางใน Terminal (กด ⌘Space พิมพ์ Terminal แล้วกด Enter) หรือวางใน Claude Code / Codex ให้มันรันให้:

```bash
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
```

It installs everything into your home folder. It does not ask for your Mac password, and you don't need Homebrew or Apple's developer tools. In Claude Code, click Yes when it asks to run a command. When it's done, the TadClip page opens in your browser. A timed log of the install is kept in `~/Library/Logs/TadClip/`.

ลงทุกอย่างไว้ในโฟลเดอร์ของคุณเอง ไม่ถามรหัสผ่านเครื่อง ไม่ต้องลง Homebrew หรือ developer tools ของ Apple ถ้าวางใน Claude Code แล้วขึ้นถามว่าจะให้รันคำสั่งไหม ให้กด Yes เสร็จแล้วหน้า TadClip จะเปิดขึ้นในเบราว์เซอร์ บันทึกการติดตั้งพร้อมเวลาอยู่ที่ `~/Library/Logs/TadClip/`

Or let your agent read the guide and do it · หรือให้ agent อ่านคู่มือแล้วติดตั้งเอง:

```text
Install TadClip: https://raw.githubusercontent.com/npnatt12/tadclip-public/main/docs/INSTALL.md
```

## Step 2 (optional): Open the key file · ขั้นที่ 2 (ไม่บังคับ): เปิดไฟล์คีย์

TadClip works without any key: skip to step 4. Two free keys make the reels more tailored. To add them, ask your agent to "open the TadClip key file", or paste this into Terminal:

TadClip ใช้ได้เลยโดยไม่ต้องมีคีย์ ข้ามไปขั้นที่ 4 ได้ ถ้าอยากให้คลิปตรงใจขึ้น ใส่คีย์ฟรี 2 ตัว: บอก agent ว่า "เปิดไฟล์คีย์ TadClip" หรือวางบรรทัดนี้ใน Terminal:

```bash
open -e ~/.claude/skills/tadclip/.env
```

Keep the file open for step 3. **Paste keys into this file, never into the chat.** It stays on your Mac.

เปิดไฟล์ค้างไว้สำหรับขั้นที่ 3 **วางคีย์ในไฟล์นี้เท่านั้น ห้ามวางในแชต** ไฟล์นี้อยู่ในเครื่องของคุณ ไม่ถูกส่งขึ้นไปไหน

## Step 3 (optional): Get the free keys · ขั้นที่ 3 (ไม่บังคับ): ขอคีย์ฟรี

**Gemini** (a more exact Thai transcript, B-roll checked against its line, pictures scored for you · ถอดเสียงไทยแม่นขึ้น ตรวจ B-roll ให้ตรงกับประโยค เลือกรูปให้)

1. Open **https://aistudio.google.com/apikey** and sign in with Google.<br>เปิดลิงก์แล้วล็อกอินด้วยบัญชี Google
2. Click **Create API key**, then copy it.<br>กด **Create API key** แล้วคัดลอกคีย์
3. Paste it right after `GEMINI_API_KEY=`, with no spaces or quotes.<br>วางต่อจาก `GEMINI_API_KEY=` ไม่ต้องเว้นวรรค ไม่ต้องใส่เครื่องหมายคำพูด

**Pexels** (more stock footage. Without it TadClip uses Mixkit and Wikimedia · ได้ฟุตเทจสต็อกเพิ่ม ถ้าไม่ใส่ TadClip จะใช้ Mixkit และ Wikimedia แทน)

1. Open **https://www.pexels.com/api/key/** and log in, or create a free account.<br>เปิดลิงก์แล้วล็อกอิน หรือสมัครบัญชีฟรี
2. If it asks about your project, fill in the short form.<br>ถ้าถามเรื่องโปรเจกต์ ก็กรอกสั้นๆ ได้เลย
3. Copy your key and paste it right after `PEXELS_API_KEY=`.<br>คัดลอกคีย์ แล้ววางต่อจาก `PEXELS_API_KEY=`

Save the file (⌘S) and close it. It should look like this, with your own keys:

กด ⌘S เพื่อเซฟแล้วปิดไฟล์ หน้าตาจะเป็นแบบนี้ แต่เป็นคีย์ของคุณเอง:

```text
GEMINI_API_KEY=your-gemini-key
PEXELS_API_KEY=your-pexels-key
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

The easiest way: the TadClip page (it opened after the install; later, double-click TadClip on the Desktop, then TadClip.app). Choose your clip, press **ตัดต่อให้หน่อย**.

ง่ายที่สุด: หน้า TadClip (เปิดขึ้นเองหลังติดตั้ง ครั้งต่อไปดับเบิลคลิก TadClip บนเดสก์ท็อป แล้วเปิด TadClip.app) เลือกคลิป แล้วกด **ตัดต่อให้หน่อย**

In the chat instead: quit and reopen the Claude app once (so it sees the new tools), start a new chat, then say:

ปิดแอป Claude แล้วเปิดใหม่หนึ่งครั้ง (ให้เห็นเครื่องมือที่เพิ่งลง) เปิดแชตใหม่ แล้วสั่งแบบนี้:

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
| `MISS GEMINI_API_KEY ... test call failed` | The key you pasted doesn't work. Copy it again (step 3), or delete the line: TadClip works without it.<br>คีย์ที่วางไว้ใช้ไม่ได้ คัดลอกใหม่อีกครั้ง (ขั้นที่ 3) หรือลบทิ้งก็ได้ TadClip ใช้ได้โดยไม่ต้องมีคีย์ |
| The agent doesn't know TadClip<br>agent ไม่รู้จัก TadClip | Quit and reopen the Claude app, then start a new chat.<br>ปิดแล้วเปิดแอป Claude ใหม่ แล้วเปิดแชตใหม่ |
| Any other `MISS` line<br>บรรทัด `MISS` อื่นๆ | It prints its own fix. Run it, or paste the install line again: it's safe to repeat.<br>บรรทัดนั้นจะบอกวิธีแก้ไว้ ทำตามนั้น หรือวางบรรทัดติดตั้งอีกครั้งก็ได้ ทำซ้ำได้ไม่มีผลเสีย |

**Update to the latest version · อัปเดตเวอร์ชันล่าสุด:** paste the install line again · วางบรรทัดติดตั้งเดิมอีกครั้ง

**Send us the logs · ส่งบันทึกให้ทีม:** `bash ~/.claude/skills/tadclip/scripts/logs.sh` (or tell Claude "เก็บบันทึก TadClip"). It gathers the install log, the app's events and recent TadClip chats into one folder in `/Users/Shared/TadClip-logs/`, with keys removed · รวมบันทึกการติดตั้ง เหตุการณ์ในแอป และแชต TadClip ล่าสุดไว้ในโฟลเดอร์เดียว ไม่มีคีย์ติดไป

**Privacy · ความเป็นส่วนตัว:** the speaker's audio and frames go to Google for the transcript and checks. On the free tier, Google may use them to improve its products ([terms](https://ai.google.dev/gemini-api/terms)). Get the speaker's OK before you edit someone else's recording.

เสียงและภาพของคนในคลิปจะถูกส่งไปที่ Google เพื่อถอดเสียงและตรวจคลิป ถ้าใช้คีย์ฟรี Google อาจนำไปปรับปรุงผลิตภัณฑ์ของเขาได้ ([ข้อกำหนด](https://ai.google.dev/gemini-api/terms)) ถ้าจะตัดคลิปของคนอื่น ขออนุญาตเจ้าตัวก่อน

---

## For the agent doing the install

Tell the user in plain words what you're installing and why. Never ask for keys in the chat.

1. **Run the installer yourself** (don't send the user to Terminal): `bash -c "$(curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh)"`. No password, no developer tools. Run it in the background: it takes about 10 minutes, up to 30 on a slow connection (the Thai transcription download is the longest). Don't ask for keys: TadClip works without them (step 3 below). Each step prints `== [n/8] ...`: when you check on it, tell the user that line. The last line is `TADCLIP_STATUS=ok`, or `TADCLIP_STATUS=incomplete N missing`: then fix what the MISS lines say (usually the internet dropped) and run it again, it skips what's done. It installs into ~/.claude/skills/tadclip on every agent: some scripts look for files there.
2. **What it did:** It installs the tools (ffmpeg, Node 22, uv, Python packages, whisper, the Thai transcription venv), downloads the sounds, music and emoji, installs the `reel-helper` agent, links the skill into `~/.codex/skills` when Codex is there, and creates `.env` from `.env.example`. Everything goes in `~/.local` without Homebrew, so it never asks for the Mac password or Apple's developer tools.
3. **Keys are optional: don't ask for them during the install.**
4. **Finish when setup prints `TADCLIP_STATUS=ok`** (or `doctor.sh` ends with `0 missing`). On `incomplete`, fix what the MISS lines say and run setup again: it skips what's done. A `note ~/.local/bin` line is not a fault: the app needs one restart.
5. **Close in Thai** (unless the user wrote in English): send the text of `~/.claude/skills/tadclip/docs/WELCOME.th.txt` as it is, then nothing long in English. It tells them to quit and reopen the Claude app once, how to start, the time, the optional keys and the three things to tell once.
6. **The three things, once, all optional.** If they answer: the speaker's name and the brand go into `~/.claude/skills/tadclip/profile.json` (`{"speaker": "...", "brand": "<folder>"}`; a new brand: its logo, tagline and LINE handle into `recipes/clubgig/brand/<name>/` like the Clubgig one). Rules for B-roll go into `people-rules.json` in the format of `people-rules.example.json`; never add rules they didn't ask for. If they want the keys: `open -e ~/.claude/skills/tadclip/.env` and walk them through step 3 above, and tell them audio and frames go to Google.
7. **Other extras only if they ask** (each one command, weights in `~/.cache`):
   - `ELEVENLABS_API_KEY` in `.env`, from https://elevenlabs.io/app/developers/api-keys: only the vector explainer's narrator.
   - `APIFY_TOKEN` exported in the shell, from https://console.apify.com/settings/integrations: only Google Images search.
   - `bash scripts/setup_looks.sh`: film-stock looks (generates the LUTs, ~1 GB venv, a minute).
   - `bash scripts/setup_matte.sh`: the clean person cut-out for words behind the speaker (~2.4 GB with the model).
   - `bash scripts/setup_audioqa.sh`: pause detection on noisy recordings and voice super-resolution (~1.9 GB).
   - `bash scripts/setup_captions.sh`: only to add a new font to the caption templates.

**Any other agent** (untested): tell it "Follow `~/.claude/skills/tadclip/SKILL.md` to edit this recording." Every step is a plain shell command.
