---
name: Autonomous Web Research
version: 1.0
author: Gentech AI
class: research
description: Strategies for conducting web research when standard search tools are unavailable, covering browser navigation, content extraction, and overcoming bot detection.
---

# Autonomous Web Research

## Overview
Strategies for conducting comprehensive web research when standard web search tools are unavailable or limited. This skill covers techniques for extracting information from websites that employ bot detection, require authentication, or have dynamic content that's difficult to scrape.

## When to Use
- Web search tools (e.g., Firecrawl) are not configured or require API keys
- Websites employ aggressive bot detection (reCAPTCHA, Cloudflare)
- Dynamic content requires JavaScript execution
- Authentication is required to access information

## Workflow

### 1. Direct Navigation to Official Sources
Start with official sources (company blogs, documentation, official announcements) as they are most reliable.

**Technique**: Use browser navigation to access official websites directly rather than relying on search engines.

### 2. Content Extraction via Browser Snapshots
When dynamic content prevents easy scraping, use browser snapshots to capture page content.

**Technique**: 
- Navigate to the target page
- Use `browser_snapshot` to capture full page content
- Parse the snapshot for relevant information
- Scroll down to load more content if needed

### 3. Direct URL Access for Specific Content
If you know the specific content you need, try to construct the direct URL.

**Technique**:
- From the blog or documentation index, identify patterns in URLs
- Navigate directly to the content page
- Use `browser_click` to interact with elements if needed

### 4. Terminal-Based Content Retrieval
For documentation and content-rich sites, use terminal commands to fetch content directly.

**Technique**:
- Use `curl` to download HTML pages
- Use `curl` to access static content files (e.g., documentation index files)
- Parse the downloaded content for relevant information

### 5. Search Within Sites
When direct access is blocked, use site-specific search if available.

**Technique**:
- Locate search functionality on the site
- Use `browser_type` and `browser_press` to submit search queries
- Extract results from the search results page

### 6. Handling Bot Detection
When encountering bot detection challenges:

**Techniques**:
- Accept cookies when prompted
- Use browser navigation with delays between actions
- Try accessing different pages first to establish a browsing pattern
- If detection persists, switch to alternative sources

### 7. Information Synthesis
Combine information from multiple sources to build a comprehensive picture.

**Technique**:
- Cross-reference information from official blogs, documentation, and third-party sources
- Look for patterns and confirmations across sources
- Document findings systematically

## Pitfalls
- **Don't rely solely on search engines** when tools are unavailable - they often lead to bot detection
- **Don't give up** when encountering access restrictions - try alternative approaches
- **Do verify information** from multiple sources when possible
- **Do document your methodology** so it can be replicated in future sessions

## Tools Used
- browser_navigate
- browser_click
- browser_type
- browser_press
- browser_scroll
- browser_snapshot
- terminal (curl)

## References
This skill was developed during a LayerZero DVN security monitor check where web search tools were unavailable, requiring creative approaches to gather information from official sources while avoiding bot detection.