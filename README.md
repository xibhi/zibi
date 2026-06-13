# zibi

[![PyPI version](https://img.shields.io/pypi/v/zibi.svg?color=blue)](https://pypi.org/project//)
[![Python versions](https://img.shields.io/pypi/pyversions/zibi.svg)](https://pypi.org/project//)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/xibhi/zibi/blob/master/LICENSE)

`zibi` is a cute clipboard manager that lives entirely in your terminal. Copy, paste, search, transform, pin, share, and track clipboard history — all without touching a mouse or opening a browser.

---

## Demo

![zibi --help screen](./assets/zibi.gif)

---

## Features

- **Persistent History** — Every copy is saved to a local SQLite database with source tagging (`manual`, `pipe`, `file`, `snatch`).
- **Snatch Previous Command Output** — `--snatch` captures the output of the last terminal command and copies it straight to your clipboard. No selecting, no scrolling.
- **Pinning** — Pin any history entry so it never gets deleted during `--clear`.
- **Transform** — Mutate clipboard content in place. Encode, Decode, Sanitize, Humanize, uppercase, lowercase, flip, trim, and more.
- **Live Watch** — Monitor clipboard changes in real time with timestamps.
- **Share** — Upload clipboard content to a public paste URL and get a shareable link in one command.
- **QR Codes** — Render any URL in your clipboard as a scannable ASCII QR code directly in the terminal. Links only.
- **Pipe-safe** — `--paste` and `--top` output clean stdout with zero decoration so they pipe correctly.

---

## Installation

### From Source (Development)

```bash
# Clone the repo. No, Ctrl+C won't copy this time.
git clone https://github.com/xibhi/zibi.git

# Enter the zibiverse.
cd zibi

# Build a tiny Python apartment.
python3 -m venv venv
source venv/bin/activate

# Feed the dependency gremlins.
pip install --upgrade pip
pip install .

# Your Ctrl+C just got promoted.
zibi --init
zibi --help
```

---

## Shell Hook Setup (--snatch)

`--snatch` is zibi's signature feature. It copies the output of the previous terminal command to your clipboard without selecting anything.

To enable it, add the shell hook to your config:

**zsh / bash**
```bash
echo 'source <(zibi --init)' >> ~/.zshrc
source ~/.zshrc
```

**fish**
```fish
echo 'zibi --init --shell fish | source' >> ~/.config/fish/config.fish
zibi --init --shell fish | source
```

> `--snatch` only captures output from commands run through `zibi-run`. Regular terminal commands are not captured. Run `zibi --init` first to set up the hooks.

---

## Quick Start

```bash
# Copy a string
zibi --copy "hello world"

# Copy a file's contents
zibi --copy --file config.json

# Pipe into zibi
cat README.md | zibi --copy

# Paste to stdout (pipe-safe)
zibi --paste

# Copy last command's output
zibi-run ls -la
zibi --snatch
```

---

## Commands

| Command | Description |
|---|---|
| `zibi --help` | Show the full command list. |
| `zibi --copy "<text>"` | Steal text from your fingers and hold it hostage. |
| `zibi --copy --file <path>` | Steal directly from a file instead. |
| `zibi --copy` (stdin) | Pipe content straight into zibi. |
| `zibi --paste` | Spit out whatever zibi is currently sitting on. |
| `zibi --snatch` | Snitch on the last command you ran via zibi-run. |
| `zibi --init` | Teach your shell to spy for zibi. |
| `zibi --log` | Scroll through zibi's diary of everything you copied. |
| `zibi --log --limit <n>` | Show last N entries. |
| `zibi --fetch <index>` | Resurrect a dead clipboard entry back to life. |
| `zibi --grep <query>` | Dig through the graveyard for something specific. |
| `zibi --pin [index]` | Tell zibi this one is too important to ever forget. |
| `zibi --unpin [index]` | Free an entry from zibi's eternal memory. |
| `zibi --pins` | Show everything zibi has sworn to never forget. |
| `zibi --qr` | Turn your clipboard links into a scannable square of chaos. Links only. |
| `zibi --yeet` | Yeet your clipboard to the internet. Get a link back. |
| `zibi --spy` | Stare at your clipboard like a paranoid security guard. |
| `zibi --kill [index]` | Erase one embarrassing entry from the record. |
| `zibi --clear` | Burn the history down. Pins survive the fire. |
| `zibi --wipe` | Wipe the clipboard clean. Pretend it never happened. |
| `zibi --count` | How many things has zibi hoarded for you? |
| `zibi --top` | What was the last thing you trusted zibi with? |
| `zibi --stats` | Stare at graphs of your clipboard addiction. |
| `zibi --config` | Tell zibi how you want to be treated. It will comply. |
| `zibi --build` | Find out how old this thing is. |

---

### Transform

`zibi --transform <mode>` mutates the current clipboard content in place and copies the result.

| Mode | What it does |
|---|---|
| `upper` | SCREAM YOUR CLIPBOARD AT EVERYONE. |
| `lower` | whisper your clipboard like a coward. |
| `trim` | Shave the whitespace off both ends. |
| `flip` | .sdrawkcab ti daer ot enoemos ecrof |
| `encode` | Encode it so nobody knows what you copied. |
| `decode` | Decode what someone tried to hide from you. |
| `sanitize` | Make it URL-safe and absolutely hideous. |
| `humanize` | Undo the ugly and read it like a human being. |
| `wordcount` | Counts your words. Touches nothing. Just judges. |
| `lines` | Counts your lines. Silent. Watchful. Does not copy. |

---

## How It Works

zibi stores everything locally.

- **Clipboard history** is saved to `~/.local/share/zibi/history.db` (SQLite) every time `--copy` or `--snatch` is used.
- **Pinned entries** are flagged in the database and excluded from `--clear`.
- **Config** is stored at `~/.config/zibi/config.toml` and auto-created with defaults on first run.
- **Shell output capture** for `--snatch` works via a hook that tees command output to `~/.cache/zibi/last_output.txt`. Running `zibi --init` prints the hook script. Sourcing it activates the feature.

`--paste` and `--top` write directly to stdout with no Rich formatting so they are safe to use in pipes and scripts.

## License

This project is licensed under the [MIT License](LICENSE).
