# Zibi System-Wide Installation Guide

This guide explains how to install zibi as a system-wide command on Linux/WSL so you can use it from any directory in any shell.

## Quick Start

```bash
# Install zibi system-wide
zibi --init

# Restart your shell or run:
exec bash  # or zsh, or fish

# Now use from anywhere!
cd /tmp && zibi --count
cd / && zibi --log
```

## What `zibi --init` Does

The `--init` command performs a complete installation in 3 steps:

### 1. System-Wide Installation
- **Installs zibi binary** to `/usr/local/bin/zibi` (or `~/.local/bin/zibi` as fallback)
- Creates a wrapper script that can be called from any location
- Makes zibi accessible system-wide in any shell

### 2. Shell Integration
- **Installs hooks** to your shell config files:
  - Bash: `~/.bashrc`
  - Zsh: `~/.zshrc`
  - Fish: `~/.config/fish/conf.d/zibi.fish`
- Provides `zibi_run` function for capturing command output
- Provides `run` alias as shortcut

### 3. Verification
- Checks that `zibi` is accessible from PATH
- Reports if setup needs terminal restart

## Installation Options

### Default Installation
```bash
zibi --init
```
This auto-detects your shell and installs everything.

### Choose Specific Shell
```bash
zibi --init --shell bash
zibi --init --shell zsh
zibi --init --shell fish
```

### Install Only System-Wide (No Shell Hooks)
```bash
zibi --init --no-hooks
```

### Install Only Shell Hooks (No System-Wide)
```bash
zibi --init --no-system
```

## Installation Locations

After `zibi --init`, zibi will be installed in one of these locations (in order of preference):

| Location | Condition |
|----------|-----------|
| `/usr/local/bin/zibi` | If writable (usual on fresh Linux) |
| `/usr/bin/zibi` | If writable (some systems) |
| `~/.local/bin/zibi` | Fallback (always works) |

### PATH Configuration

If zibi installs to `~/.local/bin`, the following will be added to your shell configs:

```bash
# Added by zibi --init
export PATH="$HOME/.local/bin:$PATH"
```

This ensures `~/.local/bin` is searched before other directories.

## After Installation

### Activate in Current Terminal
```bash
# For bash
exec bash

# For zsh
exec zsh

# For fish
exec fish
```

Or simply **close and reopen your terminal**.

### Verify Installation
```bash
# Check if zibi is accessible
which zibi

# Try running a command
zibi --count

# Test from different directories
cd /tmp && zibi --log
cd / && zibi --spy
```

## Permissions

### No Sudo Needed (Recommended)
zibi will automatically use `~/.local/bin` if `/usr/local/bin` is not writable. This works for:
- User-level installations
- Restricted environments
- Windows WSL

### With Sudo
If you want to install to `/usr/local/bin` on a system where you don't have write access:
```bash
sudo zibi --init
```

**Note:** After sudo installation, `zibi --spy` and other features work normally without needing sudo.

## Uninstallation

### Remove Everything
```bash
zibi --uninstall
```

This removes:
- System-wide zibi command
- Shell integration hooks from all shells
- Cache directory (optional)

### Remove Selectively
```bash
# Keep system-wide command, remove shell hooks only
zibi --uninstall --no-system

# Remove system-wide command, keep shell hooks
zibi --uninstall --no-hooks

# Uninstall from specific shell
zibi --uninstall --shell bash
```

### Manual Uninstallation
If `zibi --uninstall` doesn't work, you can manually remove:

1. **System-wide command:**
   ```bash
   rm /usr/local/bin/zibi      # or ~/.local/bin/zibi
   ```

2. **Shell hooks** (remove these sections from config files):
   ```bash
   # Bash (~/.bashrc)
   # Remove section between:
   # === ZIBI START ===
   # === ZIBI END ===

   # Zsh (~/.zshrc)
   # Same as above

   # Fish (~/.config/fish/conf.d/zibi.fish)
   rm ~/.config/fish/conf.d/zibi.fish
   ```

## Troubleshooting

### `zibi: command not found`

**Problem:** After installation, zibi is still not found.

**Solutions:**
1. Restart your terminal
2. Manually source your shell config:
   ```bash
   source ~/.bashrc      # bash
   source ~/.zshrc       # zsh
   exec fish             # fish
   ```
3. Check if zibi is in PATH:
   ```bash
   echo $PATH
   which zibi
   ```
4. Check installation location:
   ```bash
   ls -la /usr/local/bin/zibi        # or ~/.local/bin/zibi
   ```

### Permission Denied During Installation

**Problem:** "Permission denied writing to /usr/local/bin"

**Solutions:**
1. Use `~/.local/bin` (automatic fallback):
   ```bash
   zibi --init  # Will use ~/.local/bin automatically
   ```
2. Use sudo:
   ```bash
   sudo zibi --init
   ```
3. Create `/usr/local/bin` if it doesn't exist:
   ```bash
   sudo mkdir -p /usr/local/bin
   sudo chmod 755 /usr/local/bin
   zibi --init
   ```

### PATH Configuration Issues

**Problem:** `.local/bin` not in PATH even after installation

**Solution:** Check your shell config was updated:
```bash
# Check ~/.bashrc or ~/.zshrc
grep "local/bin" ~/.bashrc

# If not there, add manually:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Shell Hooks Not Working

**Problem:** Output capture (`zibi_run`, `run`) doesn't work

**Solution:** Reinstall shell integration:
```bash
zibi --uninstall --no-system  # Remove old hooks
zibi --init --no-system       # Reinstall hooks
exec bash  # Reload shell
```

## File Locations

After installation, zibi creates/modifies these files:

| File | Purpose |
|------|---------|
| `/usr/local/bin/zibi` or `~/.local/bin/zibi` | System-wide command |
| `~/.bashrc` | Bash configuration (hooks added) |
| `~/.zshrc` | Zsh configuration (hooks added) |
| `~/.config/fish/conf.d/zibi.fish` | Fish configuration (hooks) |
| `~/.cache/zibi/` | Cache directory |
| `~/.cache/zibi/last_output.txt` | Last command output |
| `~/.cache/zibi/.message-state.json` | Message cycling state |

## Shell Integration Features

After installation, you get these additional features:

### `zibi_run` Function
Captures output of any command:
```bash
zibi_run pytest tests/
zibi --snatch  # Retrieve the output
```

### `run` Alias
Shortcut for `zibi_run`:
```bash
run npm test
zibi --snatch
```

### `--spy` Mode
Automatically saves clipboard changes:
```bash
zibi --spy &     # Run in background
# ... copy things with Ctrl+C
# When done: pkill -f "zibi --spy"
```

## Safety Features

The installation is **safe and idempotent**:

- **No duplicates:** Using markers (`=== ZIBI START ===` / `=== ZIBI END ===`), re-running `zibi --init` safely updates without duplication
- **Restore-able:** Can be completely removed with `zibi --uninstall`
- **Non-invasive:** Only modifies shell config files and creates wrapper script
- **User-only:** No system-wide permissions needed (uses `~/.local/bin` as fallback)

## Examples

### Fresh Setup on Linux
```bash
# Install
zibi --init

# Test
exec bash
zibi --count

# Use from anywhere
cd / && zibi --log
cd /tmp && zibi --spy &
```

### Update After Pull
```bash
# Pull latest code
git pull

# Reinstall (safe - won't duplicate)
zibi --init

# Restart shell
exec bash

# Continue using
zibi --copy "updated"
```

### Migrate Between Shells
```bash
# Remove old shell hooks
zibi --uninstall --shell bash --no-system

# Install for new shell
zibi --init --shell zsh --no-system

# Reload
exec zsh
```

### CI/CD Installation
```bash
# Non-interactive installation for automation
zibi --init --shell bash --no-hooks
# System-wide command is now available
# Use in scripts without shell integration
```

## Technical Details

### Wrapper Script
The wrapper script at `/usr/local/bin/zibi` (or `~/.local/bin/zibi`) looks like:
```bash
#!/bin/sh
exec /path/to/python -m zibi.main "$@"
```

This allows `zibi` to be called from anywhere regardless of Python environment.

### Shell Hooks
Shell hooks inject functions into your config that:
1. Capture command output using shell redirection
2. Save it to `~/.cache/zibi/last_output.txt`
3. Allow retrieval with `zibi --snatch`

### Safety Markers
Each shell config has markers to track where zibi was installed:
```bash
# === ZIBI START ===
# ... zibi code here ...
# === ZIBI END ===
```

These prevent duplication and enable safe updates.

## Support

For issues or questions:
- Check troubleshooting section above
- Run `zibi --help` for command options
- Review shell config files for markers
- Check `/usr/local/bin/zibi` or `~/.local/bin/zibi` exists and is executable

## See Also

- **QUICK-SETUP.md** - Quick reference for one-liner setup
- **SHELL-INTEGRATION-GUIDE.md** - Detailed shell integration information
- **SPY-MODE-GUIDE.md** - Using --spy for clipboard monitoring
