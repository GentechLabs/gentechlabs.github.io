#!/usr/bin/env python3
"""
GenTech DeFi Model — Training Data Extractor
Extracts training pairs from vault for fine-tuning
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/root/vaults/gentech")
OUTPUT_PATH = Path("/root/vaults/gentech/02-Labs/defi-model/training-data")

def extract_defi_data():
    """Extract DeFi-related content from vault"""
    training_pairs = []
    
    # Sources to scan
    sources = [
        VAULT_PATH / "11-Mess Hall",
        VAULT_PATH / "02-Labs",
        VAULT_PATH / "03-Strategies",
        VAULT_PATH / "00-HQ",
    ]
    
    keywords = [
        "LP", "liquidity", "yield", "farming", "compound", "extract",
        "AVAX", "USDC", "DeFi", "portfolio", "position", "fee",
        "IL", "impermanent loss", "range", "curve", "bid-ask",
        "FOMC", "macro", "market", "narrative", "rotation"
    ]
    
    for source in sources:
        if not source.exists():
            continue
            
        for md_file in source.rglob("*.md"):
            try:
                content = md_file.read_text()
                
                # Look for decision patterns
                decisions = extract_decisions(content)
                for decision in decisions:
                    training_pairs.append({
                        "question": decision["context"],
                        "answer": decision["decision"],
                        "source": str(md_file),
                        "type": "decision"
                    })
                
                # Look for analysis patterns
                analyses = extract_analyses(content)
                for analysis in analyses:
                    training_pairs.append({
                        "question": analysis["question"],
                        "answer": analysis["analysis"],
                        "source": str(md_file),
                        "type": "analysis"
                    })
                
                # Look for action patterns
                actions = extract_actions(content)
                for action in actions:
                    training_pairs.append({
                        "question": action["situation"],
                        "answer": action["action"],
                        "source": str(md_file),
                        "type": "action"
                    })
                    
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
    
    return training_pairs

def extract_decisions(content):
    """Extract decision patterns from content"""
    decisions = []
    
    # Pattern: "We decided to..." or "Decision:..."
    patterns = [
        r"(?:We decided to|Decision:|Chose to|Selected)\s+(.+?)(?:\.|$)",
        r"(?:Because|Since|Given that)\s+(.+?),?\s+we\s+(.+?)(?:\.|$)",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match.groups()) >= 2:
                decisions.append({
                    "context": f"Why did we {match.group(2)}?",
                    "decision": match.group(0)
                })
    
    return decisions

def extract_analyses(content):
    """Extract analysis patterns from content"""
    analyses = []
    
    # Pattern: "The analysis shows..." or "Analysis:..."
    patterns = [
        r"(?:Analysis|Insight|Finding|Observation):\s+(.+?)(?:\.|$)",
        r"(?:The data shows|We found|Results indicate)\s+(.+?)(?:\.|$)",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            analyses.append({
                "question": f"What does the analysis show about this?",
                "analysis": match.group(0)
            })
    
    return analyses

def extract_actions(content):
    """Extract action patterns from content"""
    actions = []
    
    # Pattern: "We should..." or "Action:..."
    patterns = [
        r"(?:We should|Action:|Next step:|Recommendation:)\s+(.+?)(?:\.|$)",
        r"(?:To fix|To improve|To optimize)\s+(.+?),?\s+we\s+(.+?)(?:\.|$)",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match.groups()) >= 2:
                actions.append({
                    "situation": f"How do we {match.group(1)}?",
                    "action": match.group(0)
                })
    
    return actions

def save_training_data(pairs):
    """Save training pairs to JSON"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_PATH / f"training-pairs-{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(pairs, f, indent=2)
    
    print(f"Extracted {len(pairs)} training pairs to {output_file}")
    
    # Also save as JSONL for fine-tuning
    jsonl_file = OUTPUT_PATH / f"training-pairs-{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(jsonl_file, 'w') as f:
        for pair in pairs:
            f.write(json.dumps(pair) + '\n')
    
    print(f"Saved JSONL format to {jsonl_file}")
    
    return output_file, jsonl_file

if __name__ == "__main__":
    print("Extracting DeFi training data from vault...")
    pairs = extract_defi_data()
    
    if pairs:
        save_training_data(pairs)
        print(f"\nSummary:")
        print(f"  Total pairs: {len(pairs)}")
        print(f"  By type:")
        for ptype in set(p['type'] for p in pairs):
            count = len([p for p in pairs if p['type'] == ptype])
            print(f"    {ptype}: {count}")
    else:
        print("No training pairs found. Need more vault content.")
