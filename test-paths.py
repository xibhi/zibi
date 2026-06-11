#!/usr/bin/env python3
"""Test if message manager can find files"""
from pathlib import Path
import sys

# Simulate what happens when message_manager.py runs
mm_file = Path('/mnt/x/Develop/Projects/Passion/zibi/zibi/message_manager.py')
messages_dir = mm_file.parent.parent / ".zibi-messages"
success_file = messages_dir / "success.txt"

print("Path Analysis:")
print(f"message_manager.py: {mm_file}")
print(f"Parent: {mm_file.parent}")
print(f"Parent.parent: {mm_file.parent.parent}")
print(f"Computed .zibi-messages: {messages_dir}")
print(f"Computed success.txt: {success_file}")
print()

print("File existence:")
print(f"message_manager.py exists: {mm_file.exists()}")
print(f".zibi-messages exists: {messages_dir.exists()}")
print(f"success.txt exists: {success_file.exists()}")
print()

if success_file.exists():
    print("Reading first 5 lines of success.txt:")
    with open(success_file) as f:
        for i, line in enumerate(f):
            if i < 5:
                print(f"  {line.rstrip()}")
print()

# Now test the actual parsing
print("Testing message parsing:")
sys.path.insert(0, str(Path('/mnt/x/Develop/Projects/Passion/zibi')))

from zibi.message_manager import _parse_messages_file

if success_file.exists():
    messages = _parse_messages_file(success_file)
    print(f"Parsed messages: {list(messages.keys())}")
    if "--copy" in messages:
        print(f"--copy messages: {messages['--copy']}")
