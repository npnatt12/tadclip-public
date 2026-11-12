# Sound effects and music (TadClip's own + CC0)

Everything ships or downloads under terms that allow a paid product. Mixkit is gone (11-12): its User Terms forbid
collating its items and fetching them by script, which the old installer did.

- **TadClip's own sounds** ship in this repo: `library/sfx/own-*.wav`, 48 sounds (whooshes, risers, impacts, UI pops
  and clicks, chimes, meme reactions, foley). `scripts/sfx_synth.py` makes them from code (no recording, no third-party
  source); they are dedicated CC0 1.0. They keep the old kit's names (`whoosh-1`, `impact-2`, ...) so recipes are
  unchanged. `sfx_synth.py page` writes an audition page.
- **The CC0 pack** ships in this repo: `library/sfx/cc0-*.wav`, 30 Freesound recordings under CC0 1.0, each checked by
  hand (the page shows CC0; the uploader recorded or made it). `scripts/cc0_pack.py list` shows sources.
- **Music:** 23 beds from FreePD.com, CC0 1.0 ("Can I include this music in an app that generates movies for users?
  YES!", freepd.com, archived 2024-05-28). `scripts/library_restore.py` downloads them from TadClip's release
  `music-v1` (fallback: the archived freepd.com file) and checks each against the sha256 in `library/music/manifest.json`.
  Each entry names the track and its composer.

Memes are not included. Clips and sounds you add with `scripts/meme_add.py` are your responsibility.
