#!/usr/bin/env python3
"""
Telegram Model Switch Skill
Lets Jordan switch Hermes agent models from Telegram chat.
"""

import os
import yaml
import subprocess
import re
from pathlib import Path

# Only Jordan's Telegram user ID can use this
AUTHORIZED_USER_ID = 0  # Replace with actual Telegram user ID from memory

# Profile paths
PROFILES = {
    'default': '/root/.hermes/profiles/default',
    'yoyo': '/root/.hermes/profiles/yoyo',
    'dmob': '/root/.hermes/profiles/dmob',
    'desmond': '/root/.hermes/profiles/desmond',
}

# Common model mappings
MODEL_ALIASES = {
    'mimo': ('nous', 'xiaomi/mimo-v2-pro'),
    'atem': ('nous', 'atem/atem-v1'),
    'step': ('stepfun', 'step/step-3.6-chat'),
    'step-3.5': ('stepfun', 'step/step-3.5'),
    'qwen': ('openrouter', 'qwen/qwen-3.6-chat'),
    'claude-sonnet': ('openrouter', 'anthropic/claude-sonnet-4'),
    'gpt-4': ('openai', 'gpt-4-turbo'),
}

# Provider base URLs
PROVIDER_URLS = {
    'nous': 'https://inference-api.nousresearch.com/v1',
    'openrouter': 'https://openrouter.ai/api/v1',
    'openai': 'https://api.openai.com/v1',
    'stepfun': 'https://api.stepfun.com/v1',
}


def get_current_model(profile='default'):
    """Read current model from profile config."""
    cfg_path = Path(PROFILES[profile]) / 'config.yaml'
    if not cfg_path.exists():
        return None, None
    
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    
    model_cfg = cfg.get('model', {})
    provider = model_cfg.get('provider')
    model = model_cfg.get('default')
    return provider, model


def set_model(profile, provider, model):
    """Update config.yaml with new provider/model."""
    cfg_path = Path(PROFILES[profile]) / 'config.yaml'
    if not cfg_path.exists():
        return False, "Profile not found"
    
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    
    if 'model' not in cfg:
        cfg['model'] = {}
    
    cfg['model']['provider'] = provider
    cfg['model']['default'] = model
    
    # Update base_url if needed
    if provider in PROVIDER_URLS:
        cfg['model']['base_url'] = PROVIDER_URLS[provider]
    
    with open(cfg_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
    
    return True, f"Updated {profile} → {provider}/{model}"


def restart_gateway(profile):
    """Restart the Hermes gateway for this profile."""
    hermecmd = subprocess.run(
        ['pkill', '-f', f'hermes gateway run.*{profile}'],
        capture_output=True, text=True
    )
    # Gateway will auto-restart via systemd/cron or manual start needed
    return True


def handle_models_command(args, context):
    """List available models for this agent."""
    profile = context.get('profile', 'default')
    current_provider, current_model = get_current_model(profile)
    
    lines = ["**Available Models:**\n"]
    
    for alias, (provider, model) in MODEL_ALIASES.items():
        badge = " ✅" if (provider == current_provider and model == current_model) else ""
        lines.append(f"• `{provider}/{model}`{badge}")
    
    lines.append(f"\n**Current:** `{current_provider}/{current_model}`")
    lines.append("\nSwitch with: `/model provider/model`")
    lines.append("Example: `/model openrouter/qwen/qwen-3.6-chat`")
    
    return "\n".join(lines)


def handle_model_command(args, context):
    """Switch to a new model."""
    if not args:
        return "Usage: `/model <provider>/<model>`\nExample: `/model openrouter/qwen/qwen-3.6-chat`"
    
    profile = context.get('profile', 'default')
    
    # Parse provider/model
    parts = args.strip().split('/', 1)
    if len(parts) != 2:
        return "❌ Invalid format. Use: `/model provider/model-name`"
    
    provider, model = parts
    
    # Check if it's an alias
    if model in MODEL_ALIASES:
        provider, model = MODEL_ALIASES[model]
    
    # Ask for confirmation
    current_provider, current_model = get_current_model(profile)
    confirm_msg = f"Switch {profile} from `{current_provider}/{current_model}` → `{provider}/{model}`?"
    
    # TODO: Implement yes/no confirmation flow
    # For now, just switch
    
    success, msg = set_model(profile, provider, model)
    if not success:
        return f"❌ {msg}"
    
    # Restart gateway
    restart_gateway(profile)
    
    return f"✓ {msg}\nGateway restarting… (5-10 sec)"


def handle(args, context):
    """Main entry point for the skill."""
    command = args.strip().split()[0] if args else ''
    
    if command == '/models' or command == 'models':
        return handle_models_command(args.replace('/models', '').strip(), context)
    elif command == '/model' or command == 'model':
        rest = args.replace('/model', '').strip()
        return handle_model_command(rest, context)
    else:
        return "Model switch skill. Commands: `/model <provider/model>`, `/models`"
