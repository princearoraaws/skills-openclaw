---
name: documentary-video-maker
version: "1.0.0"
displayName: "Documentary Video Maker — Create Mini Documentaries and Docuseries Videos"
description: >
  Create compelling mini-documentaries, docuseries episodes, and investigative video features from raw interviews, archival footage, and field recordings. NemoVideo structures narrative arcs from unscripted material — weaving interview soundbites with b-roll, data visualizations, and archival media into stories that inform, persuade, and hold attention across 5-30 minute runtimes.
metadata: {"openclaw": {"emoji": "🎥", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Documentary Video Maker — Mini Documentaries and Docuseries Videos

The documentary format has undergone a migration that mirrors what happened to music, publishing, and journalism before it: the 90-minute theatrical documentary still exists but the growth is in shorter forms — the 8-minute YouTube mini-doc, the 20-minute podcast-style video essay, the 5-part docuseries released weekly on a creator's channel — formats that don't require a distribution deal or a festival premiere but do require the same fundamental skills that make documentary filmmaking the hardest category of video production: finding the story inside the raw material. A scripted video starts with a script. A documentary starts with 40 hours of interviews, field recordings, archival clips, and b-roll that contain a story the filmmaker can feel but hasn't yet articulated, and the editing process is the act of discovering that story by watching everything, identifying the 15 soundbites that carry the narrative, arranging them in an order that creates understanding, and filling the gaps with visual evidence that supports each claim — a process that takes professional editors weeks and amateur filmmakers months, which is why most documentary projects die in editing, not in filming. NemoVideo compresses this process by analyzing interview transcripts for narrative structure (setup, conflict, complication, resolution), identifying the strongest soundbites by emotional intensity and informational density, suggesting a narrative sequence, assembling a rough cut with b-roll matched to topic, and producing a first draft that the filmmaker can refine — transforming the editing process from "stare at 40 hours of footage" to "review and adjust a structured draft."

## Use Cases

1. **YouTube Mini-Documentary (8-12 min)** — A creator investigates why a local factory closed and 400 people lost their jobs. Source: 6 interview recordings (45 min each), drone footage of the empty factory, archival news clips, county economic data. NemoVideo transcribes all interviews, identifies the narrative arc (thriving factory → corporate acquisition → cost-cutting → closure → community impact → what's next), selects the 20 strongest soundbites, arranges them in chronological narrative, intercuts with b-roll and data visualizations (employment graph, tax revenue decline), and produces a 10-minute rough cut with music and chapter markers.
2. **Brand Documentary / Origin Story (3-5 min)** — A company wants a documentary-style brand film instead of a corporate video. NemoVideo structures: the founder's motivation (interview soundbite), the early struggle (archival photos, early product prototypes), the breakthrough moment (customer or market validation), the current state (facility footage, team at work), and the forward vision (founder speaking to camera). Documentary pacing — not corporate polish. Imperfections are features, not bugs.
3. **Social Issue Docuseries (5 episodes × 8 min)** — A nonprofit produces a 5-part series on housing insecurity. Each episode follows a different person. NemoVideo structures each episode as a self-contained story (problem → context → personal journey → systemic analysis → call to action) while maintaining series-level continuity through recurring visual motifs, consistent color grade, and episode-end teasers for the next installment.
4. **Historical Documentary from Archives (10-15 min)** — A local history society has digitized 200 photos, 30 newspaper clippings, and 5 oral-history audio recordings from the 1950s. NemoVideo animates the photos (Ken Burns pan-and-zoom), overlays newspaper text with highlight annotations, syncs oral-history audio to visual timelines, and produces a 12-minute documentary narrated by the archival voices with supplementary text cards for context.
5. **Conference / Event Documentary (5-8 min)** — Beyond a recap, a documentary treatment of a conference: the theme explored through speaker insights, attendee perspectives, and behind-the-scenes footage. NemoVideo identifies the 3-4 most thematically resonant speaker clips, interweaves them with candid attendee interviews, and structures the film around the conference's central question rather than its schedule.

## How It Works

### Step 1 — Upload All Source Material
Provide interview recordings, b-roll footage, archival media (photos, newspaper clips, old video), data files (for visualization), and any narration scripts. NemoVideo accepts up to 50 hours of raw material per project.

### Step 2 — Define the Story
Specify the documentary type, narrative focus, target length, and any must-include moments or soundbites. Alternatively, let NemoVideo analyze the transcripts and propose a narrative structure.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "documentary-video-maker",
    "prompt": "Create a 10-minute mini-documentary about the closure of Westfield Manufacturing and its community impact. Source: 6 interviews (factory workers, town mayor, union rep, company spokesperson, school principal, local business owner), 45 min each. Plus drone footage of empty factory, archival local news clips from 2018 opening ceremony, county employment data 2015-2026. Narrative arc: (1) Cold open — drone over silent factory, 15 sec. (2) What Westfield was — archival clips of opening day, worker interviews describing the good years, 90 sec. (3) The acquisition — company spokesperson explaining the merger, workers describing the mood shift, 90 sec. (4) The closure announcement — union rep and workers reacting, news clip, 60 sec. (5) The ripple effect — mayor on tax revenue decline (animate the graph), school principal on enrollment drop, local business owner on lost customers, 120 sec. (6) Where are they now — 3 workers describing current situations, mix of resilience and struggle, 90 sec. (7) What comes next — mayor on redevelopment plans, workers on retraining, 60 sec. (8) Closing — drone pulling away from factory, text cards with key stats, 30 sec. Color grade: slightly desaturated, documentary-neutral. Music: sparse piano, builds to strings in the ripple-effect section.",
    "duration": "10 min",
    "style": "mini-documentary",
    "narrative_analysis": true,
    "data_visualization": true,
    "archival_animation": true,
    "chapters": true,
    "music": "sparse-piano-to-strings",
    "format": "16:9"
  }'
```

### Step 4 — Refine the Rough Cut
Review the AI-assembled narrative. Swap soundbites, adjust pacing, refine b-roll selections. The rough cut is the starting point — human editorial judgment shapes the final film.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the subject, source material, and narrative arc |
| `duration` | string | | Target length: "5 min", "10 min", "15 min", "20 min" |
| `style` | string | | "mini-documentary", "brand-origin", "docuseries-episode", "historical-archive", "event-documentary" |
| `narrative_analysis` | boolean | | AI-analyze transcripts for narrative structure and strongest soundbites (default: true) |
| `data_visualization` | boolean | | Generate animated charts and graphs from provided data (default: true) |
| `archival_animation` | boolean | | Apply Ken Burns effect to photos and annotate archival text (default: true) |
| `chapters` | boolean | | Generate chapter markers for narrative sections (default: true) |
| `music` | string | | "sparse-piano", "ambient-documentary", "tension-strings", "hopeful-acoustic" |
| `format` | string | | "16:9", "9:16" |

## Output Example

```json
{
  "job_id": "dvm-20260328-001",
  "status": "completed",
  "title": "After the Whistle — The Westfield Manufacturing Story",
  "duration_seconds": 612,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 186.4,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/dvm-20260328-001.mp4",
  "chapters": [
    {"title": "Cold Open — The Empty Factory", "start": "0:00"},
    {"title": "The Good Years", "start": "0:15"},
    {"title": "The Acquisition", "start": "1:45"},
    {"title": "The Closure", "start": "3:15"},
    {"title": "The Ripple Effect", "start": "4:15"},
    {"title": "Where Are They Now", "start": "6:15"},
    {"title": "What Comes Next", "start": "7:45"},
    {"title": "Closing", "start": "8:45"}
  ],
  "soundbites_selected": 24,
  "interviews_analyzed": 6,
  "total_source_hours": 4.5,
  "data_visualizations": 3,
  "archival_clips_used": 8
}
```

## Tips

1. **Cold open with the strongest visual, not the explanation** — The silent drone shot over the empty factory asks a question the viewer needs answered. Starting with "In 2018, Westfield Manufacturing was acquired by..." is a lecture. Let the image create curiosity.
2. **Soundbites under 20 seconds** — The best documentary editing keeps individual interview clips under 20 seconds. Longer clips lose the viewer. If someone said something important in 45 seconds, NemoVideo finds the 12-second core.
3. **B-roll should evidence, not decorate** — When the mayor says "tax revenue dropped 34%," the graph should appear. When the worker says "the parking lot was full every morning," show the empty lot. Every b-roll cut should support the audio.
4. **Archival media with Ken Burns animation holds attention** — A static photo loses the viewer in 3 seconds. The same photo with a slow zoom into a face or a pan across a crowd holds for 8-10 seconds — enough to deliver the narration over it.
5. **End with a question, not an answer** — The most rewatched and shared documentaries end with ambiguity: "the factory is still empty" rather than "and they all moved on." Open endings stay with the viewer.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / Vimeo / streaming platform |
| MP4 9:16 | 1080p | TikTok / Reels documentary clip |
| MP4 1:1 | 1080p | Twitter / LinkedIn / Facebook |
| SRT/VTT | — | Subtitle files for accessibility |

## Related Skills

- [interview-video-editor](/skills/interview-video-editor) — Interview recording editing
- [reaction-video-maker](/skills/reaction-video-maker) — Reaction content production
- [vlog-video-maker](/skills/vlog-video-maker) — Vlog creation and editing
