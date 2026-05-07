---
name: hermes-oauth-refresh
version: 1.0
tags: [devops, auth, nous, maintenance]
description: |
  Proactive management of Hermes OAuth token refresh and re-authentication workflows.
  Covers automated token refresh scripts, handling revoked sessions, and device flow completion.
  This skill governs the maintenance of OAuth-based provider credentials in Hermes profiles.
---
prelude: |
  When running scheduled cron jobs or automated agents, OAuth token expiry is a common maintenance task.
  Hermes provides built-in scripts to handle this proactively, especially for cron job scenarios.

  Key components:
  - `refresh_nous_oauth.py` - Main automated refresh script
  - `complete_nous_device_flow.py` - Device flow completion script
  - `auth.json` - Authentication state storage
  - `config.yaml` - Provider configuration

learning_outcomes:
  - Identify when OAuth tokens need manual re-authentication vs. automatic refresh
  - Execute the refresh_nous_oauth.py script correctly
  - Handle the "needs_reauth: true" condition appropriately
  - Complete the device flow authentication when required
  - Interpret auth.json and token expiry states

sections:
  - chapter: Introduction
    content: |
      Hermes profiles using OAuth providers (like Nous) require periodic token refreshes. The system
      includes automated scripts to handle this proactively, especially for cron job scenarios.

      Key components:
      - `refresh_nous_oauth.py` - Main automated refresh script
      - `complete_nous_device_flow.py` - Device flow completion script
      - `auth.json` - Authentication state storage
      - `config.yaml` - Provider configuration

  - chapter: Automated Refresh Workflow
    content: |
      The primary script for proactive token management is `/root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py`.

      ### Execution
      ```bash
      python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
      ```

      ### Expected Outputs
      - **Success (success: true)**: Tokens are fresh and valid
      - **Needs Reauth (success: false, needs_reauth: true)**: Token fully revoked, requires manual intervention
      - **Critical Error (success: false, critical: true)**: Unexpected script failure

      ### Exit Codes
      - `0` - Tokens fresh OR re-auth needed (expected maintenance state)
      - `1` - Unexpected critical error

      The script is designed to return 0 even when re-auth is needed to avoid false positive alerts in monitoring systems.

  - chapter: Handling Revoked Sessions
    content: |
      When the refresh script returns `needs_reauth: true`, the OAuth session has been fully revoked
      and requires manual re-authentication via `hermes model`.

      Message to expect:
      ```
      "Refresh session has been revoked Run `hermes model` to re-authenticate."
      ```

      ### Required Action
      Run the following command in an **interactive terminal**:
      ```bash
      hermes model
      ```

      This initiates the device flow authentication process:
      1. Generates a device code
      2. Saves pending flow state to `pending_nous_device_flow_latest.json`
      3. Displays verification URL and user code
      4. User completes authentication in browser
      5. Tokens are saved to `auth.json`

      ### Important Notes
      - The `hermes model` command **requires** an interactive terminal
      - Cannot be executed in cron jobs or non-interactive contexts
      - After running `hermes model`, wait for user authentication to complete
      - Then run the device flow completion script (see next section)

  - chapter: Device Flow Completion
    content: |
      After initiating device flow via `hermes model` and completing browser authentication,
      the pending device flow file must be processed to obtain the actual tokens.

      ### Completion Script
      ```bash
      python3 /root/.hermes/profiles/gentech/scripts/complete_nous_device_flow.py
      ```

      ### Prerequisites
      - The `pending_nous_device_flow_latest.json` file must exist in the scripts directory
      - The user must have visited the verification URL and completed authentication
      - The device code must not have expired (typically 10-15 minutes validity)

      ### Script Behavior
      - Polls the OAuth token endpoint until tokens are obtained
      - Saves tokens to `auth.json`
      - Removes the pending flow file upon success
      - Handles errors like expiration, authorization pending, and slow_down

      ### Monitoring Output
      The script provides real-time feedback:
      ```
      Nous OAuth Device Flow Completion
      ==================================
      Verify at: https://portal.nousresearch.com/manage-subscription
      Expires: 2026-05-06 13:30 UTC

      Polling for token completion...
      ```

  - chapter: Auth File Structure
    content: |
      Understanding `auth.json` is crucial for troubleshooting:

      ```json
      {
        "credential_pool": {
          "nous": [
            {
              "access_token": "eyJhbG...",
              "refresh_token": "rt_u0u55a4Uyu8dpMEH8VK3L7FtPtldLqwvz2VaJ805xGNOigHY3OABeYdtGDseEoiI",
              "expires_at": "2026-05-06T12:38:54.268608+00:00",
              "agent_key": "sk-nou...",
              "expires_in": 900
            }
          ]
        },
        "providers": {
          "nous": {
            "access_token": "...",
            "refresh_token": "...",
            "expires_at": "...",
            "agent_key": "..."
          }
        }
      }
      ```

      Key fields to monitor:
      - `expires_at` - When the access token expires
      - `refresh_token` - Present for refresh capability
      - `needs_reauth` flag from refresh script output

  - chapter: Troubleshooting
    content: |
      ### Script not found errors
      Ensure you're in the correct Hermes profile directory:
      ```bash
      cd /root/.hermes/profiles/gentech
      ```

      ### Device flow file missing
      Run `hermes model` first to initiate device flow.

      ### Token refresh fails repeatedly
      The session may be permanently revoked. Full re-authentication required.

      ### Script permissions
      Scripts should be executable. Fix with:
      ```bash
      chmod +x /root/.hermes/profiles/gentech/scripts/*.py
      ```

      ### Python path issues
      The refresh script adds `/usr/local/lib/hermes-agent` to Python path.
      Ensure Hermes is installed there.

  - chapter: Best Practices
    content: |
      - Run the refresh script regularly via cron (it's designed for this)
      - Monitor logs for `needs_reauth: true` conditions
      - Keep `hermes model` command available for manual re-authentication
      - Document the verification URL and user code when initiating device flow
      - Test the workflow periodically to ensure it works when needed

  - chapter: Integration with Monitoring
    content: |
      The refresh script is designed for monitoring systems:
      - Exit code 0 prevents false alerts
      - JSON output contains `needs_reauth` flag for manual review
      - Check logs or parse JSON for maintenance conditions
      - Consider pairing with `hermes status` checks for comprehensive monitoring

references:
  - file: references/auth-workflow-diagram.png
    description: Visual diagram of the OAuth refresh and re-authentication flow
  - file: references/refresh-script-output-example.json
    description: Sample JSON output from successful refresh attempt
  - file: references/device-flow-initiation-transcript.txt
    description: Example interaction when running `hermes model`

scripts:
  - file: scripts/auth-health-check.py
    description: Quick script to check auth file status and token validity
  - file: scripts/test-refresh-cycle.sh
    description: Integration test for the full refresh workflow

templates:
  - file: templates/auth-monitor-config.yaml
    description: Template for monitoring auth health in external systems

epilogue: |
      This skill covers the complete OAuth token management lifecycle in Hermes.
      Remember: automated refresh handles normal expiry; device flow handles revoked sessions.
      Always use interactive terminal for `hermes model` initiation.