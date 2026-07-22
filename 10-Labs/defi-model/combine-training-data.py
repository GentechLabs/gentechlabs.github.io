#!/usr/bin/env python3
"""
GenTech DeFi Model — Training Data Combiner
Combines all training data sources into final dataset
"""

import json
from pathlib import Path
from datetime import datetime

TRAINING_DATA_PATH = Path("/root/vaults/gentech/02-Labs/defi-model/training-data")
OUTPUT_PATH = Path("/root/vaults/gentech/02-Labs/defi-model")

def combine_training_data():
    """Combine all training data sources"""
    all_pairs = []
    
    # Find all training data files
    for json_file in TRAINING_DATA_PATH.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                pairs = json.load(f)
                all_pairs.extend(pairs)
                print(f"Loaded {len(pairs)} pairs from {json_file.name}")
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    # Deduplicate by question
    seen_questions = set()
    unique_pairs = []
    for pair in all_pairs:
        question = pair.get('question', '')
        if question not in seen_questions:
            seen_questions.add(question)
            unique_pairs.append(pair)
    
    print(f"\nTotal pairs: {len(all_pairs)}")
    print(f"Unique pairs: {len(unique_pairs)}")
    
    return unique_pairs

def format_for_finetuning(pairs):
    """Format pairs for fine-tuning"""
    formatted = []
    
    for pair in pairs:
        # Format as instruction-following
        formatted.append({
            "instruction": pair.get('question', ''),
            "input": "",
            "output": pair.get('answer', ''),
            "type": pair.get('type', 'general')
        })
    
    return formatted

def save_final_dataset(pairs):
    """Save final dataset"""
    # Save as JSON
    json_file = OUTPUT_PATH / f"final-training-{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_file, 'w') as f:
        json.dump(pairs, f, indent=2)
    
    # Save as JSONL for fine-tuning
    jsonl_file = OUTPUT_PATH / f"final-training-{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(jsonl_file, 'w') as f:
        for pair in pairs:
            f.write(json.dumps(pair) + '\n')
    
    # Save statistics
    stats = {
        "total_pairs": len(pairs),
        "by_type": {},
        "generated": datetime.now().isoformat(),
        "sources": ["vault extraction", "synthetic generation"]
    }
    
    for pair in pairs:
        ptype = pair.get('type', 'general')
        stats["by_type"][ptype] = stats["by_type"].get(ptype, 0) + 1
    
    stats_file = OUTPUT_PATH / f"training-stats-{datetime.now().strftime('%Y%m%d')}.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\nFinal dataset saved:")
    print(f"  JSON: {json_file}")
    print(f"  JSONL: {jsonl_file}")
    print(f"  Stats: {stats_file}")
    
    return json_file, jsonl_file, stats_file

if __name__ == "__main__":
    print("Combining all training data...")
    pairs = combine_training_data()
    
    if pairs:
        formatted = format_for_finetuning(pairs)
        save_final_dataset(formatted)
        
        print(f"\nFinal dataset summary:")
        print(f"  Total pairs: {len(formatted)}")
        print(f"  By type:")
        for ptype in set(p['type'] for p in formatted):
            count = len([p for p in formatted if p['type'] == ptype])
            print(f"    {ptype}: {count}")
    else:
        print("No training data found.")
