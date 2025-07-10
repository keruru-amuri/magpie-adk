#!/usr/bin/env python3
"""
Setup script for Google ADK with Azure OpenAI via LiteLLM
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Google ADK with Azure OpenAI via LiteLLM")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found. Make sure to create it with your Azure OpenAI credentials.")
        return False
    
    # Create virtual environment
    if not run_command("python -m venv .venv", "Creating virtual environment"):
        return False
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = ".venv\\Scripts\\activate"
        pip_command = ".venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = ".venv/bin/activate"
        pip_command = ".venv/bin/pip"
    
    # Install requirements
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing requirements"):
        return False
    
    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Test the agent: python agents.py")
    print("3. Start the web interface: adk web")
    print("4. Open http://localhost:8000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
