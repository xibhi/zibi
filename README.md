# zibi

[![PyPI version](https://img.shields.io/pypi/v/zibi.svg?color=blue)](https://pypi.org/project/zibi/)
[![Python versions](https://img.shields.io/pypi/pyversions/zibi.svg)](https://pypi.org/project/zibi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)


`zibi` is a cute clipboard manager that lives entirely in your terminal. Copy, paste, search, transform, pin, share, and track clipboard history — all without touching a mouse or opening a browser.

---

## Demo

![zibi @help screen](./assets/zibi-help.png)

---

## Features

- **Persistent History**: Every copy is saved to a local SQLite database with source tagging (`manual`, `pipe`, `file`, `copyp`).
- **Copy Previous Command Output**: `@copyp` captures the output of the last terminal command and copies it straight to your clipboard — no selecting, no scrolling.
- **Pinning**: Pin any history entry so it never gets deleted during auto-pruning.
- **Transforms**: Mutate clipboard content in place — base64, URL encode/decode, uppercase, reverse, trim, and more.
- **Live Watch**: Monitor clipboard changes in real time with timestamps.
- **Share**: Upload clipboard content to a public paste URL and get a shareable link in one command.
- **QR Codes**: Render current clipboard as a scannable ASCII QR code directly in the terminal.
- **Pipe-safe**: `@paste` and `@latest` output clean stdout with zero decoration so they pipe correctly.

---

## Installation

### From Source (Development)

```
git clone https://github.com/krreeshhh/zibi.git
cd zibi/
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install .
```

---

## Shell Hook Setup (`@copyp`)

`@copyp` is zibi's signature feature. It copies the output of the previous terminal command to your clipboard without you having to select anything.

To enable it, add the shell hook to your config:

**zsh / bash**
```bash
echo 'source <(zibi @install-hooks)' >> ~/.zshrc
source ~/.zshrc
```

**fish**
```fish
echo 'zibi @install-hooks --shell fish | source' >> ~/.config/fish/config.fish
zibi @install-hooks --shell fish | source
```

---

## Quick Start

```bash
# Copy a string
zibi @copy "hello world"

# Copy a file's contents
zibi @copy --file README.md

# Pipe into zibi
cat README.md | zibi @copy

# Paste to stdout (pipe-safe)
zibi @paste

# Copy last command's output
zibi @copyp

# View history
zibi @history

# Recall entry number 3 back to clipboard
zibi @recall 3

# Transform clipboard to base64
zibi @transform base64

# Share clipboard as a paste link
zibi @share

# Render clipboard as a QR code
zibi @qr
```

---

## Command Reference

### Clipboard

| Command | Description |
|---|---|
| `zibi @copy <text>` | Copy a string to clipboard and save to history. |
| `zibi @copy --file <path>` | Copy a file's contents to clipboard. |
| `zibi @copy` (stdin) | Read from stdin and copy. |
| `zibi @paste` | Print current clipboard to stdout. Clean, pipe-safe. |
| `zibi @copyp` | Copy the last captured terminal command output. Requires shell hook. |
| `zibi @clear` | Clear the live clipboard and delete non-pinned history after confirmation. |

---

### History

| Command | Description |
|---|---|
| `zibi @history` | Show last 20 clipboard entries. |
| `zibi @history --limit <n>` | Show last N entries. |
| `zibi @pin <index>` | Pin a history entry so it survives pruning and `@clear`. |
| `zibi @pins` | List all pinned entries. |
| `zibi @recall <index>` | Copy a history entry back to clipboard by index. |
| `zibi @delete <index>` | Delete a single history entry by index. |
| `zibi @search <query>` | Full-text search across clipboard history. |
| `zibi @latest` | Print the most recent history entry. Clean, pipe-safe. |
| `zibi @count` | Print total number of saved history entries. |
| `zibi @wipe` | Clear the live clipboard and delete all history, including pins, after confirmation. |

---

### Transform

`zibi @transform <mode>` mutates the current clipboard content in place and copies the result, except for the read-only `lines` and `wordcount` modes.

| Mode | What it does |
|---|---|
| `upper` | ALL CAPS |
| `lower` | all lowercase |
| `trim` | Strip leading/trailing whitespace |
| `reverse` | Reverse the string |
| `base64` | Base64 encode |
| `unbase64` | Base64 decode |
| `urlencode` | URL encode |
| `urldecode` | URL decode |
| `lines` | Print line count without modifying the clipboard |
| `wordcount` | Print word count without modifying the clipboard |

---

### Utilities

| Command | Description |
|---|---|
| `zibi @qr` | Render clipboard as an ASCII QR code in the terminal. |
| `zibi @share` | Upload using the configured `termbin` or `paste.rs` service. |
| `zibi @watch` | Monitor clipboard in real time. Prints a new line on every change. |
| `zibi @stats` | Dashboard showing total entries, top words, busiest day, source breakdown. |

---

### Misc

| Command | Description |
|---|---|
| `zibi @config` | Interactive setup for history limits, deduplication, and share service. |
| `zibi @install-hooks` | Print shell integration script for `@copyp`. Supports `--shell fish`. |
| `zibi @version` | Print zibi version and Python version. |
| `zibi @help` | Show the full command list. |

---

## How It Works

zibi stores everything locally.

- **Clipboard history** is saved to `~/.local/share/zibi/history.db` (SQLite) every time `@copy` or `@copyp` is used.
- **Pinned entries** are flagged in the database and excluded from all destructive operations.
- **Config** is stored at `~/.config/zibi/config.toml` and auto-created with sensible defaults on first run.
- **Shell output capture** for `@copyp` works via a hook that tees command output to `~/.cache/zibi/last_output.txt`. Running `zibi @install-hooks` prints the hook script; sourcing it activates the feature.

`@paste` writes the live clipboard and `@latest` reads the newest history entry. Both write directly to stdout with no Rich formatting so they are safe to use in pipes and scripts.

---
