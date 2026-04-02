---
name: aivideomakerai
version: "1.0.0"
displayName: "AI Video Maker AI — Create Stunning Videos from Text, Images & Ideas"
description: >
  Drop a concept, a few images, or a script and watch aivideomakerai turn it into a polished, shareable video in minutes. This skill handles everything from scene assembly and transitions to captions and background music suggestions — so you skip the timeline headaches. Whether you're a content creator, marketer, or small business owner, aivideomakerai helps you produce eye-catching videos without touching editing software.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm here to help you create compelling videos with aivideomakerai — just tell me your topic, style, and target platform, and I'll build a complete video concept or production-ready output for you. What video would you like to make today?

**Try saying:**
- "Create a 30-second promotional video for my new coffee brand targeting young professionals on Instagram"
- "Turn this 5-point blog post about home workouts into a 60-second explainer video with text overlays and upbeat pacing"
- "Make a birthday tribute video using 10 photos with a warm, nostalgic feel and soft background music"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/aivideomakerai/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# From Blank Canvas to Finished Video — Fast

Most people have a story to tell but no time to learn video editing. aivideomakerai bridges that gap by turning your raw ideas — a product description, a blog post, a handful of photos — into a structured, visually engaging video ready for social media, presentations, or marketing campaigns.

You describe what you want: the mood, the message, the audience, the length. aivideomakerai maps that into a scene-by-scene plan, suggests visuals, writes on-screen text, and recommends pacing. It's like having a video producer in your pocket who never needs a brief twice.

The skill is built for speed without sacrificing quality. Whether you need a 15-second Instagram reel, a 2-minute explainer, or a product showcase, aivideomakerai gives you a production-ready blueprint — and in supported environments, it can generate the video directly. No prior editing experience required.

## Directing Your Video Requests

Every prompt you send — whether a text description, uploaded image, or raw concept — is parsed by AI Video Maker AI's intent engine and routed to the appropriate generation pipeline: text-to-video, image-to-video, or storyboard assembly.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering Backend Reference

AI Video Maker AI processes all generation jobs on a distributed cloud rendering backend, meaning your video assets are compiled, diffused, and encoded server-side without taxing your local device. Render queues are managed dynamically, so complex multi-scene productions are handled with the same API surface as single-clip requests.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `aivideomakerai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Best Practices

Be specific about your audience and platform upfront. aivideomakerai produces noticeably better results when you say 'a 15-second TikTok for Gen Z fitness enthusiasts' versus 'a fitness video.' Platform dimensions, tone, and pacing all shift based on that context.

When working with images or existing footage, describe the emotional tone you want — 'energetic and punchy' or 'calm and cinematic' — rather than just listing technical specs. aivideomakerai uses tone cues to make smarter decisions about transitions, text timing, and music style.

Iterate in rounds. Start with a rough concept request, review the scene plan aivideomakerai produces, then refine individual scenes rather than restarting from scratch. This staged approach keeps your creative direction intact while letting the AI handle the structural heavy lifting. Finally, always specify your target video length — it prevents over-stuffed scripts and keeps the final output tight and watchable.

## Common Workflows

One of the most popular ways to use aivideomakerai is the idea-to-script-to-video pipeline. You start with a raw concept — say, launching a new product — and aivideomakerai generates a full scene breakdown, voiceover script, and caption suggestions before any footage is touched. This is especially useful for social media managers juggling multiple campaigns.

Another common workflow is the image-to-video conversion. Upload a collection of photos from an event, a product shoot, or a travel trip, and aivideomakerai sequences them into a cohesive video with suggested transitions, title cards, and timing that matches your chosen mood.

For content repurposing, many users paste in a YouTube transcript or article and ask aivideomakerai to reformat it as a short-form vertical video for TikTok or Reels — complete with punchy hooks, text overlays, and call-to-action slides. This workflow alone can save hours of manual reformatting each week.
