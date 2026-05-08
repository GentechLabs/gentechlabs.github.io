---
name: frontend-modification
title: Frontend Modification with Embedded JavaScript
description: Skill for safely modifying HTML files with embedded JavaScript, particularly when dealing with complex data structures or escaping issues. Provides workarounds for common pitfalls when using the patch tool with HTML/JS files.
---
# Frontend Modification Skill

## Overview
Skill for safely modifying HTML files with embedded JavaScript, particularly when dealing with complex data structures or escaping issues. This skill provides workarounds for common pitfalls when using the `patch` tool with HTML/JS files.

## When to Use
- Modifying HTML files that contain inline JavaScript
- Inserting JSON data into script tags
- Working around `patch` tool escape-drift issues
- Breaking down complex file modifications into manageable steps

## Steps

### 1. Assess the File Structure
Before making changes, read the entire HTML file to understand:
- The overall structure and sections
- Where you need to insert content
- Existing script blocks and their locations

### 2. Use Python for Complex Modifications
When the `patch` tool fails due to escape-drift or complex string matching, use Python's file manipulation capabilities:

```python
# Read the file
with open('file.html', 'r') as f:
    content = f.read()

# Make modifications
# ... your logic here ...

# Write back
with open('file.html', 'w') as f:
    f.write(modified_content)
```

### 3. Break Down Large Insertions
For large JavaScript blocks with embedded data:
- Insert the HTML structure first (without the script content)
- Then add the script content separately
- Use clear markers to identify insertion points

### 4. Handle JSON Data in Scripts
When embedding JSON data in a script tag:
- Load the JSON data from a file or generate it
- Convert to a compact string representation
- Escape quotes properly if needed
- Insert as a raw string in the script template

### 5. Verify Changes
After modification:
- Read back the file to ensure content is correct
- Check for syntax errors in JavaScript
- Test that the page still renders properly

## Pitfalls
- **Escape-drift**: The `patch` tool may fail if the old_string contains backslashes that aren't in the file. Use Python for complex cases.
- **Partial views**: When using pagination with `read_file`, you might not get the full context. Read the entire file for critical modifications.
- **Overwriting**: Be careful not to overwrite entire sections unintentionally. Use precise insertion points.
- **CSS specificity battles**: When a style fix doesn't take effect, check `document.styleSheets` in browser console to see which rule is actually applied. Look for duplicate selectors across multiple `<style>` blocks — later blocks win. Use `getComputedStyle(el)` to verify the actual rendered value vs what the file says.
- **Browser CSS caching**: After pushing CSS changes to GitHub Pages, the live site may serve stale CSS. Force a fresh load with a cache-buster (`?v=2`) or verify via `browser_console` querying `getComputedStyle()`. Don't trust the first visual check after deployment.
- **Git index staleness**: After using the `patch` tool, `git status` may not show changes even though the file was modified. Run `git update-index --refresh` before staging. Symptoms: `diff` shows no changes, `md5sum` differs between working copy and `git show HEAD:path`.
- **Multiple `<style>` blocks**: HTML files often accumulate inline `<style>` tags in different sections. Rules in later blocks override earlier ones for same-specificity selectors. When a CSS fix doesn't apply, search ALL style blocks for conflicting rules — `grep -n 'selector' file.html` across the full file.

## Verification Steps (Critical)
After any CSS/visual change to a deployed site:
1. **Check computed styles in browser** — don't trust the file alone:
   ```javascript
   const el = document.querySelector('.target-class');
   const cs = window.getComputedStyle(el);
   console.log({ color: cs.color, fontWeight: cs.fontWeight, whiteSpace: cs.whiteSpace });
   ```
2. **Verify the CSS rule exists in stylesheets**:
   ```javascript
   for (const sheet of document.styleSheets) {
     for (const rule of sheet.cssRules) {
       if (rule.selectorText?.includes('target')) console.log(rule.cssText);
     }
   }
   ```
3. **Visual check via `browser_vision`** — screenshot confirms layout, wrapping, overlap
4. **Force fresh load** if first check looks stale — add `?v=N` to URL

## Example Workflow
1. Read the HTML file completely
2. Identify the insertion point (e.g., before a specific section)
3. Create the new HTML content as a string
4. Insert the HTML structure
5. Create the JavaScript with embedded JSON
6. Insert the script tag
7. Write the modified file
8. Verify the changes in-file (grep for the change)
9. Deploy (git push)
10. Verify on live site via browser_console + browser_vision

## Tools Used
- `execute_code` with Python for file manipulation
- `read_file` for inspecting file content
- `patch` for simple text replacements
- `search_files` for finding specific patterns

## References
- `references/portfolio-deployment-workflow.md` — Portfolio site deployment pipeline, CSS class reference, and gotchas

## Related Skills
- `gentech-project-coordination`: For overall project coordination
- `html-embedding`: For embedding data in HTML
- `javascript-integration`: For integrating JavaScript with web pages