# --spy (Watch Mode) Feature

The `--spy` command enables **real-time clipboard monitoring** with automatic history saving.

## How It Works

When you run `zibi --spy`, it:

1. **Watches your clipboard** - Monitors for any changes in real-time (checks every 0.75 seconds)
2. **Detects changes** - When new content is copied to the clipboard
3. **Displays changes** - Shows a timestamped message with a preview
4. **Saves to history** - Automatically saves each change to zibi's history database

## Basic Usage

```bash
# Start watching the clipboard
zibi --spy

# Output:
# ┌─ Info ─┐
# │ zibi is watching. Press Ctrl+C to stop the surveillance. │
# └─────────┘
# [2026-06-11 17:11:59] Something changed: test content here
# [2026-06-11 17:12:03] Something changed: another piece of text
# ...
```

Press **Ctrl+C** to stop watching.

## Example Workflow

### Terminal 1: Start watching
```bash
zibi --spy
```

### Terminal 2: Copy content multiple times
```bash
echo "First item" | xclip -selection clipboard
echo "Second item" | xclip -selection clipboard
echo "Third item" | xclip -selection clipboard
```

### Result in Terminal 1:
```
[2026-06-11 17:11:59] Something changed: First item
[2026-06-11 17:12:01] Something changed: Second item
[2026-06-11 17:12:03] Something changed: Third item
```

### Then check history (in Terminal 2 or new terminal):
```bash
zibi --log
# Shows all three items in history

zibi --count
# Shows the updated count
```

## Features

✅ **Real-time monitoring** - Detects clipboard changes continuously  
✅ **Automatic saving** - All changes are saved to history  
✅ **Timestamped output** - Shows exact time of each change  
✅ **Content preview** - Displays a preview of the copied content  
✅ **Config-independent** - Saves regardless of `auto_save_history` setting  
✅ **Cycling messages** - Uses the cycling message system for variety  

## Configuration

The `--spy` command respects these settings:

- **max_history_entries** - Maximum number of entries to keep (default: 1000)
- **deduplicate_consecutive** - If enabled, ignores duplicate consecutive copies

It **ignores** the `auto_save_history` setting because spy mode is specifically designed to save everything it detects.

## Use Cases

1. **Capture all copies from a session**
   ```bash
   zibi --spy &  # Start in background
   # ... do your work, copy lots of things ...
   kill %1  # Stop spy
   zibi --log  # View everything you copied
   ```

2. **Monitor what others are copying**
   - Useful for understanding workflow patterns
   - See what content flows through the clipboard

3. **Automatic session logging**
   - Run during work sessions to capture everything
   - Review later in `--log`

4. **Find "lost" content**
   - If you forgot what you copied
   - Spy mode logs everything with timestamps

## Advanced Usage

### Running in background
```bash
# Start spy in background
zibi --spy &

# Do your work...

# Stop when done
pkill -f "zibi --spy"

# View what was captured
zibi --log --limit 20
```

### With deduplication
Edit config to enable/disable consecutive deduplication:
```toml
deduplicate_consecutive = true  # Ignores repeated identical copies
```

### View with timestamps
All spy-captured items show source as "clipboard":
```bash
zibi --log  # Shows source column
```

## Message Cycling

The `--spy` command uses cycling messages:

**Start message variations:**
- "zibi is watching. Press Ctrl+C to stop the surveillance."

**Change detection variations:**
- "[{timestamp}] Something changed: {preview}"

Run multiple times to see different messages.

## Troubleshooting

### No changes detected
- Make sure you're copying to the **system clipboard**
- On Linux, ensure `xclip` is installed: `sudo apt install xclip`
- WSL: Use Windows clipboard tools (clips, wsl-clipboard, etc.)

### Changes not saved
- Check that the database file is writable
- Verify `max_history_entries` hasn't been exceeded
- Check config with: `zibi --config`

### Performance issues
- Reduce the sample time in code (currently 0.75 seconds)
- Run on a less busy system if experiencing slowdowns

## Technical Details

- **Source label**: Clipboard changes are labeled as "clipboard" source
- **Deduplication**: Works even in spy mode (if enabled in config)
- **Database**: Uses the same database as other zibi commands
- **State**: Each change is treated independently (no state tracking needed)

## See Also

- `zibi --log` - View history
- `zibi --count` - Count entries
- `zibi --copy` - Manual copy with auto-save
- `zibi --config` - Configure auto-save and other settings
