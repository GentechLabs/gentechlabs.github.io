# Contributing to x402 Payment Security YARA Rules

## How to Contribute

1. **Fork the repository** and create a feature branch.
2. **Add or modify YARA rules** in the root directory (`.yar` files).
3. **Follow the rule format**:
   - Use descriptive rule names with `x402_<category>_<descriptor>` pattern
   - Include complete `meta:` block with description, category, severity, confidence, and reference
   - Use appropriate severity: CRITICAL, HIGH, or MEDIUM
   - Set confidence between 0.0 and 1.0
4. **Add test cases** in the `tests/` directory.
5. **Update README.md** if adding new categories.
6. **Submit a pull request** with a clear description of the vulnerability pattern.

## Rule Quality Guidelines

- **Minimize false positives:** Use specific, multi-condition rules where possible
- **Document references:** Every rule must cite its source (academic paper, CVE, security advisory)
- **Test coverage:** Include both positive (should match) and negative (should not match) test cases
- **Consistent severity:** CRITICAL = direct financial loss, HIGH = significant security bypass, MEDIUM = hardening/practice issue

## Code of Conduct

Be respectful, constructive, and focused on improving AI agent payment security.
