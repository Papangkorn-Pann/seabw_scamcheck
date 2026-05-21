#!/usr/bin/env python3
"""
Verification script to check if SCAMCHECK is properly set up.
Run this before starting the bot to ensure all dependencies are installed.
"""

import os
import sys

def check_dependency(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name.replace("-", "_")

    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        return False

def check_environment():
    """Check if required environment variables are set."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        # Show only first and last 4 characters for security
        masked = f"{token[:4]}...{token[-4:]}"
        print(f"✅ TELEGRAM_BOT_TOKEN is set ({masked})")
        return True
    else:
        print(f"❌ TELEGRAM_BOT_TOKEN is NOT set")
        print("   Set it with: export TELEGRAM_BOT_TOKEN='your-token-here'")
        return False

def main():
    print("=" * 60)
    print("SCAMCHECK - Setup Verification")
    print("=" * 60)

    print("\n📦 Checking dependencies...")
    dependencies = [
        ("transformers", "transformers"),
        ("torch", "torch"),
        ("python-telegram-bot", "telegram"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("kagglehub", "kagglehub"),
        ("datasets", "datasets"),
    ]

    all_deps_ok = all(check_dependency(pkg, imp) for pkg, imp in dependencies)

    print("\n🔐 Checking environment variables...")
    env_ok = check_environment()

    print("\n" + "=" * 60)
    if all_deps_ok and env_ok:
        print("✅ All checks passed! You're ready to run the bot.")
        print("\n   Run: python main.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        if not all_deps_ok:
            print("\n   To install dependencies:")
            print("   pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
