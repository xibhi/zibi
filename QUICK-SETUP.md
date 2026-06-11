# Quick Reference: zibi --init Setup

## One-Line Setup

```bash
zibi --init
```

That's all you need! This will:
- ✅ Auto-detect your shell (bash/zsh/fish)
- ✅ Create the necessary hooks
- ✅ Write to your shell config file (~/.bashrc, ~/.zshrc, or ~/.config/fish/conf.d/zibi.fish)
- ✅ Make zibi accessible globally

## After Installation

### Reload your shell

**Option 1: Restart terminal**
- Close and reopen your terminal window

**Option 2: Reload config**
```bash
source ~/.bashrc    # bash
source ~/.zshrc     # zsh
exec fish          # fish
```

### Test it worked

```bash
# Should show zibi functions
which zibi_run

# Use from any directory
cd /tmp
zibi --count
```

## Usage

### Capture command output

```bash
zibi_run pytest tests/         # Runs pytest, captures output
zibi --snatch                  # Get the output
```

### Short alias

```bash
run npm test                   # Same as zibi_run npm test
```

## What Changed

Your shell config file now has a section like:

```bash
# === ZIBI START ===
# ... zibi hook installation ...
# === ZIBI END ===
```

The markers let you safely run `zibi --init` again if needed.

## Manual Installation

If automatic doesn't work:

```bash
# Bash
zibi --init --shell bash --no-persist >> ~/.bashrc
source ~/.bashrc

# Zsh
zibi --init --shell zsh --no-persist >> ~/.zshrc
source ~/.zshrc

# Fish
mkdir -p ~/.config/fish/conf.d
zibi --init --shell fish --no-persist > ~/.config/fish/conf.d/zibi.fish
```

## Verify Installation

```bash
# Check if hooks were added
cat ~/.bashrc | grep "ZIBI START"
cat ~/.zshrc | grep "ZIBI START"
cat ~/.config/fish/conf.d/zibi.fish | head -5

# Check cache directory was created
ls -la ~/.cache/zibi/
```

## Access from Anywhere

After setup, use zibi from any directory:

```bash
cd /
zibi --log

cd /tmp
zibi --count

cd ~/projects
zibi --spy
```

## Need Help?

```bash
# See all options
zibi --init --shell auto      # Use auto-detected shell
zibi --init --shell bash      # Force bash
zibi --init --shell zsh       # Force zsh
zibi --init --shell fish      # Force fish

# For more details, see:
# SHELL-INTEGRATION-GUIDE.md
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `zibi: command not found` | Run `source ~/.bashrc` or restart terminal |
| Hooks not installed | Check if config file is writable: `ls -la ~/.bashrc` |
| Using wrong shell | Run `zibi --init --shell bash` (specify shell explicitly) |
| Want to uninstall | Edit config file and remove `# === ZIBI START ===` to `# === ZIBI END ===` section |

## Global Access Achievement

✅ **zibi is now accessible from any directory in your system!**

Examples:
```bash
zibi --copy "anything"        # From home
cd /tmp && zibi --fetch 1     # From /tmp
cd ~/src && zibi --log        # From projects
zibi --spy &                  # Run from anywhere
```
