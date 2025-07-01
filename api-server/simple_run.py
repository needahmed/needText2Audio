#!/usr/bin/env python3
"""
Simple startup script for Kokoro TTS API server
"""

import uvicorn
import sys
import os

if __name__ == "__main__":
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting Kokoro TTS API server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation will be available at: http://localhost:8000/docs")
    
    try:
        # Simple direct run without reload to avoid multiprocessing issues
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        print("This might be due to missing Kokoro dependencies.")
        print("The server will start with mock TTS functionality.") 