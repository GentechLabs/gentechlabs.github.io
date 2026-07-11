# BlockRun Spend Log

> Track wallet balance and per-request costs. Update after every paid tool call.

## Wallet
**Address:** `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` (Base)
**Explorer:** https://basescan.org/address/0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8

## Balance History

| Date | Balance | Change | What For |
|------|---------|--------|----------|
| 2026-07-09 | $6.10 | — | Starting balance |
| 2026-07-09 | $5.05 | -$1.05 | Image gen, speech, search calls |
| 2026-07-09 | $5.05 | $0.00 | Steve Harvey TTS (via ElevenLabs API key, not BlockRun) |
| 2026-07-09 | $5.02 | -$0.03 | CogView-4: DbD killer concept "The Rayban Runner" |
| 2026-07-09 | $4.96 | -$0.06 | GPT Image 2: DbD killer "The Rayban Runner" v2 |
| 2026-07-09 | $4.95 | -$0.015 | CogView-4: Dead as Disco "The Rayban Runner" arcade |
| 2026-07-10 | $5.05 | +? | (pending next check) |

## Cost Reference Guide

| Tool | Cost | Notes |
|------|------|-------|
| DefiLlama (any path) | $0.001–0.005 | Protocol data, yields, prices |
| DexScreener | **FREE** | DEX pairs, token prices |
| Exa Search | $0.01/call | Neural web search |
| Exa Contents | $0.002/URL | Fetch page content |
| BlockRun Chat (GLM-5) | $0.001/call | Audit/second opinion |
| BlockRun Chat (smart route) | varies | ClawRouter auto-select |
| Image Gen (CogView-4) | **$0.015** | Cheap, good for drafts |
| Image Gen (GPT Image 2) | $0.06–0.12 | Best quality, text rendering |
| Image Gen (Nano Banana) | $0.05 | Gemini-family |
| Image Gen (Grok Imagine) | $0.02 | Fast, stylized |
| Speech (ElevenLabs via BR) | $0.05/1k chars | Via BlockRun gateway |
| **Speech (ElevenLabs direct)** | **~~$0~~** | Using our own API key — free! |
| Music (MiniMax) | $0.1575/track | Full ~3min track |
| Video (Grok Imagine) | $0.05/sec | 1–15s clips |
| Video (Seedance 1.5 Pro) | ~$0.092/sec | 720p, audio sync |
| Video (Seedance 2.0 Fast) | ~$0.238/sec | Higher quality |
| Sound Effects | $0.0525/clip | ElevenLabs SFX |

## Pro Tips
- **Use ElevenLabs direct API** (our key) for speech — $0 on BlockRun
- **DexScreener** is completely free for token lookups
- **CogView-4** at $0.015 is best value image model
- **Exa search** capped at $0.025 per result source
