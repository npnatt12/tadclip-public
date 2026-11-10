# Teardown: {{account}} · {{reel_id}}

> `{{...}}` placeholders are filled by the script from the spec JSON (`format_spec.py` v2) and the study file.
> Sections marked **[agent]** are written by the teardown agent (`briefs/teardown.md`) following REA.md.
> Every row carries a basis: measured · derived · looked · inferred · unknown.

## 0. At a glance [agent]
One paragraph covering what this video is, its hook pattern, its beat structure in one line, and the 2–3 things worth
learning from it.

## 1. The numbers [script]
| field | value | basis |
|---|---|---|
| length | {{seconds}} s · {{w}}x{{h}} | measured |
| all cut detections | {{cuts.n}} ({{cuts.per_min}}/min) | measured |
| shot cuts (the speaker's shot changes) | {{len(cuts.shot_cuts)}} ({{cuts.shot_cuts_per_min}}/min) | measured |
| insert changes (something else changes) | {{len(cuts.insert_changes)}} ({{insert_per_min}}/min) | derived |
| shot length median / p90 | {{cuts.shot_median}} s / {{cuts.shot_p90}} s | measured |
| first detection | {{cuts.first}} s | measured |
| face on screen | {{face.share}} of frames · top {{face.top}} · height {{face.height}} · cx {{face.cx}} | measured |
| text on screen (all, incl. footage) | {{text.share_of_time}} of time · first at {{text.first_seen}} s · {{text.events}} events | measured |
| pauses | {{audio.pauses_per_min}}/min · longest {{audio.longest_pause}} s | measured |
| views / engagement | {{study.views or "not available"}} | measured (study) |

## 2. Cut audit [script fills the list, agent checks it]
| t | measured label | sheet shows | corrected label | note |
|---|---|---|---|---|
| {{t}} | {{shot/insert}} | [agent] | [agent] | second face / graphic onset / cut to footage / ok |

Corrected: **hook end {{hook_end}} s** · body shot cuts {{body_shot_n}} in {{body_seconds}} s =
**{{body_shot_per_min}}/min** · body shot median {{body_shot_median}} s · cuts landing together with panel/B-roll
changes: {{coincident}} [agent].

## 3. Own graphics [script lists candidates; agent assigns roles]
| t0–t1 | text (approx.) | role | y | line_h | rows | plate | letters | basis |
|---|---|---|---|---|---|---|---|---|
| {{t0}}–{{t1}} | {{text}} | [agent] | {{y}} | {{line_h}} | {{rows}} | {{plate}} | {{letters}} | measured |

Footage text (screens, UIs, signs) is excluded: {{n_footage}} events.

## 4. Second by second
### 4a. First 10 seconds [script + agent]
| s | frame on sheet | layout [agent] | own text on screen | cut at | what is said |
|---|---|---|---|---|---|
| 0 | {{frame_at_0}} | | {{text_at_0}} | {{cut}} | {{transcript or "unknown"}} |
| … | | | | | |

### 4b. Beats [agent, times from the script]
| # | t0–t1 | layout | on screen | said | shot / insert cuts | job | evidence |
|---|---|---|---|---|---|---|---|
| 1 | 0.00–{{hook_end}} | | | | {{n}} / {{n}} | promise / question / … | frame {{t}}, text {{t0}} |

## 5. The hook [agent]
- Frame 0: …
- Promise or question visible at: {{t}} s (TikTok asks ≤ 3 s [S9]) → within / outside.
- Pattern: claim-on-screen / question / promise-headline / result-first / contrast / list-promise / pov.
- Mechanics: hook length {{hook_end}} s, {{n}} cuts inside it, first own text at {{text.first_seen}} s, face
  {{in/out}}.

## 6. Recurring devices [agent]
| device (by function) | when | where (y) | job for the viewer | seen | lever to rebuild |
|---|---|---|---|---|---|

## 7. Why it holds attention [agent]
At most five reasons, each a feature, a mechanism with its source, and an evidence level. Phrase them as "consistent
with", never "causes".

## 8. What we know, what we looked at, what we can't know [agent]
| measured | looked | unknown |
|---|---|---|

## 9. Take this, don't copy that [agent]
| device / element | take (the system) | make your own (never copy) |
|---|---|---|
Standing rule: never copy the creator's face, words, series name, logo or handle, music, footage, or the exact look
that identifies them. Ideas and methods are free to use; expression is not [S14][S15]. Platforms also favour
originals [S17]. Not legal advice.

## 10. Your brief [agent]
- **Your angle:** <the user's line>
- **Length:** {{target_seconds}} s → beat plan:
| beat | job | your seconds | device | what you need to film or gather |
|---|---|---|---|---|
- **Rhythm targets:** shot cuts {{body_shot_per_min ± band}}/min, insert changes {{insert_per_min ± band}}/min; reach
  them with take boundaries at sentence starts (and panel/B-roll clips starting on them if `coincident`), never by
  cutting words.
- **Hook:** pattern …; show the promise by 3 s; 2–3 original line shapes.
- **Make it yours:** series name, palette, type, one device the creator doesn't use.
- **Levers:** reel.json fragment or the list of beats.
- **Missing material:** drop or replace.
