#!/usr/bin/env bash
# Test message cycling in zibi

echo "===== Zibi Message Cycling System - Live Demo ====="
echo ""
echo "Testing message cycling for --copy command:"
echo ""

echo "Run 1:"
zibi --copy "hello"
echo ""

echo "Run 2:"
zibi --copy "world"
echo ""

echo "Run 3:"
zibi --copy "test"
echo ""

echo "Run 4 (should cycle back):"
zibi --copy "cycling"
