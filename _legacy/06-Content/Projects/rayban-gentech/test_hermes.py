#!/usr/bin/env python3
"""
Test script to verify Hermes integration works
"""
import os
import sys
import asyncio
import subprocess

async def test_hermes_connection():
    """Test if we can communicate with Hermes"""
    print("🔍 Testing Hermes connection...")
    
    # Test command structure
    cmd = ["hermes", "-p", "gentech", "chat", "-q", "test message", "-Q"]
    
    try:
        print(f"Running: {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        
        if proc.returncode == 0:
            output = stdout.decode().strip()
            print(f"✅ Success: {output}")
            return True
        else:
            error = stderr.decode().strip()
            print(f"❌ Error: {error}")
            return False
            
    except asyncio.TimeoutError:
        print("⏰ Timeout: Hermes took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

async def test_simple_server_imports():
    """Test if we can import required modules for simple server"""
    print("🔍 Testing server imports...")
    
    try:
        import json
        print("✓ json available")
    except ImportError:
        print("✗ json missing")
        return False
    
    try:
        import time
        print("✓ time available")
    except ImportError:
        print("✗ time missing")
        return False
        
    try:
        import datetime
        print("✓ datetime available")
    except ImportError:
        print("✗ datetime missing")
        return False
        
    try:
        import pathlib
        print("✓ pathlib available")
    except ImportError:
        print("✗ pathlib missing")
        return False
        
    print("✓ All basic imports available")
    return True

async def main():
    print("🚀 Gentech Ray-Ban Bridge Test")
    print("=" * 40)
    
    # Test Hermes connection
    hermes_ok = await test_hermes_connection()
    
    # Test basic imports
    imports_ok = await test_simple_server_imports()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Hermes connection: {'✅' if hermes_ok else '❌'}")
    print(f"Basic imports: {'✅' if imports_ok else '❌'}")
    
    if hermes_ok and imports_ok:
        print("\n🎉 Tests passed! The bridge should work.")
        print("To run the server, install dependencies:")
        print("  pip install fastapi uvicorn")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))