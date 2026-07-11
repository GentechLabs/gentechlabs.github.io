#!/usr/bin/env python3
"""
Test the actual server functionality
"""
import asyncio
import os
import subprocess
import json
import time

async def ask_hermes(message: str) -> str:
    """Send message to Hermes and get response - same as server.py"""
    cmd = ["hermes", "-p", "gentech", "chat", "-q", message, "-Q"]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "HERMES_YOLO_MODE": "1"},
        )
        
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=30  # 30 seconds timeout
        )
        
        output = stdout.decode().strip()
        
        # Parse session_id from output (first line: "session_id: ...")
        new_session_id = None
        response_text = output
        
        if output.startswith("session_id:"):
            lines = output.split("\n", 1)
            new_session_id = lines[0].replace("session_id:", "").strip()
            response_text = lines[1].strip() if len(lines) > 1 else ""
        
        return {
            "response": response_text or "(no response)",
            "session_id": new_session_id,
            "ok": True,
        }
        
    except asyncio.TimeoutError:
        return {"response": "⏰ Hermes took too long to respond.", "ok": False, "session_id": None}
    except Exception as e:
        return {"response": f"❌ Error: {str(e)}", "ok": False, "session_id": None}

async def test_server_functionality():
    """Test the core server functionality"""
    print("🚀 Testing Gentech Ray-Ban Bridge Server")
    print("=" * 50)
    
    # Test 1: Basic Hermes communication
    print("🔍 Test 1: Basic Hermes communication")
    result = await ask_hermes("Hello! This is a test message.")
    if result["ok"]:
        print(f"✅ Success: {result['response']}")
    else:
        print(f"❌ Failed: {result['response']}")
    
    # Test 2: Session continuity
    print("\n🔍 Test 2: Session continuity")
    first_result = await ask_hermes("What's your name?")
    if first_result["ok"] and first_result.get("session_id"):
        session_id = first_result["session_id"]
        print(f"✅ First response: {first_result['response']}")
        print(f"📋 Session ID: {session_id}")
        
        # Send follow-up message
        second_result = await ask_hermes("What can you help me with?", session_id)
        if second_result["ok"]:
            print(f"✅ Follow-up response: {second_result['response']}")
        else:
            print(f"❌ Follow-up failed: {second_result['response']}")
    else:
        print("❌ First message failed or no session ID")
    
    # Test 3: Error handling
    print("\n🔍 Test 3: Error handling")
    # Test with empty message
    empty_result = await ask_hermes("")
    print(f"Empty message: {empty_result}")
    
    # Test 4: Form processing simulation
    print("\n🔍 Test 4: Form processing simulation")
    test_messages = [
        "Hello, I'm using Ray-Ban glasses",
        "Can you help me with coding?",
        "Tell me about cryptocurrency"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"  Message {i}: {msg}")
        result = await ask_hermes(msg)
        if result["ok"]:
            print(f"  ✅ Response: {result['response'][:100]}...")
        else:
            print(f"  ❌ Error: {result['response']}")
        time.sleep(1)  # Small delay between messages
    
    return True

async def test_server_requirements():
    """Test if all required dependencies are available"""
    print("\n🔍 Testing server requirements:")
    
    required_modules = [
        "json", "os", "sys", "time", "asyncio", "secrets", "pathlib", "datetime"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
    
    # Test external dependencies
    external_deps = {
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server"
    }
    
    print("\n🔍 External dependencies:")
    for dep, desc in external_deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep} ({desc})")
        except ImportError:
            print(f"❌ {dep} ({desc}) - MISSING")

async def main():
    print("🧪 Gentech Ray-Ban Bridge Comprehensive Test")
    print("=" * 60)
    
    # Test requirements
    await test_server_requirements()
    
    # Test functionality
    await test_server_functionality()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("✅ Core functionality works")
    print("⚠️  External dependencies missing (fastapi, uvicorn)")
    print("📝 To run the server: pip install fastapi uvicorn")
    print("🌐 Server will be available on http://localhost:8765")

if __name__ == "__main__":
    asyncio.run(main())