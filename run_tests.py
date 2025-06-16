#!/usr/bin/env python3
"""
Test Runner for B2 First Content Generation Tool

This script provides easy ways to run different test suites.
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle the result"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 B2 First Content Generation Tool - Test Suite")
    print("=" * 60)
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Install with: pip install pytest pytest-timeout")
        return 1
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "smoke"
    
    success = True
    
    if test_type == "smoke":
        # Run smoke tests only (fast)
        success = run_command(
            "python -m pytest tests/test_smoke.py -v -m unit",
            "Smoke Tests (Unit Tests Only)"
        )
        
    elif test_type == "unit":
        # Run all unit tests
        success = run_command(
            "python -m pytest tests/ -v -m unit",
            "Unit Tests"
        )
        
    elif test_type == "integration":
        # Run integration tests (requires Ollama)
        success = run_command(
            "python -m pytest tests/ -v -m integration",
            "Integration Tests (requires Ollama)"
        )
        
    elif test_type == "system":
        # Run system tests (slow, requires Ollama)
        success = run_command(
            "python -m pytest tests/ -v -m system --timeout=600",
            "System Tests (slow, requires Ollama)"
        )
        
    elif test_type == "all":
        # Run all tests
        success = run_command(
            "python -m pytest tests/ -v",
            "All Tests"
        )
        
    elif test_type == "fast":
        # Run fast tests only (unit + integration, no slow tests)
        success = run_command(
            "python -m pytest tests/ -v -m 'not slow'",
            "Fast Tests (excludes slow system tests)"
        )
        
    else:
        print(f"❌ Unknown test type: {test_type}")
        print("\nAvailable test types:")
        print("  smoke      - Quick smoke tests (default)")
        print("  unit       - Unit tests only")
        print("  integration- Integration tests (requires Ollama)")
        print("  system     - System tests (slow, requires Ollama)")
        print("  fast       - All tests except slow ones")
        print("  all        - All tests")
        print("\nUsage: python run_tests.py [test_type]")
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. If smoke tests passed, the basic setup is working")
        print("2. Run 'python run_tests.py integration' to test Ollama integration")
        print("3. Run 'python run_tests.py system' for full end-to-end testing")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. For integration/system tests, ensure Ollama is running: ollama serve")
        print("3. Check that required models are available: ollama pull llama3.1:8b")
        return 1

if __name__ == "__main__":
    exit(main()) 