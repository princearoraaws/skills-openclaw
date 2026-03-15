---
name: publora-threads
description: >
  Post or schedule content to Threads using the Publora API. Use this skill
  when the user wants to publish or schedule a Threads post via Publora.
---

# Publora — Threads

Threads platform skill for the Publora API. For auth, core scheduling, media upload, and workspace/webhook docs, see the `publora` core skill.

**Base URL:** `https://api.publora.com/api/v1`  
**Header:** `x-publora-key: sk_YOUR_KEY`  
**Platform ID format:** `threads-{accountId}`

## ⚠️ Temporary Restriction — Thread Nesting Unavailable

**Multi-threaded nested posts are temporarily unavailable** on Threads due to Threads app reconnection status.

This means: content over 500 characters that would normally auto-split into connected reply chains does **not** work right now.

**What still works normally:**
- Single posts (text, images, videos, carousels)
- Standalone posts under 500 characters

Contact support@publora.com for updates on when thread nesting will be restored.

## Platform Limits (API)

| Property | API Limit | Notes |
|----------|-----------|-------|
| Text | **500 characters** | 10,000 via text attachment |
| Images | Up to 20 × 8 MB | JPEG, PNG |
| Video | **5 min** / 500 MB | MP4, MOV |
| Max links | 5 per post | — |
| Text only | ✅ Yes | — |
| Threading | ⚠️ Temporarily unavailable | See above |
| Rate limit | 250 posts/24hr | 1,000 replies/24hr |

## Post a Single Thread

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Building in public is the best marketing strategy. Here\'s why 👇',
    platforms: ['threads-17841412345678']
  })
});
```

## Schedule a Post

```javascript
body: JSON.stringify({
  content: 'Your Threads post here',
  platforms: ['threads-17841412345678'],
  scheduledTime: '2026-03-20T10:00:00.000Z'
})
```

## Post with Image

```javascript
// Step 1: Create post
const post = await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Caption for your image post',
    platforms: ['threads-17841412345678']
  })
}).then(r => r.json());

// Step 2: Get upload URL
const upload = await fetch('https://api.publora.com/api/v1/get-upload-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    postGroupId: post.postGroupId,
    fileName: 'photo.jpg',
    contentType: 'image/jpeg',
    type: 'image'
  })
}).then(r => r.json());

// Step 3: Upload to S3
await fetch(upload.uploadUrl, {
  method: 'PUT',
  headers: { 'Content-Type': 'image/jpeg' },
  body: imageBytes
});
```

## Thread Nesting (when available)

When thread nesting is restored, you can split long content using `---` on its own line:

```javascript
body: JSON.stringify({
  content: 'First post in thread.\n\n---\n\nSecond post continues the thought.\n\n---\n\nFinal post wraps up.',
  platforms: ['threads-17841412345678']
})
```

> ⚠️ Currently disabled. Single posts and carousels work normally.

## Platform Quirks

- **Connected via Meta OAuth** — same account as Instagram
- **5 links per post max** — Threads enforces this at the API level
- **PNG supported** — unlike Instagram, Threads accepts PNG images
- **Threading restriction** — see the notice at the top of this skill
