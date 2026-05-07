---
name: testing
domain: red-teaming
tags:
- testing
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for testing-* skills.
---
## Included Capabilities

### testing-handbook-generator
Meta-skill that analyzes the Trail of Bits Testing Handbook (appsec.guide) and generates Claude Code skills for security testing tools and techniques. Use when creating new skills based on handbook content.

- **Full reference:** `references/testing-handbook-generator/SKILL.md`
- **Execution scripts:** `scripts/testing-handbook-generator/`

### testing-for-business-logic-vulnerabilities
Identifying flaws in application business logic that allow price manipulation, workflow bypass, and privilege escalation beyond what technical vulnerability scanners can detect.
- **Full reference:** `references/testing-for-business-logic-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-for-business-logic-vulnerabilities/`

### testing-for-broken-access-control
Systematically testing web applications for broken access control vulnerabilities including privilege escalation, missing function-level checks, and insecure direct object references.
- **Full reference:** `references/testing-for-broken-access-control/SKILL.md`
- **Execution scripts:** `scripts/testing-for-broken-access-control/`

### testing-for-xss-vulnerabilities
Tests web applications for Cross-Site Scripting (XSS) vulnerabilities by injecting JavaScript payloads into reflected, stored, and DOM-based contexts to demonstrate client-side code execution, session hijacking, and user impersonation. The tester identifies all injection points and output contexts, crafts context-appropriate payloads, and bypasses sanitization and CSP protections. Activates for requests involving XSS testing, cross-site scripting assessment, client-side injection testing, or JavaScript injection vulnerability testing.

- **Full reference:** `references/testing-for-xss-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-for-xss-vulnerabilities/`

### testing-android-intents-for-vulnerabilities
Tests Android inter-process communication (IPC) through intents for vulnerabilities including intent injection, unauthorized component access, broadcast sniffing, pending intent hijacking, and content provider data leakage. Use when assessing Android app attack surface through exported components, testing intent-based data flows, or evaluating IPC security. Activates for requests involving Android intent security, IPC testing, exported component analysis, or Drozer assessment.

- **Full reference:** `references/testing-android-intents-for-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-android-intents-for-vulnerabilities/`

### testing-jwt-token-security
Assessing JSON Web Token implementations for cryptographic weaknesses, algorithm confusion attacks, and authorization bypass vulnerabilities during security engagements.
- **Full reference:** `references/testing-jwt-token-security/SKILL.md`
- **Execution scripts:** `scripts/testing-jwt-token-security/`

### testing-for-email-header-injection
Test web application email functionality for SMTP header injection vulnerabilities that allow attackers to inject additional email headers, modify recipients, and abuse contact forms for spam relay.
- **Full reference:** `references/testing-for-email-header-injection/SKILL.md`
- **Execution scripts:** `scripts/testing-for-email-header-injection/`

### testing-websocket-api-security
Tests WebSocket API implementations for security vulnerabilities including missing authentication on WebSocket upgrade, Cross-Site WebSocket Hijacking (CSWSH), injection attacks through WebSocket messages, insufficient input validation, denial-of-service via message flooding, and information leakage through WebSocket frames. The tester intercepts WebSocket handshakes and messages using Burp Suite, crafts malicious payloads, and tests for authorization bypass on WebSocket channels. Activates for requests involving WebSocket security testing, WS penetration testing, CSWSH attack, or real-time API security assessment.

- **Full reference:** `references/testing-websocket-api-security/SKILL.md`
- **Execution scripts:** `scripts/testing-websocket-api-security/`

### testing-api-security-with-owasp-top-10
Systematically assessing REST and GraphQL API endpoints against the OWASP API Security Top 10 risks using automated and manual testing techniques.
- **Full reference:** `references/testing-api-security-with-owasp-top-10/SKILL.md`
- **Execution scripts:** `scripts/testing-api-security-with-owasp-top-10/`

### testing-for-sensitive-data-exposure
Identifying sensitive data exposure vulnerabilities including API key leakage, PII in responses, insecure storage, and unprotected data transmission during security assessments.
- **Full reference:** `references/testing-for-sensitive-data-exposure/SKILL.md`
- **Execution scripts:** `scripts/testing-for-sensitive-data-exposure/`

### testing-ransomware-recovery-procedures
Test and validate ransomware recovery procedures including backup restore operations, RTO/RPO target verification, recovery sequencing, and clean restore validation to ensure organizational resilience against destructive ransomware attacks.
- **Full reference:** `references/testing-ransomware-recovery-procedures/SKILL.md`
- **Execution scripts:** `scripts/testing-ransomware-recovery-procedures/`

### testing-for-xml-injection-vulnerabilities
Test web applications for XML injection vulnerabilities including XXE, XPath injection, and XML entity attacks to identify data exposure and server-side request forgery risks.
- **Full reference:** `references/testing-for-xml-injection-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-for-xml-injection-vulnerabilities/`

### testing-api-authentication-weaknesses
Tests API authentication mechanisms for weaknesses including broken token validation, missing authentication on endpoints, weak password policies, credential stuffing susceptibility, token leakage in URLs or logs, and session management flaws. The tester evaluates JWT implementation, API key handling, OAuth flows, and session token entropy to identify authentication bypasses. Maps to OWASP API2:2023 Broken Authentication. Activates for requests involving API authentication testing, token validation assessment, credential security testing, or API auth bypass.

- **Full reference:** `references/testing-api-authentication-weaknesses/SKILL.md`
- **Execution scripts:** `scripts/testing-api-authentication-weaknesses/`

### testing-for-json-web-token-vulnerabilities
Test JWT implementations for critical vulnerabilities including algorithm confusion, none algorithm bypass, kid parameter injection, and weak secret exploitation to achieve authentication bypass and privilege escalation.
- **Full reference:** `references/testing-for-json-web-token-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-for-json-web-token-vulnerabilities/`

### testing-oauth2-implementation-flaws
Tests OAuth 2.0 and OpenID Connect implementations for security flaws including authorization code interception, redirect URI manipulation, CSRF in OAuth flows, token leakage, scope escalation, and PKCE bypass. The tester evaluates the authorization server, client application, and token handling for common misconfigurations that enable account takeover or unauthorized access. Activates for requests involving OAuth security testing, OIDC vulnerability assessment, OAuth2 redirect bypass, or authorization code flow testing.

- **Full reference:** `references/testing-oauth2-implementation-flaws/SKILL.md`
- **Execution scripts:** `scripts/testing-oauth2-implementation-flaws/`

### testing-for-xxe-injection-vulnerabilities
Discovering and exploiting XML External Entity injection vulnerabilities to read server files, perform SSRF, and exfiltrate data during authorized penetration tests.
- **Full reference:** `references/testing-for-xxe-injection-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-for-xxe-injection-vulnerabilities/`

### testing-for-xss-vulnerabilities-with-burpsuite
Identifying and validating cross-site scripting vulnerabilities using Burp Suite's scanner, intruder, and repeater tools during authorized security assessments.
- **Full reference:** `references/testing-for-xss-vulnerabilities-with-burpsuite/SKILL.md`
- **Execution scripts:** `scripts/testing-for-xss-vulnerabilities-with-burpsuite/`

### testing-mobile-api-authentication
Tests authentication and authorization mechanisms in mobile application APIs to identify broken authentication, insecure token management, session fixation, privilege escalation, and IDOR vulnerabilities. Use when performing API security assessments against mobile app backends, testing JWT implementations, evaluating OAuth flows, or assessing session management. Activates for requests involving mobile API auth testing, token security assessment, OAuth mobile flow testing, or API authorization bypass.

- **Full reference:** `references/testing-mobile-api-authentication/SKILL.md`
- **Execution scripts:** `scripts/testing-mobile-api-authentication/`

### testing-api-for-broken-object-level-authorization
Tests REST and GraphQL APIs for Broken Object Level Authorization (BOLA/IDOR) vulnerabilities where an authenticated user can access or modify resources belonging to other users by manipulating object identifiers in API requests. The tester intercepts API calls, identifies object ID parameters (numeric IDs, UUIDs, slugs), and systematically replaces them with IDs belonging to other users to determine if the server enforces per-object authorization. This is OWASP API Security Top 10 2023 risk API1. Activates for requests involving BOLA testing, IDOR in APIs, object-level authorization testing, or API access control bypass.

- **Full reference:** `references/testing-api-for-broken-object-level-authorization/SKILL.md`
- **Execution scripts:** `scripts/testing-api-for-broken-object-level-authorization/`

### testing-api-for-mass-assignment-vulnerability
Tests APIs for mass assignment (auto-binding) vulnerabilities where clients can modify object properties they should not have access to by including additional parameters in API requests. The tester identifies writable endpoints, adds undocumented fields to request bodies (role, isAdmin, price, balance), and checks if the server binds these to the data model without filtering. Part of OWASP API3:2023 Broken Object Property Level Authorization. Activates for requests involving mass assignment testing, parameter binding abuse, auto-binding vulnerability, or API over-posting.

- **Full reference:** `references/testing-api-for-mass-assignment-vulnerability/SKILL.md`
- **Execution scripts:** `scripts/testing-api-for-mass-assignment-vulnerability/`

### testing-cors-misconfiguration
Identifying and exploiting Cross-Origin Resource Sharing misconfigurations that allow unauthorized cross-domain data access and credential theft during security assessments.
- **Full reference:** `references/testing-cors-misconfiguration/SKILL.md`
- **Execution scripts:** `scripts/testing-cors-misconfiguration/`

### testing-for-open-redirect-vulnerabilities
Identify and test open redirect vulnerabilities in web applications by analyzing URL redirection parameters, bypass techniques, and exploitation chains for phishing and token theft.
- **Full reference:** `references/testing-for-open-redirect-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/testing-for-open-redirect-vulnerabilities/`

### testing-for-host-header-injection
Test web applications for HTTP Host header injection vulnerabilities to identify password reset poisoning, web cache poisoning, SSRF, and virtual host routing manipulation risks.
- **Full reference:** `references/testing-for-host-header-injection/SKILL.md`
- **Execution scripts:** `scripts/testing-for-host-header-injection/`