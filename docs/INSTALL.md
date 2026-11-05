# Installing TadClip

About 15 minutes, most of it downloads. Works in Claude Code and Codex.

## Before you start

| You need | Get it |
|---|---|
| A Mac with Apple silicon | Linux and Intel Macs are untested |
| Claude Code or Codex | [Claude Code](https://claude.com/claude-code) · [Codex](https://github.com/openai/codex) |

## Step 1: Install

Open Terminal (⌘Space, type Terminal) and paste this one line:

```bash
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
```

It installs what it needs, including Homebrew, and may ask for your Mac password. It works for Claude Code and Codex: install your agent first, so the skill gets linked in.

## Step 2: Open the key file

The installer does this for you. To open it again, paste this into Terminal:

```bash
open -e ~/.claude/skills/tadclip/.env
```

Keep the file open for step 3. **Paste keys into this file, never into the chat.** It stays on your Mac and is never committed.

## Step 3: Get your two free keys

**Gemini** (Thai transcript and B-roll checks)
1. Open **https://aistudio.google.com/apikey** and sign in with Google.
2. Click **Create API key**, then copy it.
3. Paste it right after `GEMINI_API_KEY=`, with no spaces or quotes.

**Pexels** (stock footage)
1. Open **https://www.pexels.com/api/key/** and log in, or create a free account.
2. If it asks about your project, fill in the short form.
3. Copy your key and paste it right after `PEXELS_API_KEY=`.

Save the file (⌘S) and close it. It should look like this, with your own keys:

```text
GEMINI_API_KEY=your-gemini-key
PEXELS_API_KEY=your-pexels-key
```

## Step 4: Check it

Tell the agent "run the TadClip doctor", or paste this into Terminal:

```bash
bash ~/.claude/skills/tadclip/scripts/doctor.sh
```

You're ready when it ends with `0 missing`. Lines marked `opt` are optional.

## Step 5: Edit your first reel

Start a new session so the agent sees the skill, then say:

> ตัดต่อคลิปนี้ ~/Downloads/my-video.mov

ClubGig is the default. To copy a creator's style:

> ตัดต่อคลิปนี้ให้เป็นสไตล์ @someone ให้หน่อย ~/Downloads/my-video.mov

For a brand other than Clubgig, you'll be asked once for its logo and LINE handle.

**On Codex:** the edit runs in your session instead of in helper agents. `@someone` needs a logged-in browser, so if your agent can't reach one, paste links to 3 of their reels.

## If something goes wrong

| What you see | What to do |
|---|---|
| `503` from Gemini | Google is busy, your key is fine. Try again later |
| `429` from Gemini | The free daily limit is used up. It was 20 requests a day when we measured it, resetting at 15:00 Bangkok time ([current limits](https://ai.google.dev/gemini-api/docs/rate-limits)) |
| `MISS GEMINI_API_KEY` or `MISS PEXELS_API_KEY` | The key isn't in the file, or the file wasn't saved. Repeat steps 2 and 3 |
| The agent doesn't know TadClip | Start a new session |
| Any other `MISS` line | It prints its own fix. Run it, or re-run `bash ~/.claude/skills/tadclip/scripts/setup.sh`, which is safe to repeat |

**Update to the latest version:**

```bash
curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh | bash
```

**Privacy:** the speaker's audio and frames go to Google for the transcript and checks. On the free tier, Google may use them to improve its products ([terms](https://ai.google.dev/gemini-api/terms)). Get the speaker's OK before you edit someone else's recording.

---

## For the agent doing the install

Tell the user in plain words what you're installing and why. Never ask for keys in the chat.

1. **Run the installer:** `TADCLIP_NO_OPEN=1 bash -c "$(curl -fsSL https://raw.githubusercontent.com/npnatt12/tadclip-public/main/install.sh)"`. It clones into ~/.claude/skills/tadclip, on every agent: some scripts look for files there.
2. **What it did:** It installs the tools (ffmpeg, Node 22, uv, Python packages, whisper, the Thai transcription venv), downloads the sounds, music and emoji, installs the `reel-helper` agent, links the skill into `~/.codex/skills` when Codex is there, and creates `.env` from `.env.example`. If Homebrew is missing, ask the user to install it from https://brew.sh, then re-run.
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
