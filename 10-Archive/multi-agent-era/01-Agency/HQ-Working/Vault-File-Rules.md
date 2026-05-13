# Obsidian Vault — File Rules

Last updated: 2026-04-16

## Rule: Markdown Only in Synced Vault

The Obsidian vault (synced via Obsidian Sync) is for **markdown files and thoughts only**.

### ✅ OK in synced vault
- `.md` files (notes, analysis, plans, logs)
- Small inline images if critical to a note

### ❌ Move to Google Drive
- Audio files (.mp3, .wav, .ogg)
- Large images (.jpg, .png over 50KB)
- Documents (.docx, .pdf)
- Videos
- Generated content (AI images, TTS output)

## Files to Move Out (as of 2026-04-16)

### Audio
- `assets/voices/dmob-def-jam-vendetta.mp3` (2.9 MB)

### Images (root level)
- `IHTyuh03Sm9vTj6-Qb4PA_EgxH8a8s.jpg.png` (1.3 MB)
- `Lucid_Origin_Creating_a_vibrant_telegram_contact_photo_for_the_0.jpg` (540 KB)
- `Lucid_Origin_Create_a_stylized_telegram_logo_for_the_Content_C_2.jpg` (288 KB)
- `gemini-2.5-flash-image_*.jpg` (4 files, ~900 KB total)
- `DMob.jpg` (16 KB)
- `DMobGenTech.jpg` (187 KB)
- `gemini-image-2_*.jpg` (172 KB)

### Images (assets folder)
- `assets/branding/*.jpg` (3 files, ~520 KB total)

### Documents
- `gentech_agency_ops_v6.docx` (496 KB)
- `ai-portfolio.docx` (492 KB)

### Other in vault
- `defi-milestone-tracker.html` (28 KB)
- `sync-vault.sh` (1 KB)

## Google Drive Structure (suggested)
```
Google Drive/
└── Gentech Media/
    ├── Audio/
    ├── Images/
    │   ├── Branding/
    │   └── Generated/
    ├── Documents/
    └── TTS Output/
```

## Current vault size: 8.6 MB
## After cleanup: ~200 KB (markdown only)
