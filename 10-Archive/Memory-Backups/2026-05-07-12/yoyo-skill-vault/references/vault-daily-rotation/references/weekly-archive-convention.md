# Weekly Archive Naming Convention

When archiving weekly folders from the Mess Hall, use this convention:

## Structure
```
10-Archive/
└── Mess Hall/
    └── YYYY-MM/
        └── W##/
            ├── 2026-MM-DD/
            │   ├── today-context.md
            │   ├── mid-shift-coordination-report.md
│   │   └── ...
            ├── 2026-MM-DD/
            └── ...
```

## Rules
1. **Month selection**: Archive to the month containing the week's start date
   - W19 (May 5-9, 2026) → `10-Archive/Mess Hall/2026-05/`
   - W16 (Apr 14-20, 2026) → `10-Archive/Mess Hall/2026-04/`

2. **Week numbering**: Use the original W## folder name
   - W16, W17, W18, W19, etc.

3. **Daily subfolders**: Preserve the daily structure inside each weekly folder
   - Each day's context files remain in their own subfolder

4. **Current week**: Never archive the current week until it's complete
   - Only archive full or partial weeks that are definitively in the past

## Examples
- Archive W16 (Apr 14-20) → `10-Archive/Mess Hall/2026-04/W16/`
- Archive W17 (Apr 21-27) → `10-Archive/Mess Hall/2026-04/W17/`
- Archive W18 (Apr 28-May 4) → `10-Archive/Mess Hall/2026-05/W18/`

## Why This Pattern?
- **Consistency**: Matches the live vault structure, making retrieval intuitive
- **Monthly grouping**: Keeps related weeks together by month
- **Easy retrieval**: Find any week by year-month and week number
- **Scalable**: Works for any number of weeks without cluttering the archive root