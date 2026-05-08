---
name: reverse
domain: red-teaming
tags:
- reverse
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for reverse-* skills.
---
## Included Capabilities

### reverse-engineering-ios-app-with-frida
Reverse engineers iOS applications using Frida dynamic instrumentation to understand internal logic, extract encryption keys, bypass security controls, and discover hidden functionality without source code access. Use when performing authorized iOS penetration testing, analyzing proprietary protocols, understanding obfuscated logic, or extracting runtime secrets from iOS binaries. Activates for requests involving iOS reverse engineering, Frida iOS hooking, Objective-C/Swift method tracing, or iOS binary analysis.

- **Full reference:** `references/reverse-engineering-ios-app-with-frida/SKILL.md`
- **Execution scripts:** `scripts/reverse-engineering-ios-app-with-frida/`

### reverse-engineering-android-malware-with-jadx
Reverse engineers malicious Android APK files using JADX decompiler to analyze Java/Kotlin source code, identify malicious functionality including data theft, C2 communication, privilege escalation, and overlay attacks. Examines manifest permissions, receivers, services, and native libraries. Activates for requests involving Android malware analysis, APK reverse engineering, mobile malware investigation, or Android threat analysis.

- **Full reference:** `references/reverse-engineering-android-malware-with-jadx/SKILL.md`
- **Execution scripts:** `scripts/reverse-engineering-android-malware-with-jadx/`

### reverse-engineering-malware-with-ghidra
Reverse engineers malware binaries using NSA's Ghidra disassembler and decompiler to understand internal logic, cryptographic routines, C2 protocols, and evasion techniques at the assembly and pseudo-C level. Activates for requests involving malware reverse engineering, disassembly analysis, decompilation, binary analysis, or understanding malware internals.

- **Full reference:** `references/reverse-engineering-malware-with-ghidra/SKILL.md`
- **Execution scripts:** `scripts/reverse-engineering-malware-with-ghidra/`

### reverse-engineering-rust-malware
Reverse engineer Rust-compiled malware using IDA Pro and Ghidra with techniques for handling non-null-terminated strings, crate dependency extraction, and Rust-specific control flow analysis.
- **Full reference:** `references/reverse-engineering-rust-malware/SKILL.md`
- **Execution scripts:** `scripts/reverse-engineering-rust-malware/`

### reverse-engineering-dotnet-malware-with-dnspy
Reverse engineers .NET malware using dnSpy decompiler and debugger to analyze C#/VB.NET source code, identify obfuscation techniques, extract configurations, and understand malicious functionality including stealers, RATs, and loaders. Activates for requests involving .NET malware analysis, C# malware decompilation, managed code reverse engineering, or .NET obfuscation analysis.

- **Full reference:** `references/reverse-engineering-dotnet-malware-with-dnspy/SKILL.md`
- **Execution scripts:** `scripts/reverse-engineering-dotnet-malware-with-dnspy/`

### reverse-engineering-ransomware-encryption-routine
Reverse engineer ransomware encryption routines to identify cryptographic algorithms, key generation flaws, and potential decryption opportunities using static and dynamic analysis.
- **Full reference:** `references/reverse-engineering-ransomware-encryption-routine/SKILL.md`
- **Execution scripts:** `scripts/reverse-engineering-ransomware-encryption-routine/`