#!/usr/bin/env python3
"""
Detect Python bytecode corruption in Hermes agent installation.

Compares .pyc file sizes against their corresponding .py source files.
A significantly smaller .pyc indicates truncation/corruption.

Usage: python detect_bytecode_corruption.py
Output: Lists corrupted files with size comparison.
"""

import os
import glob
import sys

PYCACHE_DIR = '/usr/local/lib/hermes-agent/agent/__pycache__'

def check_corruption():
    corrupted = []
    pyc_files = glob.glob(os.path.join(PYCACHE_DIR, '*.pyc'))
    
    for pyc in pyc_files:
        # Derive source .py path
        basename = os.path.basename(pyc)
        # Remove .cpython-311.pyc suffix → get module name
        if '.cpython-311.pyc' in basename:
            mod_name = basename.replace('.cpython-311.pyc', '')
        else:
            continue
        
        py_src = os.path.join(os.path.dirname(pyc), mod_name + '.py')
        if not os.path.exists(py_src):
            continue
        
        pyc_size = os.path.getsize(pyc)
        py_size = os.path.getsize(py_src)
        
        # Heuristic: if .pyc is < 50% of .py size, it's likely truncated
        # (compiled bytecode is typically smaller, but not 2x smaller than source)
        if pyc_size < py_size * 0.5:
            corrupted.append((pyc, pyc_size, py_size))
    
    return corrupted

if __name__ == '__main__':
    print("=== Bytecode Corruption Detection ===\n")
    
    if not os.path.exists(PYCACHE_DIR):
        print(f"ERROR: Pycache directory not found: {PYCACHE_DIR}")
        sys.exit(1)
    
    corrupted = check_corruption()
    
    if not corrupted:
        print("✓ No bytecode corruption detected. All .pyc files appear healthy.")
        sys.exit(0)
    
    print(f"⚠️  Found {len(corrupted)} corrupted bytecode file(s):\n")
    for pyc, pyc_size, py_size in corrupted:
        ratio = pyc_size / py_size * 100
        print(f"  {os.path.basename(pyc)}")
        print(f"    .pyc: {pyc_size:,} bytes")
        print(f"    .py : {py_size:,} bytes")
        print(f"    ratio: {ratio:.1f}% (expected >50%)")
        print()
    
    print("RECOMMENDED ACTION:")
    print("  find /usr/local/lib/hermes-agent -name '*.pyc' -delete")
    print("  Then restart all gateways to regenerate caches.\n")
    sys.exit(2)
