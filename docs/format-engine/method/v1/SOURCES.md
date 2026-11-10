# Sources

These are the external sources found for this method, with what each one was used for. Tags [S1]..[S13] match
METHOD.md. "Read" describes how far each source was actually reached, so no source is claimed to have been read
further than it was.

| tag | source | URL | read | what was used |
|---|---|---|---|---|
| S1 | Cutting, DeLong & Nothelfer (2010), "Attention and the evolution of Hollywood film", *Psychological Science* 21(3) | https://www.psychologicalscience.org/journals/psychological-science/0956797610361679/ (DOI 10.1177/0956797610361679) | journal abstract page and summaries via search; the full text was not reached (the fetch timed out or returned 403) | Over 70 years of films, shot lengths became more correlated with their neighbours, and the structure approaches a 1/f pattern that the authors link to attention. Used to treat edit rhythm as a distribution (median **and** p90, and the cut-kind mix) instead of one rate (METHOD R2, S2). |
| S2 | Cerf, Harel, Einhäuser & Koch (2007/2008), "Predicting human gaze using low-level saliency combined with face detection", *NIPS 20* | https://proceedings.neurips.cc/paper/2007/hash/708f3cf8100d5e71834b1db77dfa15d6-Abstract.html | abstract | Observers looked at a face within their first two fixations over 80 % of the time, without being told to. Used for the face as the anchor of every text zone, the "never cover the face" geometry test (F1) and the face gate (C1). |
| S3 | Mayer (2008), "Applying the science of learning: Evidence-based principles for the design of multimedia instruction", *American Psychologist* 63(8) | https://pubmed.ncbi.nlm.nih.gov/19014238/ | abstract; principle wording from secondary summaries (see note) | Signalling (cues that pick out the key words help) and redundancy (full on-screen text repeating fast narration can hurt; short keywords next to what they describe are the exception). Used to separate punch words from captions and to keep on-screen text short (R3, F2). |
| S4 | Chan, Kruger & Doherty (2022), "An investigation of subtitles as learning support in university education", *JoSTrans* 38; also Kruger, Hefer & Matthew (2014), *Journal of Eye Movement Research* | https://www.jostrans.org/article/view/7984 ; https://doaj.org/article/bb03fa1fdde148a7b150e6efc8ca75ec | abstracts | In lecture studies, first-language subtitles improved comprehension with no significant difference in measured cognitive load. Used for "captions on by default" (F2). |
| S5 | Winskel, Radach & Luksaneeyanawin (2009), "Eye movements when reading spaced and unspaced Thai and English", *Journal of Memory and Language* | https://researchers.westernsydney.edu.au/en/publications/eye-movements-when-reading-spaced-and-unspaced-thai-and-english-a/ (DOI 10.1016/j.jml.2009.07.002) | abstract | Spaces inserted into Thai helped word recognition, though they did not change eye guidance. Used for breaking Thai only at phrase boundaries and keeping phrase spaces (F3). |
| S6 | Netflix Partner Help Center, "Thai Timed Text Style Guide" | https://partnerhelp.netflixstudios.com/hc/en-us/articles/220448308-Thai-Timed-Text-Style-Guide | page | 35 characters per line (tone marks and upper or lower vowels not counted); up to 17 characters/s for adult programmes (13 for children); 2 lines at most, 1 preferred; bottom-heavy line breaks. Used as the Thai reading limits (F2, C1). |
| S7 | Netflix Partner Help Center, "Timed Text Style Guide: General Requirements" | https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements | page | Minimum 5/6 s and maximum 7 s per subtitle event; 2 lines at most; position subtitles so they do not overlap on-screen text. Used for the minimum display time and the "no two text layers" gate (F2, C1). |
| S9 | TikTok Ads Help Center, "Creative best practices for performance ads" | https://ads.tiktok.com/help/article/creative-best-practices?lang=en | page | Introduce the proposition within the first 3 s and prioritise the hook in the first 6 s; use captions or overlays for context; about 5–10 words per second when using text; keep content inside the UI safe zone. Used for the hook check (C3); the words-per-second figure is treated as an upper bound, not a target (F2). |
| S10 | YouTube Help, audience retention / key moments (answer 9314415) | https://support.google.com/youtube/answer/9314415 | page | The retention report shows dips where viewers leave and spikes where they rewatch; "intro" is the share still watching after 30 s; the guidance is to experiment with the opening. Used to justify a separate hook check and to make the critic report conformance, not predicted retention (C3). |
| S11 | EBU R 128, "Loudness normalisation and permitted maximum level of audio signals" | https://tech.ebu.ch/publications/r128 | publication page | Programmes are normalised to a target loudness (−23 LUFS in broadcast). Used for the argument that a delivered file's loudness reflects the distributor's normalisation, so `audio.lufs` is not saved as a creator trait (R6). |
| S12 | W3C, Web Content Accessibility Guidelines (WCAG) 2.2 | https://www.w3.org/TR/WCAG22/ | the relevant success criteria | 1.4.3: text contrast at least 4.5:1. 1.4.11: non-text contrast 3:1. 1.2.2: captions for prerecorded audio. 2.3.1: no more than three flashes in any one second. Used for the contrast, captions and flashing gates (F2, C1). |

## Looked for, not verified, not relied on
- **S8: the BBC Subtitle Guidelines** (bbc.github.io/subtitle-guidelines). The primary page returned 404 and the BBC
  site refused the fetch. Secondary pages attribute 160–180 words per minute and about 0.3 s per word to it. The
  0.3 s/word floor in METHOD is kept as TadClip's own rule (the builder already enforces it for `textfx`), not as a
  BBC citation.
- **S13: Meta's Reels safe zones.** Only third-party pages were found (top ~14 %, bottom ~35 % for ads, with
  conflicting figures). METHOD relies on the builder's own safe-area lever (`platform`, `layout.capBottom`, the y 1470
  rule) instead.
- **The −14 LUFS target for Instagram/TikTok** appears only in vendor blogs and is not used.

Note on S3: the PubMed abstract confirms the paper and its principle-based framing. The exact wording of the
redundancy exception (short, key-word text placed next to what it describes) comes from university teaching summaries
found in the same search, not from the paper's full text.
