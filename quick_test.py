#!/usr/bin/env python
"""
Quickest way to test individual commands without installing zibi
Just run: python quick_test.py
"""

import sys
import io
from typer.testing import CliRunner
from zibi.main import app

# Windows encoding fix
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

runner = CliRunner()

def test(name, cmd, args=None, input_text=None):
    """Test a single command"""
    args = args or []
    internal_cmd = cmd.replace("--", "@")
    result = runner.invoke(app, [internal_cmd] + args, input=input_text)
    
    print(f"\n{'='*70}")
    print(f"TEST: zibi {cmd}")
    print(f"Exit Code: {result.exit_code} {'✓' if result.exit_code == 0 else '✗'}")
    print(f"{'='*70}")
    # Show first 400 chars
    output = result.output[:400]
    print(output)
    if len(result.output) > 400:
        print("...[output truncated]")
    return result.exit_code == 0

# Run the most important tests
print("\n" + "🧪 TESTING ZIBI CLI WITHOUT INSTALLING".center(70))
print("="*70)

tests_passed = 0
tests_total = 0

# Test 1: Help
tests_total += 1
if test("Help", "--help"):
    tests_passed += 1

# Test 2: Count (new message)
tests_total += 1
if test("Count", "--count"):
    tests_passed += 1

# Test 3: Stats (new header)
tests_total += 1
if test("Stats", "--stats"):
    tests_passed += 1

# Test 4: Wipe confirmation (new message)
tests_total += 1
if test("Wipe (cancel)", "--wipe", input_text="n\n"):
    tests_passed += 1

# Test 5: Clear confirmation (new message)
tests_total += 1
if test("Clear (cancel)", "--clear", input_text="n\n"):
    tests_passed += 1

# Test 6: Log
tests_total += 1
if test("Log", "--log"):
    tests_passed += 1

# Test 7: Build
tests_total += 1
if test("Build", "--build"):
    tests_passed += 1

# Summary
print(f"\n{'='*70}")
print(f"✓ Tests Passed: {tests_passed}/{tests_total}".center(70))
print(f"{'='*70}\n")
