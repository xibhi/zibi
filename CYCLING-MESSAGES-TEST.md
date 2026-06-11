# Cycling Messages Test Guide

This document shows how to test all the cycling messages that have been implemented in zibi.

## Success Messages (Cycling Output)

These commands show different messages each time they're executed:

### Copy Command
```bash
echo "test" | zibi --copy
echo "test" | zibi --copy  # Should show different message
echo "test" | zibi --copy  # Should cycle through all 3 messages
```

Expected messages:
- "Snatched. zibi is holding it tight."
- "Locked in. zibi won't let go."
- "Yours. Well, zibi's. Same thing."

### Pin Command
```bash
zibi --pin 1
zibi --pin 1
```

Expected messages:
- "Pinned. zibi will guard this with its life."
- "Locked down. Not even --wipe can touch this one."

### Clear Command
```bash
zibi --clear
```

Expected messages:
- "Clipboard wiped. zibi remembers nothing. Like a goldfish."
- "Gone. Whatever it was, it never existed."

### Fetch Command
```bash
zibi --fetch 1
zibi --fetch 1  # Should cycle
```

Expected messages:
- "Brought back from the dead. You're welcome."
- "Resurrected. Clipboard is alive again."

### Transform Commands
```bash
echo "hello" | zibi --copy
zibi --transform upper
zibi --transform lower
zibi --transform trim
```

These have individual messages that rotate through different variations.

## Error Messages (Cycling Errors)

These commands generate errors with cycling messages:

### QR Error - Invalid URL
```bash
echo "not a url" | zibi --copy
zibi --qr
zibi --qr  # Should show different error message
zibi --qr  # Should cycle
```

Expected error messages:
- "zibi only makes QR codes for links. That's not a link."
- "QR mode is for URLs only. As mentioned in --help, links only."
- "That looks like text, not a URL. zibi refuses to QR-ify it."
- "Did you read --help? QR codes are for links. Not your grocery list."

### Index Out of Range Error
```bash
zibi --fetch 999
zibi --fetch 999
zibi --fetch 999
```

Expected error messages (with dynamic {n} and {max}):
- "Index 999 doesn't exist. zibi only has {max} entries."
- "That entry is gone or never existed. Try --log first."
- "Out of range. zibi checked the whole diary. Nothing at 999."

## Info Messages (Cyan Styled)

These commands show informational messages with cycling:

### Count Command
```bash
zibi --count
zibi --count
```

Expected message:
- "zibi is hoarding {n} entries for you."

### Watch/Spy Command
```bash
zibi --spy
# Wait for clipboard changes
# Press Ctrl+C to stop
```

Expected messages:
- Initial: "zibi is watching. Press Ctrl+C to stop the surveillance."
- On change: "[{timestamp}] Something changed: {preview}"

### Log/History Command
```bash
# When history is empty:
zibi --log

# Expected message:
# "zibi's diary is empty. Nothing copied yet."
```

## Message State Tracking

The system tracks which message was last shown in:
```bash
# Linux/Mac
~/.zibi-messages/.message-state.json

# Or inside the package (when installed)
{python_site-packages}/zibi/.zibi-messages/.message-state.json
```

You can reset the cycling by deleting this file, and messages will start from message 0 again.

## How It Works

1. **Message Files**: Messages are stored in text files with a special format:
   - `success.txt` - Success messages
   - `error.txt` - Error messages

2. **Format**:
   ```
   # --command name
   "First message variant"
   "Second message variant"
   "Third message variant"
   ```

3. **Placeholders**: Messages can include `{placeholder}` for dynamic content:
   - `{n}` - Number or count
   - `{max}` - Maximum value
   - `{preview}` - Text preview
   - `{timestamp}` - Timestamp

4. **State Tracking**: The `.message-state.json` file tracks which message index to show next for each command

## Testing Tips

- Run commands multiple times to see messages cycle
- Check debug output with: `ZIBI_DEBUG=1 zibi --command` (on Linux/Mac)
- Look at `.message-state.json` to see the current cycling state
- Add more messages to success.txt or error.txt to extend cycling options
- Each command can have different numbers of messages

## Adding New Messages

To add new messages:

1. Open `zibi/.zibi-messages/success.txt` or `error.txt`
2. Find the section for your command (e.g., `# --copy`)
3. Add new quoted lines after the command header:
   ```
   # --copy
   "Existing message"
   "New message here"
   "Another new variant"
   ```
4. Reinstall: `pip install -e .`
5. Run the command multiple times to see all variants
