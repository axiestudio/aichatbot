#!/usr/bin/env python3
"""
Minimal test script to identify startup issues
"""

import sys
import os
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure we're in the correct directory
backend_dir = Path(__file__).parent.absolute()
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test all critical imports"""
    try:
        logger.info("🔍 Testing basic imports...")
        
        logger.info("1. Testing config import...")
        from app.core.config import settings
        logger.info(f"✅ Config loaded - Environment: {settings.ENVIRONMENT}")
        
        logger.info("2. Testing database import...")
        from app.core.database import init_database
        logger.info("✅ Database import successful")
        
        logger.info("3. Testing main app import...")
        from app.main import app
        logger.info("✅ Main app imported successfully")
        
        logger.info("4. Testing uvicorn import...")
        import uvicorn
        logger.info("✅ Uvicorn available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_server():
    """Test if we can start a minimal server"""
    try:
        logger.info("🚀 Testing minimal server startup...")
        
        from app.main import app
        import uvicorn
        
        # Test configuration
        config = {
            "app": app,
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "info",
            "access_log": False,
            "reload": False,
        }
        
        logger.info("✅ Server configuration ready")
        logger.info("🎯 Starting server...")
        
        # This will actually start the server
        uvicorn.run(**config)
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🔍 MINIMAL STARTUP TEST")
    
    # Test imports first
    if not test_imports():
        logger.error("❌ Import test failed")
        sys.exit(1)
    
    logger.info("✅ All imports successful")
    
    # Test server startup
    test_minimal_server()
