# Unity CLI Integration — Agent-Native Game Dev Pipeline

> Unity CLI (released Jul 20, 2026) lets agents install Unity editors, manage projects,
> drive a running Editor, and execute live C# — all from the terminal. No UI needed.
>
> This skill integrates Unity CLI as a first-class agent tool in GenTech's pipeline.

## What

Unity CLI (`unity` binary) + Pipeline package (`com.unity.pipeline`) + eval = a full agent-native game development environment. An agent can:

1. **Install** Unity editors and modules from the terminal
2. **Create and open** projects
3. **Drive a running Editor** — trigger imports, run tests, execute commands
4. **Run live C#** — inspect and modify a running project with no recompile
5. **Target a live Player** — debug a running build, pull logs, hot-reload

## Quick Install

```bash
# Windows (PowerShell)
$env:UNITY_CLI_CHANNEL='beta'
irm https://public-cdn.cloud.unity3d.com/hub/prod/cli/install.ps1 | iex

# macOS / Linux
curl -fsSL https://public-cdn.cloud.unity3d.com/hub/prod/cli/install.sh | UNITY_CLI_CHANNEL=beta bash

# Verify
unity --help
```

## Agent Workflows

### 1. Editor Management

```bash
# Install an editor with modules
unity install 6000.2.10f1 -m android ios webgl --accept-eula --yes

# List installed editors
unity editors --format json

# Install modules for a specific version
unity modules list 6000.2.10f1
```

### 2. Project Operations

```bash
# Open a project (resolves the right editor)
unity open path/to/project

# Add Pipeline package to a project
unity pipeline install --project path/to/project

# List projects with Pipeline installed
unity pipeline list
```

### 3. Driving a Running Editor

```bash
# List available commands on a connected Editor
unity command

# Run a command
unity command greet --name World

# Execute live C# (no recompile!)
unity command eval "return Application.version;"
unity command eval "return UnityEditor.EditorApplication.isPlaying;" --json
unity command eval_file path/to/script.cs

# Target a running Player build instead of Editor
unity command --runtime MyGame.exe eval "return Time.time;"
```

### 4. Adding Custom Agent Commands

Add `[CliCommand]` attributes to any static method in your project:

```csharp
using Unity.Pipeline.Commands;
using UnityEngine;

public static class AgentCommands
{
    [CliCommand("scan-scene", "Scan scene for null references")]
    public static int ScanScene(
        [CliArg("verbose", "Print details")]
        bool verbose = false)
    {
        var count = 0;
        foreach (var obj in Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))
        {
            if (obj == null) count++;
            else if (verbose) Debug.Log($"  {obj.name}");
        }
        return count;
    }
}
```

Then call from terminal:
```bash
unity command scan-scene --verbose
```

## Agent-Native Dev Cycle

```
┌─────────────────────────────────────────────────────────┐
│  Agent-Assisted Unity Development Loop                   │
│                                                          │
│  1. unity command eval "return ..."   ← Observe         │
│  2. Edit C# script (via Hermes file tools)  ← Act       │
│  3. unity command eval "..."          ← Verify          │
│  4. Repeat → ship                                          │
└─────────────────────────────────────────────────────────┘
```

### Example: Fix a runtime bug

```bash
# 1. Observe — check what's broken
unity command eval "return GameObject.FindObjectsByType<Collider>(FindObjectsSortMode.None).Length;"

# 2. Edit — fix the script (via Hermes)
# [agent edits the .cs file]

# 3. Verify — check Play mode state
unity command eval "return UnityEditor.EditorApplication.isPlaying;"
```

## MCP Integration

The Unity CLI's structured JSON output maps naturally to MCP tools.
Each `[CliCommand]` becomes a discoverable tool:

```json
{
  "name": "scan-scene",
  "description": "Scan scene for null references",
  "inputSchema": {
    "type": "object",
    "properties": {
      "verbose": {
        "type": "boolean",
        "description": "Print details"
      }
    }
  }
}
```

## Files

```
10-Labs/gentech-unity-cli/
├── SKILL.md              # This file
└── scripts/
    └── unity-agent.py    # Agent-friendly Unity CLI wrapper
```

## Prerequisites

- Windows (for Unity Editor + CLI)
- 32GB RAM free for Unreal (Unity CLI uses minimal RAM)
- Unity 6.0 LTS or newer for Pipeline package
