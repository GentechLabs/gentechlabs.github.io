# 🧠 Weekly Brain Review — 2026-04-19

## Inventory Summary

| Metric | Value |
|--------|-------|
| Total skills loaded | 123 |
| Categories | 18 |
| User-installed dirs (top-level) | 74 |
| User-installed skills (subdirs) | 166 |
| Skills with git tracking | 0 |
| Built-in skills (bundled) | ~82 (per manifest) |

## New This Week

**First brain review.** No previous week to compare against. This is the baseline.

## Update Check Results

**No updates found.** None of the 123 user-installed skills have `.git` directories — they were installed by copying files, not cloning repositories. Without git tracking, there is no mechanism to check for upstream updates.

### Skills by Category

| Category | Count | Notes |
|----------|-------|-------|
| autonomous-ai-agents | 4 | claude-code, codex, hermes-agent, opencode |
| creative | 9 | ascii-art, ascii-video, baoyu-infographic, excalidraw, ideation, manim-video, p5js, popular-web-designs, songwriting |
| data-science | 1 | jupyter-live-kernel |
| devops | 13 | aae-agent-reference, aae-staking-reference, cron-jobs-reference, department-routing-protocol, elevenlabs voices (3), gentech-group-routing, hermes-skin-creation, tts-voice-assignments, vault-context-loader, voicebox-backup-tts, watchdog-troubleshooting, webhook-subscriptions |
| email | 1 | himalaya |
| gaming | 2 | minecraft-modpack-server, pokemon-player |
| github | 7 | codebase-inspection, github-auth, github-code-review, github-issues, github-pr-workflow, github-repo-data-analysis, github-repo-management |
| leisure | 1 | find-nearby |
| mcp | 2 | mcporter, native-mcp |
| media | 7 | gif-search, heartmula, hf-tts, hf-tts-voice-generation, kokoro-tts, songsee, youtube-content |
| mlops | 21 | audiocraft, axolotl, clip, dspy, evaluating-llms-harness, fine-tuning-with-trl, gguf-quantization, grpo-rl-training, guidance, huggingface-hub, llama-cpp, modal-serverless-gpu, obliteratus, outlines, peft-fine-tuning, pytorch-fsdp, segment-anything, serving-llms-vllm, stable-diffusion, unsloth, weights-and-biases, whisper |
| note-taking | 1 | obsidian |
| productivity | 11 | end-of-shift-wrapup, google-workspace, hackathon-content-deliverables, hackathon-tracker-structure, linear, nano-pdf, notion, ocr-and-documents, powerpoint, skills-audit |
| red-teaming | 1 | godmode |
| research | 10 | arxiv, blogwatcher, coinmarketcap-data-extraction, crypto-monitor-browser, lfj-contract-lookup, lfj-trader-joe-contracts, llm-wiki, polymarket, research-paper-writing |
| smart-home | 1 | openhue |
| social-media | 5 | content-extraction-pipeline, twitter-extract-fallback, x-content-strategy, xitter, xurl |
| software-development | 7 | agentforge-hackathon-build, foundry-testing-patterns, plan, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, writing-plans |
| Uncategorized | 17 | agent-catchup-digest, blockchain-ecosentry-scout, browser-harness, channel-agent-setup, cron-pitfalls, crypto-watchlist-report, dogfood, elevenhacks-tracking, git-history-rewrite, green-room-coordination, hackathon-reuse-strategy, lp-position-rebalance, memory-consolidation, nous-token-troubleshoot, project-board-assembly, research-js-rendered-sites, sdk-evaluation-framework |

## Git Tracking Audit

**0 out of 240 user-installed skill directories have `.git` directories.** This means:

- No automatic update checking is possible
- Skills installed from GitHub repos were copied, not cloned
- There is no record of the source repository for most skills
- Update checking requires manual comparison against original repos

### Recommendation

For skills installed from GitHub repos, consider re-installing via `git clone` instead of copying files. This would enable:
1. Automatic update detection (`git fetch` + `git log HEAD..origin/main`)
2. Easy rollback to previous versions
3. Clear provenance tracking

## Recommendations

1. **Pull:** N/A — no updates available
2. **Ignore:** N/A — no new commits
3. **Remove:** Consider auditing the 17 uncategorized skills and the large mlops category (21 skills) for relevance to Gentech's actual work. Many mlops skills (pytorch-fsdp, segment-anything-model, stable-diffusion) are general ML tools that may not be actively used.
