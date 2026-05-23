# Roast Battle Scripts — Multi-Voice Social Clips

**Created:** May 23, 2026
**Format:** Multi-voice roast battles for social content (IG Reels, TikTok, YouTube Shorts)
**Voices:** Optimus Prime vs Vanito, Steve Harvey vs Uncle Iroh

## Battle 1: Optimus vs Vanito — "Who Has It Worse?"

**Style:** Trash-talk battle, competitive but friendly
**Duration:** ~30 seconds
**Voice switching:** Each line = different voice

```
[OPTIMUS]
I lead a team of autonomous agents across three blockchains.
Meanwhile, Vanito's out here losing to greyhounds in POE2.

[VANITO]
At least my agents don't need PTO and a mental health day.
Your Optimus Prime voice costs eleven cents a minute.
That's more than your portfolio.

[OPTIMUS]
I have 75 tests passing across three GenLayer contracts.
You have 75 losses in ranked matches.

[VANITO]
And yet I'm still here. Still grinding. Still alive.
That's more than your mainnet deployment can say.

[OPTIMUS]
...Fair enough.
```

**Punchline:** Optimus admits defeat — unexpected humility from an authority figure

---

## Battle 2: Steve Harvey vs Uncle Iroh — "Motivational Off"

**Style:** Coaching styles clash — hustle vs zen
**Duration:** ~25 seconds
**Voice switching:** Each line = different voice

```
[STEVE HARVEY]
Listen here. You want success? You gotta WAKE UP EARLY.
You gotta GRIND. You gotta want it more than you want to sleep.

[IROH]
Or... you could drink some tea, reflect on what matters,
and let success come to you naturally.

[STEVE HARVEY]
That's TERRIBLE advice! You can't just SIT THERE drinking TEA!

[IROH]
I have achieved inner peace, financial freedom, and a
very nice tea collection. What have you achieved?

[STEVE HARVEY]
I... okay, that's actually pretty good.
```

**Punchline:** Steve concedes — Iroh's wisdom wins

---

## Battle 3: Optimus vs Steve Harvey — "Who's the Better Leader?"

**Style:** Leadership styles clash — military vs motivational
**Duration:** ~30 seconds

```
[OPTIMUS]
I have led the Autobots through millions of years of war.
Strategic precision. Calculated risk. Zero hesitation.

[STEVE HARVEY]
I hosted Family Feud for fifteen years. You know what that takes?
Reading people. Timing. And dealing with families who think
"udders" is an acceptable answer to anything.

[OPTIMUS]
War is more complex than a game show.

[STEVE HARVEY]
Is it? Because I've seen families fall apart over $200.
You ain't never seen REAL conflict until you've asked
"Name something you'd find in a bathroom" and gotten "freedom."

[OPTIMUS]
...I yield.

[STEVE HARVEY]
That's what I THOUGHT.
```

**Punchline:** Steve's real-world experience beats Optimus's theoretical leadership

---

## Battle 4: Vanito vs Uncle Iroh — "Street Smarts vs Wisdom"

**Style:** Young energy vs old wisdom
**Duration:** ~25 seconds

```
[VANITO]
I'm out here every day grinding. Posting. Building.
I don't have time for tea and meditation.

[IROH]
The tea is not the point. The point is knowing WHEN to act
and when to wait. A fisherman who casts his net in a storm
catches nothing but trouble.

[VANITO]
Okay but what if the fish are only there during the storm?

[IROH]
Then you have already learned the lesson.
I am proud of you, young one.

[VANITO]
Wait, was that a compliment?

[IROH]
Don't get used to it.
```

**Punchline:** Iroh turns the roast into mentorship

---

## Battle 5: Three-Way Battle — "Who's the GOAT?"

**Style:** Free-for-all chaos
**Duration:** ~35 seconds

```
[STEVE HARVEY]
Let me tell y'all something. I started with nothing.
Slept in my car. Now I'm on TV. That's the American dream.

[OPTIMUS]
I was rebuilt after being destroyed by Megatron. Twice.
Your car story is cute.

[VANITO]
Y'all both old. I'm out here with the new generation.
We don't even watch TV. We ARE the content.

[STEVE HARVEY]
Boy, sit down. You haven't even finished your first album.

[OPTIMUS]
Agreed. Though I respect the ambition.

[VANITO]
At least I don't charge eleven cents a minute to talk.

[OPTIMUS]
...That was unnecessary.

[STEVE HARVEY]
No, that was FUNNY. I'll give him that one.
```

---

## Production Notes

**Audio generation:** Each [VOICE] tag = separate ElevenLabs API call, then concat with ffmpeg
**Post-processing:** Denoise + compress + normalize each clip
**Captions:** Required — 80% of social video watched on mute
**Length:** 25-35 seconds max per battle
**Posting schedule:** 1 battle per day = 5 days of content

## Voice IDs
- Optimus Prime: `xQbwtCgzouB5QdCSd0Z7`
- Steve Harvey: `Rxk9LQxvNFEplpjjsjuN`
- Uncle Iroh: `TkEJnN27nf5BsX1xwrLB`
- Vanito: `eMQtaKLvw87ksRqmQVpS`

## Voice Settings
- Optimus: stability 0.75, similarity 0.90, speed 0.88
- Steve Harvey: stability 0.55, similarity 0.82, speed 0.92
- Uncle Iroh: stability 0.70, similarity 0.88, speed 0.85
- Vanito: stability 0.60, similarity 0.85, speed 0.95
