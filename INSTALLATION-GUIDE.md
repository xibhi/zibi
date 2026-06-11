# ✅ Shell Integration Complete - Global Access Achievement

## What's New

The `zibi --init` command has been completely rewritten to **automatically detect your shell and install hooks permanently**, making zibi accessible from anywhere in your system.

## Key Features

### 1️⃣ Auto-Detection
Automatically detects your shell:
- **bash** → adds to `~/.bashrc`
- **zsh** → adds to `~/.zshrc`  
- **fish** → adds to `~/.config/fish/conf.d/zibi.fish`

### 2️⃣ One-Command Installation
```bash
zibi --init
```
That's it! No manual file editing needed.

### 3️⃣ Persistent Configuration
The installation is written to your shell config file, so it persists across terminal restarts.

### 4️⃣ Safe Updates
Running `zibi --init` multiple times is safe - it updates the existing installation using markers:
```
# === ZIBI START ===
# ... configuration ...
# === ZIBI END ===
```

### 5️⃣ Global Accessibility
After installation, use zibi from **any directory** in your system:
```bash
cd /tmp && zibi --count
cd ~/projects && zibi --log  
cd / && zibi --spy
```

## How It Works

### Installation Process

1. **Detects your shell** from `$SHELL` environment variable
2. **Generates shell-specific hooks** for bash, zsh, or fish
3. **Creates necessary directories** (~/.cache/zibi)
4. **Writes to config file** with safety markers
5. **Shows success message** with next steps

### What Gets Installed

Shell functions:
- `zibi_run` - Capture command output
- `run` - Alias for zibi_run

Environment variables:
- `ZIBI_LAST_OUTPUT` - Path to last captured output
- `ZIBI_CACHE_DIR` - Cache directory location

## Usage

### Basic Setup
```bash
# Automatic installation
zibi --init

# Reload shell config
source ~/.bashrc  # bash
source ~/.zshrc   # zsh
exec fish        # fish
```

### Manual Installation (if needed)
```bash
# Just print the script without installing
zibi --init --no-persist

# Or install specific shell
zibi --init --shell bash
zibi --init --shell zsh
zibi --init --shell fish
```

### Verify Installation
```bash
# Check if installed
which zibi_run

# See installation markers
cat ~/.bashrc | grep "ZIBI START"

# Check cache directory
ls -la ~/.cache/zibi/
```

## Usage Examples

### Capture & Retrieve
```bash
# Capture output of any command
zibi_run pytest tests/
zibi_run npm test
zibi_run python script.py

# Later, retrieve the output
zibi --snatch
```

### Use Anywhere
```bash
# From home
cd ~ && zibi --copy "text"

# From /tmp
cd /tmp && zibi --fetch 1

# From deep project directories
cd ~/projects/app/src/components && zibi --log

# Watch clipboard from anywhere
cd / && zibi --spy
```

### Alias Usage
```bash
run python test.py          # Captured by zibi
run cargo build --release   # Captured by zibi
```

## Files Modified

### Core Changes
- **zibi/hooks.py** - Added `install_to_shell()` function
- **zibi/main.py** - Enhanced `@app.command("@init")` decorator
- **zibi/.zibi-messages/success.txt** - Added more init message variants

### Documentation Added
- **SHELL-INTEGRATION-GUIDE.md** - Comprehensive guide (400+ lines)
- **QUICK-SETUP.md** - Quick reference
- **INSTALLATION-GUIDE.md** - (This file)

## Architecture

### Shell Config File Handling

The system handles three different shell types:

| Shell | Config File | Method |
|-------|------------|--------|
| Bash | ~/.bashrc | Append with markers |
| Zsh | ~/.zshrc | Append with markers |
| Fish | ~/.config/fish/conf.d/zibi.fish | Append with markers |

### Safety Mechanism

Installation markers prevent duplication:
```bash
# === ZIBI START ===
# Previous installation is removed and replaced
# === ZIBI END ===
```

This allows safe re-runs of `zibi --init`.

## Installation Scenarios

### Scenario 1: Bash User
```bash
$ echo $SHELL
/bin/bash

$ zibi --init
# Installs to ~/.bashrc
# Detected shell: bash

$ source ~/.bashrc
$ zibi --count
# Now works from anywhere
```

### Scenario 2: Zsh User
```bash
$ echo $SHELL
/bin/zsh

$ zibi --init
# Installs to ~/.zshrc
# Detected shell: zsh

$ source ~/.zshrc
$ zibi --log
# Now works from anywhere
```

### Scenario 3: Fish User
```bash
$ echo $SHELL
/usr/bin/fish

$ zibi --init
# Installs to ~/.config/fish/conf.d/zibi.fish
# Detected shell: fish

$ exec fish
$ zibi --spy
# Now works from anywhere
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Run `source ~/.bashrc` (bash) or `source ~/.zshrc` (zsh) or restart terminal |
| Wrong shell detected | Use `zibi --init --shell bash` to force a specific shell |
| Permission denied | Check file permissions: `chmod 644 ~/.bashrc` |
| Hooks not written | Ensure config file parent directory exists and is writable |
| Multiple installations | Run `zibi --init` again to update - markers prevent duplicates |

## Verification Steps

```bash
# 1. Check environment
echo $SHELL

# 2. Run installation
zibi --init

# 3. Reload configuration
source ~/.bashrc  # or appropriate shell

# 4. Test the hooks
which zibi_run
echo $ZIBI_LAST_OUTPUT

# 5. Use from any directory
cd /tmp
zibi --count

# 6. Check cache
ls -la ~/.cache/zibi/
```

## Uninstallation

If you want to remove zibi integration:

1. Edit your shell config file
2. Find the section marked with `# === ZIBI START ===` to `# === ZIBI END ===`
3. Delete those lines
4. Save and reload: `source ~/.bashrc` (or equivalent)

## Advanced Features

### Re-installation
```bash
# Safe to run multiple times
zibi --init    # First time
zibi --init    # Second time (updates existing)
zibi --init    # Third time (still works)
```

### Manual Installation
```bash
# If automatic installation fails
zibi --init --no-persist | tee -a ~/.bashrc
```

### Environment Variables
After installation, these are available:
```bash
$ZIBI_LAST_OUTPUT      # Where last output is stored
$ZIBI_CACHE_DIR        # Cache directory path
```

## Performance Impact

- ⚡ Minimal - Only adds a few shell functions
- 📦 No dependencies - Pure shell code
- 💾 Small - < 1KB of shell code
- ⏱️ Fast - No noticeable impact on shell startup

## Security Notes

1. **File Permissions** - Config files are created with standard permissions
2. **Cache Directory** - Private cache in user's home directory
3. **No Root Required** - Everything installs to user's home directory
4. **Environment Variables** - Only `ZIBI_LAST_OUTPUT` is added

## Integration with Other Tools

After `zibi --init`, you can combine with other tools:

```bash
# Pipe to grep
zibi_run pytest | grep PASSED

# Chain commands
zibi_run npm test && zibi --snatch

# Background execution
zibi_run long_task &
```

## Next Steps

1. **Run setup**: `zibi --init`
2. **Reload shell**: `source ~/.bashrc` (or restart terminal)
3. **Test**: `cd /tmp && zibi --count`
4. **Start using**: `zibi_run <command>` to capture outputs
5. **Explore**: `zibi --help` to see all commands

## See Also

- **QUICK-SETUP.md** - Quick start guide
- **SHELL-INTEGRATION-GUIDE.md** - Detailed integration guide
- **SPY-MODE-GUIDE.md** - Watch mode documentation
- **CYCLING-MESSAGES-TEST.md** - Message testing guide

---

**Result:** zibi is now globally accessible from any directory in your system! 🚀
