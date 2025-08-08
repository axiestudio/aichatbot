#!/usr/bin/env python3
"""
Quick startup test to identify issues
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

print("🔍 Testing startup components...")

try:
    print("1. Testing config import...")
    from app.core.config import settings
    print(f"✅ Config loaded - Environment: {settings.ENVIRONMENT}")
except Exception as e:
    print(f"❌ Config failed: {e}")
    sys.exit(1)

try:
    print("2. Testing main app import...")
    from app.main import app
    print("✅ Main app imported successfully")
except Exception as e:
    print(f"❌ Main app import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing uvicorn import...")
    import uvicorn
    print("✅ Uvicorn available")
except Exception as e:
    print(f"❌ Uvicorn failed: {e}")
    sys.exit(1)

print("✅ All startup components working!")
print("🚀 Ready to start server!")
