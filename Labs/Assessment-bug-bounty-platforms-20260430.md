---
title: "Codebase Assessment — Disclose Bug Bounty Platforms"
date: 2026-04-30
type: assessment
tags: [bug-bounty, security, web3, defi, audit, crowdsourced-security]
status: ready
---

# Codebase Assessment: Bug Bounty Platforms (Disclose)
**Repo:** [https://github.com/disclose/bug-bounty-platforms](https://github.com/disclose/bug-bounty-platforms)
**License:** MIT | **Stars:** 1.2K | **Language:** Markdown, YAML

## Overview
This is a **community-maintained, open-source directory** of bug bounty and vulnerability disclosure platforms (VDPs) worldwide. It provides a **structured table** of platforms, their regions, program types, leaderboard availability, and direct links to public programs. The repository is **static** (Jekyll-based) and designed for easy contribution via GitHub PRs.

## Codebase Metrics
| Metric               | Value                          |
|---------------------|--------------------------------|
| Files               | 5                              |
| Directories         | 1 (_layouts)                   |
| Lines of Content    | ~107 (README.md table)         |
| Language            | Markdown, YAML (Jekyll config) |
| Comment Ratio       | N/A (static content)           |

## Architecture
```
.
├── _config.yml       # Jekyll configuration
├── _layouts/         # HTML templates for rendering
│   └── default.html  # Main layout template
├── CNAME             # Custom domain config
├── LICENSE           # MIT License
└── README.md         # Primary content (platform table)
```

- **Static Site Generator**: Jekyll (GitHub Pages compatible)
- **Primary Content**: `README.md` (contains the bug bounty platform table)
- **Layout**: Single HTML template (`default.html`) for rendering
- **Deployment**: Auto-deployed via GitHub Pages

## How It Works
1. **Data Source**: The `README.md` file contains a **Markdown table** with 100+ bug bounty platforms, updated via community contributions.
2. **Rendering**: GitHub Pages uses Jekyll to render the table into a static HTML page.
3. **Contribution**: Users submit updates via GitHub PRs (directly editable via the "Improve this page" link).
4. **Hosting**: Served via GitHub Pages (no backend, no database).

## Dependencies
- **Jekyll**: Static site generation (GitHub Pages default)
- **GitHub Pages**: Hosting and auto-deployment
- **No API Keys Required**: Purely static content

## Setup Requirements
```bash
# No installation required for local use
# To contribute: Fork, edit README.md, submit PR

# For local Jekyll preview (optional)
gem install bundler jekyll
bundle install
bundle exec jekyll serve
```

## Functional Testing ✅
| Test                     | Result |
|--------------------------|--------|
| GitHub Pages Rendering   | ✅     |
| Table Formatting         | ✅     |
| Links Validation         | ✅     |
| PR Submission Workflow   | ✅     |

- **Installation**: Not applicable (static site).
- **Test Suite**: None (no dynamic functionality).
- **Core Operations**: Table renders correctly, all links verified.
- **Integration**: GitHub Pages deploys automatically on merge.

### Bugs Found
- **None**: The repository is **fully functional** as a static directory. No dynamic components to fail.

## Strengths ✅
- **Comprehensive**: Covers 100+ platforms (global, including Web3/DeFi-focused like Immunefi, Cantina, Sherlock).
- **Up-to-Date**: Community-driven updates ensure freshness.
- **Low Friction**: No setup, no dependencies, no API keys.
- **MIT Licensed**: Free to use, modify, and integrate.
- **GitHub Native**: Easy for security researchers to contribute.
- **Structured Data**: Leaderboard/public program links are standardized.

## Concerns / Questions ⚠️
- **No Web3 Filter**: Platforms like **Cantina, Sherlock, Code4rena, Immunefi** are mixed with traditional bug bounty platforms. No easy way to filter for **smart contract/DeFi-focused** programs.
- **No API**: Data is only available as a Markdown table (not JSON/CSV).
- **No Automation**: Updates require manual PRs (no web scraping or auto-sync with platforms).
- **No Program Details**: Only basic info (name, URL, region, leaderboard). No payout stats, scope, or rules.

## Fit Assessment
**Rating: ⭐⭐⭐⭐ (4/5)**
- **Why It Fits**: This is the **most comprehensive open-source directory** of bug bounty platforms, including Web3/DeFi-focused ones. It’s a **critical resource** for security researchers and auditors.
- **Why Not 5/5**: Lacks **Web3-specific filtering** and **programmatic access** (API/JSON).

## Potential Use Cases
1. **Opportunity Scanner**: Integrate with **Gentech’s audit pipeline** to auto-suggest relevant bug bounty programs (e.g., filter for Web3 platforms with leaderboards).
2. **Research Dashboard**: Build a **Web3-focused fork** that highlights DeFi/smart contract platforms (Immunefi, Cantina, Sherlock, Code4rena).
3. **Contribution Hub**: Use as a **community contribution point** for Gentech’s security researchers to add new platforms.
4. **Data Source**: Scrape/parse the table into **JSON/CSV** for use in other tools (e.g., `hermes` opportunity tracker).

## Next Steps
1. **Fork & Enhance**: Create a **Web3-focused version** with filters for smart contract/DeFi platforms.
2. **Automate Data Extraction**: Write a script to parse the table into **JSON/CSV** for programmatic use.
3. **Integrate with Hermes**: Add a **bug bounty opportunity scanner** that filters this list for Web3 platforms with active leaderboards.
4. **Community Engagement**: Encourage Gentech researchers to contribute new platforms via PRs.

## Web3/DeFi Platforms Highlight
| Platform      | URL                          | Program Type       | Leaderboard | Public Programs |
|--------------|------------------------------|--------------------|-------------|-----------------|
| **Cantina**  | [https://cantina.xyz](https://cantina.xyz) | Private + Public | Yes         | [Link](https://cantina.xyz/competitions) |
| **Sherlock** | [https://sherlock.xyz](https://sherlock.xyz) | Public           | Yes         | [Link](https://app.sherlock.xyz/audits/contests) |
| **Code4rena**| [https://code4rena.com](https://code4rena.com) | Public           | Yes         | [Link](https://code4rena.com/contests) |
| **Immunefi** | [https://immunefi.com](https://immunefi.com) | Public           | Yes         | [Link](https://immunefi.com/explore/) |
| **Hats**     | [https://hats.finance](https://hats.finance) | Public           | Yes         | N/A |
| **CodeHawks**| [https://codehawks.cyfrin.io](https://codehawks.cyfrin.io) | Private + Public | Yes         | N/A |
| **Secure3**  | [https://secure3.io](https://secure3.io) | Private + Public | N/A         | N/A |

---