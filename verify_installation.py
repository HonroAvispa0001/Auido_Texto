"""
Verification Script for Ultra Whisper Transcriptor
Verifica que el código esté listo para producción
"""

import sys
import importlib.util
from pathlib import Path

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    package = package_name or module_name
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False, f"❌ {package} not installed"
        return True, f"✅ {package} installed"
    except Exception as e:
        return False, f"❌ {package} error: {e}"

def check_file_exists(file_path):
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        return True, f"✅ {path.name} found"
    return False, f"❌ {path.name} not found"

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    return False, f"❌ Python {version.major}.{version.minor} (requires 3.8+)"

def check_syntax(file_path):
    """Check Python file for syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, file_path, 'exec')
        return True, f"✅ No syntax errors in {Path(file_path).name}"
    except SyntaxError as e:
        return False, f"❌ Syntax error in {Path(file_path).name}: Line {e.lineno}"
    except Exception as e:
        return False, f"❌ Error checking {Path(file_path).name}: {e}"

def main():
    print("=" * 70)
    print("🔍 ULTRA WHISPER TRANSCRIPTOR - PRODUCTION READINESS CHECK")
    print("=" * 70)
    print()
    
    checks = []
    
    # 1. Python Version
    print("📌 Checking Python Version...")
    status, msg = check_python_version()
    checks.append(status)
    print(f"   {msg}")
    print()
    
    # 2. Required Dependencies
    print("📌 Checking Required Dependencies...")
    required_deps = [
        ('customtkinter', 'customtkinter'),
        ('openai', 'openai'),
    ]
    
    for module, package in required_deps:
        status, msg = check_import(module, package)
        checks.append(status)
        print(f"   {msg}")
    print()
    
    # 3. Optional Dependencies
    print("📌 Checking Optional Dependencies...")
    optional_deps = [
        ('tkinterdnd2', 'tkinterdnd2 (drag-and-drop support)'),
    ]
    
    for module, package in optional_deps:
        status, msg = check_import(module, package)
        # Don't fail if optional deps are missing
        print(f"   {msg}")
    print()
    
    # 4. Required Files
    print("📌 Checking Required Files...")
    required_files = [
        'whisper_multi.py',
        'requirements.txt',
    ]
    
    for file in required_files:
        status, msg = check_file_exists(file)
        checks.append(status)
        print(f"   {msg}")
    print()
    
    # 5. Syntax Check
    print("📌 Checking Python Syntax...")
    status, msg = check_syntax('whisper_multi.py')
    checks.append(status)
    print(f"   {msg}")
    print()
    
    # 6. Configuration File Location
    print("📌 Configuration...")
    from pathlib import Path
    config_path = Path.home() / ".whisper_transcriptor_config.json"
    print(f"   ℹ️  Config will be saved to: {config_path}")
    print()
    
    # Final Summary
    print("=" * 70)
    if all(checks):
        print("✅ ALL CHECKS PASSED - PRODUCTION READY!")
        print()
        print("Next steps:")
        print("1. Run: python whisper_multi.py")
        print("2. Configure your OpenAI API key in Settings")
        print("3. Start transcribing!")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before running the application.")
        print()
        print("To install missing dependencies:")
        print("  pip install -r requirements.txt")
    print("=" * 70)
    
    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())
