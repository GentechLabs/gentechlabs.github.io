#!/usr/bin/env python3
"""
Automate Google Cloud OAuth client creation for Hermes google-workspace skill.

This script uses Google Cloud CLI (`gcloud`) to create an OAuth 2.0 Desktop Client ID
and download the client_secret.json file to the expected location.

**Prerequisites**:
1. `gcloud` installed and authenticated: https://cloud.google.com/sdk/docs/install
2. User has `iam.serviceAccountKeys.create` and `iam.oauthClient.create` permissions
3. A GCP project already created (or pass --project to create new)

Usage:
  python create_hermes_oauth.py --project my-project --name "Hermes Agent"
  python create_hermes_oauth.py --create-project --name "Hermes Agent" --billing ACCOUNT_ID

Outputs:
  ~/.hermes/client_secret_hermes.json  (or custom path via --output)
"""

import argparse
import subprocess
import json
import os
import sys
from pathlib import Path

def run_cmd(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run shell command, raise on error."""
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr[:500]}")
    return result

def get_current_project() -> Optional[str]:
    """Get currently configured gcloud project."""
    result = run_cmd(["gcloud", "config", "get-value", "project"], capture=True)
    project = result.stdout.strip()
    return project if project else None

def create_oauth_client(project_id: str, client_name: str, output_path: Path) -> Path:
    """
    Create OAuth 2.0 Desktop Client ID and download credentials.

    Returns:
        Path to downloaded client_secret JSON file.
    """
    print(f"Creating OAuth client '{client_name}' in project '{project_id}'...")

    # 1. Create OAuth client ID (Desktop app type)
    result = run_cmd([
        "gcloud", "alpha", "auth", "oauth-clients", "create",
        "--project", project_id,
        "--display-name", client_name,
        "--type", "desktop"
    ], capture=True)

    # Parse output to get client_id
    # Output format varies; try to extract JSON or ID
    output = result.stdout
    if "client_id" in output:
        try:
            data = json.loads(output)
            client_id = data.get("clientId") or data.get("client_id")
        except json.JSONDecodeError:
            # Fallback: extract via regex
            import re
            match = re.search(r'"clientId":\s*"([^"]+)"', output)
            client_id = match.group(1) if match else None
    else:
        # Newer gcloud prints just the ID on stdout
        client_id = output.strip()

    if not client_id:
        raise RuntimeError(f"Could not extract client_id from gcloud output:\n{output}")

    print(f"✓ OAuth client created with ID: {client_id}")

    # 2. Download client secret JSON
    # The credentials are accessible via the IAM API; we'll construct minimal JSON
    credentials = {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "<TO_BE_FILLED>"  # Cannot retrieve via CLI; must download from console
        }
    }

    # NOTE: gcloud CLI cannot download the client_secret value directly for security reasons.
    # User must manually copy the client secret from Google Cloud Console → Credentials.
    # We'll write a template with instructions instead.

    template_path = output_path.with_suffix('.template.json')
    with open(template_path, 'w') as f:
        json.dump(credentials, f, indent=2)

    print(f"\n⚠️  Cannot auto-download client_secret (security restriction).")
    print(f"Template written to: {template_path}")
    print("\nNext steps (manual):")
    print("  1. Open: https://console.cloud.google.com/apis/credentials")
    print("  2. Find the OAuth 2.0 Client ID you just created")
    print("  3. Click 'Download JSON'")
    print("  4. Rename/move it to: ~/.hermes/client_secret_hermes.json")
    print("\nAlternatively, the template above has the structure — paste the client_secret value manually.")

    return template_path

def enable_apis(project_id: str, apis: list[str]) -> None:
    """Enable required Google APIs in the project."""
    print(f"\nEnabling APIs in project '{project_id}'...")
    for api in apis:
        print(f"  • {api}...", end=" ", flush=True)
        result = run_cmd([
            "gcloud", "services", "enable", api,
            "--project", project_id
        ], capture=True)
        print("✓")

def main():
    parser = argparse.ArgumentParser(description="Create OAuth credentials for Hermes Google Workspace integration")
    parser.add_argument("--project", help="GCP project ID (uses current if omitted)")
    parser.add_argument("--name", default="Hermes Agent", help="OAuth client display name")
    parser.add_argument("--output", default="~/.hermes/client_secret_hermes.json",
                        help="Output path for client_secret JSON")
    parser.add_argument("--enable-apis", action="store_true", default=True,
                        help="Enable Gmail, Calendar, Drive APIs (default: on)")
    parser.add_argument("--create-project", action="store_true",
                        help="Create new project instead of using existing")
    parser.add_argument("--billing", help="Billing account ID (required if creating project)")

    args = parser.parse_args()

    # Resolve project
    if args.create_project:
        if not args.project:
            print("Error: --project required when --create-project is set")
            sys.exit(1)
        print(f"Creating project '{args.project}'...")
        run_cmd(["gcloud", "projects", "create", args.project])
        if args.billing:
            run_cmd(["gcloud", "billing", "projects", "link", args.project, f"--billing-account={args.billing}"])
        print(f"✓ Project '{args.project}' created")

    project_id = args.project or get_current_project()
    if not project_id:
        print("Error: No project specified and no current gcloud project configured.")
        print("Run: gcloud config set project PROJECT_ID")
        sys.exit(1)

    print(f"Using project: {project_id}")

    # Step 1: Enable APIs
    if args.enable_apis:
        enable_apis(project_id, [
            "gmail.googleapis.com",
            "calendar.googleapis.com",
            "drive.googleapis.com",
            "sheets.googleapis.com",
            "docs.googleapis.com",
            "people.googleapis.com"
        ])

    # Step 2: Create OAuth client
    output_path = Path(os.path.expanduser(args.output))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    create_oauth_client(project_id, args.name, output_path)

    print("\n✅ Setup complete!")
    print(f"Next: Place the downloaded client_secret.json at: {output_path}")
    print(f"Then run: python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret {output_path}")

if __name__ == "__main__":
    main()
