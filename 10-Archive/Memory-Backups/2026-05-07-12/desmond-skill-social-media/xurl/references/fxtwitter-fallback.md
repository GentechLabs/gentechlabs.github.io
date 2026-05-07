# fxtwitter API — Fallback for Tweet Reading

When `xurl` isn't authenticated (401) or unavailable, the fxtwitter API provides read-only access to tweets.

## Base URL
```
https://api.fxtwitter.com/{SCREEN_NAME}/status/{POST_ID}
```

## Quick Usage
```bash
# Read a tweet
curl -s "https://api.fxtwitter.com/elonmusk/status/1234567890" | python3 -m json.tool

# Extract key fields
curl -s "https://api.fxtwitter.com/user/status/ID" | python3 -c "
import json,sys
d=json.load(sys.stdin)
t=d.get('tweet',{})
print('Author:', t.get('author',{}).get('name'))
print('Text:', t.get('text',''))
print('Likes:', t.get('likes',0))
"
```

## Resolve t.co URLs
```bash
curl -s -L -o /dev/null -w "%{url_effective}" "https://t.co/SHORT_URL"
```

## Limitations
- **Cannot read X Articles** — requires login, returns 404
- **No search** — fxtwitter search endpoint exists but often times out
- **Rate limits** — not documented; use sparingly
- **No write access** — read-only
- **Empty text** — some tweets (link-only, card tweets) return empty `text` field; check `raw_text.text` or `twitter_card` fields

## Fields Available
- `tweet.text` / `tweet.raw_text.text` — tweet content
- `tweet.author.name` / `.screen_name` — author info
- `tweet.likes` / `.retweets` / `.quotes` / `.views` — engagement
- `tweet.created_at` — timestamp
- `tweet.media.photos[]` / `.videos[]` — media URLs
- `tweet.card` — embedded link card (title, description, url)
- `tweet.quote` — quoted tweet (nested tweet object)
