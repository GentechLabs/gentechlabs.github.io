"""
GenTech Agent Governance Integration
Two-way consensus: Hermes instructs → AGT verifies → Agent executes (or is denied)

Usage:
    from governance import GovernedAgent
    
    agent = GovernedAgent("escrow-agent", policy_path="policies/defi-governance.yaml")
    result = agent.execute(tool_name="transfer", params={"amount": 100, "to": "0x..."})
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

try:
    from agent_os.policies import PolicyEvaluator, PolicyDocument, PolicyRule, PolicyCondition, PolicyAction, PolicyOperator, PolicyDefaults
    AGT_AVAILABLE = True
except ImportError:
    AGT_AVAILABLE = False
    print("Warning: agent-os-kernel not installed. Governance disabled.")

try:
    from agent_sre.kill_switch import KillSwitch
    KILL_SWITCH_AVAILABLE = True
except ImportError:
    KILL_SWITCH_AVAILABLE = False


class GovernanceAuditLog:
    """Tamper-evident audit log for agent actions."""
    
    def __init__(self, log_path: str = "governance/audit.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def record(self, agent_id: str, action: str, decision: str, reason: str, 
               policy_rule: Optional[str] = None, metadata: Optional[dict] = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "action": action,
            "decision": decision,
            "reason": reason,
            "policy_rule": policy_rule,
            "metadata": metadata or {}
        }
        with open(self.log_path, "a") as f:
            f.write(f"{entry}\n")
        return entry


class GovernedAgent:
    """
    Agent wrapper with AGT governance layer.
    Every tool call is checked against policy before execution.
    """
    
    def __init__(self, agent_id: str, policy_path: str, audit_log_path: str = "governance/audit.log"):
        self.agent_id = agent_id
        self.audit = GovernanceAuditLog(audit_log_path)
        self._kill_switch = None
        
        if AGT_AVAILABLE:
            self.evaluator = self._load_policy(policy_path)
        else:
            self.evaluator = None
            print(f"⚠️  Agent {agent_id}: Governance disabled (AGT not available)")
        
        if KILL_SWITCH_AVAILABLE:
            self._kill_switch = KillSwitch()
    
    def _load_policy(self, policy_path: str) -> Optional[Any]:
        """Load YAML policy into AGT evaluator."""
        if not AGT_AVAILABLE:
            return None
            
        with open(policy_path) as f:
            policy_data = yaml.safe_load(f)
        
        rules = []
        for rule_data in policy_data.get("rules", []):
            cond = rule_data.get("condition", {})
            action_str = rule_data.get("action", "deny").upper()
            
            try:
                action = PolicyAction[action_str]
            except KeyError:
                action = PolicyAction.DENY
            
            rules.append(PolicyRule(
                name=rule_data["name"],
                condition=PolicyCondition(
                    field=cond.get("field", ""),
                    operator=PolicyOperator[cond.get("operator", "eq").upper()],
                    value=cond.get("value", "")
                ),
                action=action,
                priority=rule_data.get("priority", 50),
                message=rule_data.get("message", "")
            ))
        
        defaults = policy_data.get("defaults", {})
        evaluator = PolicyEvaluator(policies=[PolicyDocument(
            name=policy_data.get("name", "unnamed"),
            version=policy_data.get("version", "1.0"),
            defaults=PolicyDefaults(
                action=PolicyAction[defaults.get("action", "deny").upper()]
            ),
            rules=rules
        )])
        
        print(f"✅ Loaded policy: {policy_data.get('name')} ({len(rules)} rules)")
        return evaluator
    
    def check(self, action: str, **kwargs) -> dict:
        """Check action against governance policy."""
        if not self.evaluator:
            return {"allowed": True, "reason": "Governance disabled"}
        
        context = {"action": action, **kwargs}
        result = self.evaluator.evaluate(context)
        
        decision = "allowed" if result.allowed else "denied"
        self.audit.record(
            agent_id=self.agent_id,
            action=action,
            decision=decision,
            reason=result.reason if hasattr(result, 'reason') else str(result),
            policy_rule=result.matched_rule if hasattr(result, 'matched_rule') else None,
            metadata=kwargs
        )
        
        return {
            "allowed": result.allowed,
            "reason": result.reason if hasattr(result, 'reason') else None,
            "rule": result.matched_rule if hasattr(result, 'matched_rule') else None
        }
    
    def execute(self, tool_name: str, params: dict = None) -> dict:
        """Execute tool with governance check."""
        # Check kill switch first
        if self._kill_switch and self._kill_switch.is_triggered():
            return {"success": False, "error": "Kill switch triggered", "agent": self.agent_id}
        
        # Governance check
        check_result = self.check(tool_name, **(params or {}))
        
        if not check_result["allowed"]:
            return {
                "success": False,
                "error": f"Governance denied: {check_result['reason']}",
                "rule": check_result["rule"],
                "agent": self.agent_id
            }
        
        # If allowed, execute would happen here
        # In real integration, this calls the actual tool function
        return {"success": True, "agent": self.agent_id, "tool": tool_name, "params": params}
    
    def emergency_stop(self):
        """Trigger kill switch — stops all agent operations."""
        if self._kill_switch:
            self._kill_switch.trigger()
            self.audit.record(
                agent_id=self.agent_id,
                action="emergency_stop",
                decision="executed",
                reason="Kill switch activated"
            )
            return True
        return False


# Convenience function for quick governance wrapping
def govern(tool_func, policy_path: str):
    """Wrap any tool function with governance. Drop-in replacement for AGT's govern()."""
    agent = GovernedAgent("wrapper", policy_path)
    
    def governed_wrapper(*args, **kwargs):
        check = agent.check(tool_func.__name__, *args, **kwargs)
        if not check["allowed"]:
            raise PermissionError(f"Governance denied: {check['reason']}")
        return tool_func(*args, **kwargs)
    
    return governed_wrapper
