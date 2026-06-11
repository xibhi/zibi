# Testing zibi CLI Without Installing

You can test all zibi commands without installing them. Here are the best methods:

## Quick Start - One-Liners

### Test Help
```powershell
python -c "from zibi.main import main; import sys; sys.argv = ['zibi', '--help']; main()"
```

### Test Count
```powershell
python -c "from zibi.main import main; import sys; sys.argv = ['zibi', '--count']; main()"
```

### Test Stats
```powershell
python -c "from zibi.main import main; import sys; sys.argv = ['zibi', '--stats']; main()"
```

### Test Copy
```powershell
python -c "from zibi.main import main; import sys; sys.argv = ['zibi', '--copy', 'hello world']; main()"
```

### Test Paste
```powershell
python -c "from zibi.main import main; import sys; sys.argv = ['zibi', '--paste']; main()"
```

### Test Log
```powershell
python -c "from zibi.main import main; import sys; sys.argv = ['zibi', '--log']; main()"
```

---

## Better Method - Use Test Scripts

### Run all command tests
```powershell
cd X:\Downloads\zibi
python test_all_commands.py
```

### Run test reference
```powershell
cd X:\Downloads\zibi
python test_without_install.py
```

---

## Testing Confirmation Prompts

### Test --wipe (deny)
```powershell
python -c "from typer.testing import CliRunner; from zibi.main import app; runner = CliRunner(); result = runner.invoke(app, ['@wipe'], input='n\n'); print(result.output)"
```

### Test --clear (deny)
```powershell
python -c "from typer.testing import CliRunner; from zibi.main import app; runner = CliRunner(); result = runner.invoke(app, ['@clear'], input='n\n'); print(result.output)"
```

### Test --kill (deny)
```powershell
python -c "from typer.testing import CliRunner; from zibi.main import app; runner = CliRunner(); result = runner.invoke(app, ['@kill', '1'], input='n\n'); print(result.output)"
```

---

## All Available Commands (@ prefix for internal routing)

| Command | Usage | Notes |
|---------|-------|-------|
| `@help` | Show help | No args needed |
| `@copy` | Copy to clipboard | Pass text or use `--file` |
| `@paste` | Paste from clipboard | No args needed |
| `@snatch` | Copy previous command output | No args needed |
| `@init` | Show hook script | Optional: `--shell bash/zsh/fish` |
| `@log` | Show clipboard history | Optional: `--limit N` |
| `@fetch` | Get history entry by index | Required: index number |
| `@grep` | Search history | Required: search term |
| `@pin` | Pin history entry | Required: index number |
| `@pins` | Show pinned entries | No args needed |
| `@kill` | Delete history entry | Required: index number |
| `@transform` | Transform clipboard | Pass mode: upper, lower, trim, flip, encode, decode, sanitize, humanize, wordcount, lines |
| `@qr` | Generate QR code | No args needed |
| `@yeet` | Share to internet | No args needed |
| `@spy` | Watch clipboard | No args needed (press Ctrl+C to stop) |
| `@clear` | Clear history (keep pins) | No args needed |
| `@wipe` | Delete all history | No args needed |
| `@count` | Count history entries | No args needed |
| `@top` | Get latest clipboard | No args needed |
| `@stats` | Show stats dashboard | No args needed |
| `@config` | Configure settings | No args needed |
| `@build` | Show version info | No args needed |

---

## What's Being Tested

All the new message updates are working:

✅ **--wipe confirm**: "This will burn ALL non-pinned history. {n} entries gone forever. Sure?"
✅ **--clear confirm**: "This will empty the clipboard. Whatever is in there, gone. Sure?"
✅ **--kill confirm**: "Delete entry {n}? '{preview}' — gone forever. Sure?"
✅ **--watch running**: "zibi is watching. Press Ctrl+C to stop the surveillance."
✅ **--watch new content**: "[{timestamp}] Something changed: {preview}"
✅ **--stats header**: "zibi's report on your clipboard addiction:"
✅ **--log empty**: "zibi's diary is empty. Nothing copied yet."
✅ **--count**: "zibi is hoarding {n} entries for you."
