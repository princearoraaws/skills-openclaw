---
name: publora-instagram
description: >
  Post or schedule content to Instagram using the Publora API. Use this skill
  when the user wants to publish images, reels, stories, or carousels to
  Instagram via Publora.
---

# Publora — Instagram

Instagram platform skill for the Publora API. For auth, core scheduling, media upload, and workspace/webhook docs, see the `publora` core skill.

**Base URL:** `https://api.publora.com/api/v1`  
**Header:** `x-publora-key: sk_YOUR_KEY`  
**Platform ID format:** `instagram-{accountId}`

## Requirements

- **Instagram Business account** (personal and Creator accounts are NOT supported by the Instagram Graph API)
- Account must be connected to a Facebook Page
- Connected via OAuth through the Publora dashboard

## Platform Limits (API)

> ⚠️ Instagram API is significantly more restrictive than the native app.

| Property | API Limit | Native App |
|----------|-----------|-----------|
| Caption | **2,200 characters** | 2,200 |
| Images | **10 × 8 MB** | 20 images |
| Image format | **JPEG only** ⚠️ | PNG, GIF also work |
| Mixed carousel | ❌ No images + videos | ✅ |
| Reels duration | **90 seconds** ⚠️ | 15–20 minutes |
| Reels size | 300 MB | — |
| Carousel video | 60s per clip / 300 MB | — |
| Text only | ❌ Media required | — |
| Rate limit | 50 posts/24hr | — |

First 125 characters visible before "more".

**Common errors:**
- `(#10) The user is not an Instagram Business` — Creator accounts not supported, switch to Business
- `Error 2207010` — caption exceeds 2,200 chars
- `Error 2207004` — image exceeds 8 MB
- `Error 9, Subcode 2207042` — rate limit reached

## Post an Image

```javascript
// Step 1: Create the post
const post = await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Your caption here ✨ #hashtag',
    platforms: ['instagram-17841412345678'],
    scheduledTime: '2026-03-20T12:00:00.000Z'
  })
}).then(r => r.json());

// Step 2: Get upload URL
const upload = await fetch('https://api.publora.com/api/v1/get-upload-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    postGroupId: post.postGroupId,
    fileName: 'photo.jpg',
    contentType: 'image/jpeg',   // ⚠️ JPEG only for Instagram
    type: 'image'
  })
}).then(r => r.json());

// Step 3: Upload to S3
await fetch(upload.uploadUrl, {
  method: 'PUT',
  headers: { 'Content-Type': 'image/jpeg' },
  body: imageFileBytes
});
```

## Post a Carousel (up to 10 images)

Call `get-upload-url` N times with the **same `postGroupId`**:

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Swipe through our product highlights! 👆',
    'platforms': ['instagram-17841412345678'],
    'scheduledTime': '2026-03-20T12:00:00.000Z'
}).json()

# Upload each image (max 10)
images = ['slide1.jpg', 'slide2.jpg', 'slide3.jpg']
for img_path in images:
    upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
        'postGroupId': post['postGroupId'],
        'fileName': img_path,
        'contentType': 'image/jpeg',
        'type': 'image'
    }).json()
    with open(img_path, 'rb') as f:
        requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

## Post a Reel (video, max 90s via API)

```javascript
// Create post, then upload video via get-upload-url with type: 'video'
const post = await createPost({
  content: 'Check out our latest Reel! 🎬',
  platforms: ['instagram-17841412345678']
});

const upload = await getUploadUrl({
  postGroupId: post.postGroupId,
  fileName: 'reel.mp4',
  contentType: 'video/mp4',
  type: 'video'
});
// Then PUT the video file to upload.uploadUrl
```

> ⚠️ Reels via API are limited to **90 seconds**. Longer videos will be rejected.

## Platform Quirks

- **JPEG only**: The Instagram Graph API rejects PNG and GIF. Convert images to JPEG before uploading. Publora does NOT auto-convert for Instagram.
- **Business accounts only**: Creator accounts (`(#10)` error) cannot use the Content Publishing API
- **No shopping tags, branded content, filters, or music** via API
- **Carousels**: API max is 10 items (native app allows 20); cannot mix images and videos in same carousel
- **WebP**: Must be converted to JPEG manually before upload
