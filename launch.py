"""Launcher for Saulo v2."""
import subprocess
import sys
import time
import os

def start_services():
    """Start all services for Saulo v2."""
    print("=" * 50)
    print("SAULO v2 - Asistente IA")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("ERROR: main.py not found!")
        print("Run this from the saulo-v2 directory")
        sys.exit(1)
    
    # Start Saulo v2 server
    print("Starting Saulo v2 server on port 8000...")
    saulo_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Start cloudflared
    print("Starting Cloudflared tunnel...")
    cloudflared_process = subprocess.Popen(
        ["cloudflared", "tunnel", "--config", r"C:\Users\xiute\.cloudflared\config.yml", "run", "saulo"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print()
    print("=" * 50)
    print("SAULO v2 STARTED")
    print("=" * 50)
    print()
    print("Local:   http://127.0.0.1:8000")
    print("Web:     https://saulo.dogma.tools")
    print("Admin:   xiute / admin123")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Keep main process alive
        while True:
            time.sleep(1)
            # Check if processes are still running
            if saulo_process.poll() is not None:
                print("Saulo server stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
        saulo_process.terminate()
        cloudflared_process.terminate()
        print("Done!")

if __name__ == "__main__":
    start_services()