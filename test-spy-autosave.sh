#!/bin/bash
# Test script for --spy auto-save feature on Linux/WSL

echo "Testing --spy auto-save feature"
echo "================================"
echo ""
echo "1. Checking initial history count:"
zibi --count

echo ""
echo "2. Starting spy mode in background (will run for 5 seconds)..."
echo "3. While it's running, copy some text:"
echo ""
echo "Commands to run in another terminal:"
echo "  echo 'test content 1' | xclip -selection clipboard"
echo "  echo 'test content 2' | xclip -selection clipboard"
echo "  echo 'test content 3' | xclip -selection clipboard"
echo ""

# Start spy in background with a timeout
timeout 10 zibi --spy &
SPY_PID=$!

# Give it time to start
sleep 1

# Simulate clipboard changes using xclip (Linux)
echo "Copying test content 1..."
echo "test content 1" | xclip -selection clipboard
sleep 2

echo "Copying test content 2..."
echo "test content 2" | xclip -selection clipboard
sleep 2

echo "Copying test content 3..."
echo "test content 3" | xclip -selection clipboard
sleep 2

# Kill the spy command
kill $SPY_PID 2>/dev/null
wait $SPY_PID 2>/dev/null

echo ""
echo "4. Checking history after spy (should have new entries):"
zibi --count

echo ""
echo "5. Viewing history:"
zibi --log --limit 5

echo ""
echo "Test complete!"
