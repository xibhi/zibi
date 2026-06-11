from __future__ import annotations

import platform
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from . import __version__
from .config import CONFIG_PATH, Config, load_config, save_config
from .db import (
    add_history,
    delete_history_entry,
    count_history,
    get_entry_by_index,
    latest_entry,
    list_history,
    search_history,
    set_pinned,
    stats as db_stats,
    wipe_all,
    wipe_unpinned,
)
from .hooks import LAST_OUTPUT_PATH, detect_shell, ensure_cache, hook_script, install_to_shell, install_system_wide, uninstall_system_wide, uninstall_shell_hooks, verify_installation
from .utils import (
    ZibiError,
    console,
    err_console,
    preview,
    print_error,
    print_info,
    print_success,
    print_warning,
    read_clipboard,
    read_text_file,
    render_qr_ascii,
    share_text,
    top_words,
    transform_text,
    write_clipboard,
)


app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": []},
    no_args_is_help=False,
    rich_markup_mode="rich",
)


SOURCES = {"manual", "file", "pipe", "copyp", "transform", "share"}
TRANSFORM_MODES = [
    ("upper", "SCREAM YOUR CLIPBOARD AT EVERYONE."),
    ("lower", "whisper your clipboard like a coward."),
    ("trim", "Shave the whitespace off both ends."),
    ("reverse", ".sdrawkcab ti daer ot enoemos ecrof"),
    ("base64", "Encode it so nobody knows what you copied."),
    ("unbase64", "Decode what someone tried to hide from you."),
    ("urlencode", "Make it URL-safe and absolutely hideous."),
    ("urldecode", "Undo the ugly and read it like a human being."),
    ("wordcount", "Counts your words. Touches nothing. Just judges."),
    ("lines", "Counts your lines. Silent. Watchful. Does not copy."),
]
WEEKDAYS = {
    "0": "Sunday",
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
}


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """zibi uses --commands. Start with: zibi --help"""
    ensure_cache()
    load_config()
    if ctx.invoked_subcommand is None:
        show_help()
        raise typer.Exit()


def _save_if_enabled(content: str, source: str) -> None:
    cfg = load_config()
    if cfg.auto_save_history:
        add_history(
            content,
            source,
            max_entries=cfg.max_history_entries,
            deduplicate_consecutive=cfg.deduplicate_consecutive,
        )


def _run(action) -> None:
    try:
        action()
    except ZibiError as exc:
        print_error(str(exc), command=exc.command, replacements=exc.replacements)
        raise typer.Exit(1) from exc
    except KeyboardInterrupt:
        print_warning("Interrupted.")
        raise typer.Exit(130) from None
    except Exception as exc:
        print_error(str(exc) or exc.__class__.__name__)
        raise typer.Exit(1) from exc


def _history_table(entries, *, title: str = "Clipboard History", enumerate_from_latest: bool = True) -> Table:
    table = Table(title=title, box=box.SIMPLE_HEAVY, header_style="bold cyan")
    table.add_column("Index", style="bold", justify="right")
    table.add_column("Preview", overflow="fold")
    table.add_column("Source", style="magenta")
    table.add_column("Timestamp", style="dim")
    all_entries = list_history()
    index_by_id = {entry.id: idx for idx, entry in enumerate(all_entries, start=1)}
    for local_idx, entry in enumerate(entries, start=1):
        idx = index_by_id.get(entry.id, local_idx) if enumerate_from_latest else local_idx
        pin = "ðŸ“Œ " if entry.pinned else ""
        table.add_row(str(idx), pin + preview(entry.content, 60), entry.source, entry.created_at)
    return table


def _valid_range_message() -> str:
    total = count_history()
    if total == 0:
        return "History is empty."
    return f"Index out of range. Valid range: 1-{total}."


def _copyp_missing_message() -> str:
     if detect_shell() == "fish":
         return (
             "No previous command output found.\n"
             "Run commands through: zibi-run <command>\n"
             "Install fish hook with: zibi --init --shell fish > ~/.config/fish/conf.d/zibi.fish"
         )
     return (
         "No previous command output found.\n"
         "Run commands through: zibi-run <command>\n"
         "Enable hooks with: source <(zibi --init)"
     )


def _transform_modes_panel() -> Panel:
    modes = Text("  Â·  ".join(mode for mode, _ in TRANSFORM_MODES), style="bold magenta")
    return Panel(
        Align.center(modes),
        title="[bold magenta]Transform Modes",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def _help_command_table() -> Table:
    table = Table(
        box=box.SIMPLE,
        expand=True,
        header_style="bold magenta",
        show_lines=False,
        pad_edge=False,
    )
    table.add_column("Command", style="bold magenta", no_wrap=True)
    table.add_column("Description", style="white")
    rows = [
         ("--copy", "Steal text from your fingers and hold it hostage."),
         ("--paste", "Spit out whatever zibi is currently sitting on."),
         ("--copyp", "Snitch on the last command you ran via zibi-run."),
        ("--install-hooks", "Teach your shell to spy for zibi."),
        ("--history", "Scroll through zibi's diary of everything you copied."),
        ("--recall", "Resurrect a dead clipboard entry back to life."),
        ("--search", "Dig through the graveyard for something specific."),
        ("--pin", "Tell zibi this one is too important to ever forget."),
        ("--delete", "Erase one embarrassing entry from the record."),
        ("--pins", "Show everything zibi has sworn to never forget."),
        ("--qr", "Turn your clipboard into a scannable square of chaos."),
        ("--share", "Yeet your clipboard to the internet. Get a link back."),
        ("--watch", "Stare at your clipboard like a paranoid security guard."),
        ("--clear", "Burn the history down. Pins survive the fire."),
        ("--wipe", "Wipe the clipboard clean. Pretend it never happened."),
        ("--count", "How many things has zibi hoarded for you? Find out."),
        ("--latest", "What was the last thing you trusted zibi with?"),
        ("--stats", "Stare at graphs of your clipboard addiction."),
        ("--config", "Tell zibi how you want to be treated. It will comply."),
        ("--version", "Find out how old this thing is."),
        ("--uninstall", "Kills zibi from your system completely."),
    ]
    for command, description in rows:
        table.add_row(command, description)
    return table


def show_help() -> None:
    # ASCII-safe logo for Windows compatibility (Unicode blocks don't work on Windows)
    logo_text = """          ███  █████      ███ 
         ░░░  ░░███      ░░░  
 █████████ ███ ░███████  ████ 
░█░░░░███ ░░██ ░███░░███░███ 
░   ███░   ░███ ░███ ░███ ░███ 
  ███░   █ ░███ ░███ ░███ ░███ 
 █████████ █████ ████████ █████
░░░░░░░░░ ░░░░░ ░░░░░░░░  ░░░░░ """
    
    console.print(logo_text)
    console.print()
    console.print("Your clipboard's terminal slave.", style="italic yellow")
    console.print()
    console.print("Options:", style="bold cyan")
    console.print("  --help  Show this message.")
    console.print()
    console.print("Commands:", style="bold cyan")
    
    commands = [
        ("--copy", "Steal text from your fingers and hold it hostage."),
        ("  --file", "Steal directly from a file instead."),
        ("--paste", "Spit out whatever zibi is currently sitting on."),
        ("--snatch", "Snitch on the last command you ran via zibi-run."),
        ("--init", "Teach your shell to spy for zibi."),
        ("--uninstall", "Kills zibi from your system completely."),
        ("--log", "Scroll through zibi's diary of everything you copied."),
        ("--fetch <index>", "Resurrect a dead clipboard entry back to life."),
        ("--grep", "Dig through the graveyard for something specific."),
        ("--pin <index>", "Tell zibi this one is too important to ever forget."),
        ("--pins", "Show everything zibi has sworn to never forget."),
        ("--qr", "Turn your clipboard links into a scannable square of chaos."),
        ("--yeet", "Yeet your clipboard to the internet. Get a link back."),
        ("--spy", "Stare at your clipboard like a paranoid security guard."),
        ("--kill <index>", "Erase one embarrassing entry from the record."),
        ("--clear", "Burn the history down. Pins survive the fire."),
        ("--wipe", "Wipe the clipboard clean. Pretend it never happened."),
        ("--count", "How many things has zibi hoarded for you? Find out."),
        ("--top", "What was the last thing you trusted zibi with?"),
        ("--transform", "Perform dark magic on whatever is in your clipboard."),
        ("--stats", "Stare at graphs of your clipboard addiction."),
        ("--config", "Tell zibi how you want to be treated. It will comply."),
        ("--build", "Find out how old this thing is."),
    ]
    
    for cmd, desc in commands:
        console.print(f"  {cmd:<18} {desc}")
    
    console.print()
    console.print("Transform modes:", style="bold cyan")
    
    # Update TRANSFORM_MODES to match new names
    transform_modes = [
        ("upper", "SCREAM YOUR CLIPBOARD AT EVERYONE."),
        ("lower", "whisper your clipboard like a coward."),
        ("trim", "Shave the whitespace off both ends."),
        ("flip", ".sdrawkcab ti daer ot enoemos ecrof"),
        ("encode", "Encode it so nobody knows what you copied."),
        ("decode", "Decode what someone tried to hide from you."),
        ("sanitize", "Make it URL-safe and absolutely hideous."),
        ("humanize", "Undo the ugly and read it like a human being."),
        ("wordcount", "Counts your words. Touches nothing. Just judges."),
        ("lines", "Counts your lines. Silent. Watchful. Does not copy."),
    ]
    
    for mode, desc in transform_modes:
        console.print(f"    {mode:<12} {desc}")
    
    console.print()
    console.print("Product by Sibhi.")


@app.command("@help")
def help_command() -> None:
    show_help()


@app.command("@copy")
def copy_command(
    text: Optional[list[str]] = typer.Argument(None),
    file_path: Optional[Path] = typer.Option(
        None,
        "--file",
        metavar="PATH",
        help="Read clipboard content from a file.",
    ),
) -> None:
    def action() -> None:
        # BUG FIX: handle --file, direct text, and stdin as distinct copy sources.
        if file_path is not None:
            content = read_text_file(file_path)
            source = "file"
        elif text:
            content = " ".join(text)
            source = "manual"
        elif not sys.stdin.isatty():
            content = sys.stdin.read()
            source = "pipe"
        else:
            raise ZibiError("Nothing to copy. Provide text, use --file, or pipe content into zibi --copy.", command="--copy no input given")
        write_clipboard(content)
        _save_if_enabled(content, source)
        default_msg = f"Copied {len(content)} chars from {source}. Preview: \"{preview(content)}\""
        print_success(default_msg, command="--copy")

    _run(action)


@app.command("@paste")
def paste_command() -> None:
    try:
        sys.stdout.write(read_clipboard())
    except ZibiError:
        raise typer.Exit(1) from None


@app.command("@snatch")
def copyp_command() -> None:
    def action() -> None:
        ensure_cache()
        if not LAST_OUTPUT_PATH.exists() or LAST_OUTPUT_PATH.stat().st_size == 0:
            print_warning(_copyp_missing_message())
            return
        content = LAST_OUTPUT_PATH.read_text(encoding="utf-8", errors="replace")
        if content == "":
            print_warning(_copyp_missing_message())
            return
        write_clipboard(content)
        _save_if_enabled(content, "copyp")
        console.print(f"[bold green]Copied output of previous command[/] ({len(content)} chars)")
        console.print(f'Preview: "{preview(content)}"')

    _run(action)


@app.command("@init")
def install_hooks_command(
    shell: str = typer.Option(
        "auto",
        "--shell",
        help="Shell syntax to install for: auto, bash, zsh, or fish.",
    ),
    system: bool = typer.Option(
        True,
        "--system/--no-system",
        help="Install zibi as system-wide command (default: yes)",
    ),
    shell_hooks: bool = typer.Option(
        True,
        "--hooks/--no-hooks",
        help="Install shell hooks for output capture (default: yes)",
    ),
) -> None:
    """Complete zibi installation for system-wide access.
    
    This command performs a complete installation:
    1. Installs zibi as a system-wide command (/usr/local/bin/zibi or ~/.local/bin/zibi)
    2. Installs shell integration hooks for your shell (bash/zsh/fish)
    3. Makes zibi accessible from anywhere, any shell, any time
    
    After installation:
    - Open a new terminal, or
    - Run: exec bash (or zsh/fish)
    
    Then use zibi from any directory:
        zibi --copy "text"
        zibi --log
        zibi --spy
        cd /tmp && zibi --count
    """
    if shell not in {"auto", "bash", "zsh", "fish"}:
        print_error("Shell must be one of: auto, bash, zsh, fish.")
        raise typer.Exit(1)
    
    ensure_cache()
    
    results = []
    errors = []
    
    # Step 1: Install system-wide command
    if system:
        console.print("[bold cyan]Installing zibi as system-wide command...[/]")
        success, message = install_system_wide()
        if success:
            results.append(message)
            console.print(f"[green]{message}[/]")
        else:
            errors.append(message)
            console.print(f"[yellow]{message}[/]")
    
    # Step 2: Install shell hooks
    if shell_hooks:
        console.print("[bold cyan]Installing shell integration hooks...[/]")
        success, message = install_to_shell(shell)
        if success:
            results.append(message)
            console.print(f"[green]{message}[/]")
        else:
            errors.append(message)
            console.print(f"[yellow]{message}[/]")
    
    # Step 3: Verify installation
    console.print("[bold cyan]Verifying installation...[/]")
    verify_success, verify_msg = verify_installation()
    if verify_success:
        results.append(verify_msg)
        console.print(f"[green]{verify_msg}[/]")
    else:
        # Verification failed but installation might still work after shell restart
        console.print(f"[yellow]{verify_msg}[/]")
    
    # Final status
    if results:
        detected_shell = detect_shell() if shell == "auto" else shell
        summary = "\n".join(results)
        print_success(
            f"{summary}\n\n"
            f"✓ Installation complete!\n"
            f"Shell: {detected_shell}\n\n"
            f"To activate now, run one of:\n"
            f"  exec {detected_shell}\n"
            f"  source ~/.bashrc          # bash\n"
            f"  source ~/.zshrc           # zsh\n"
            f"  exec fish                 # fish\n\n"
            f"Or simply open a new terminal!\n\n"
            f"Then use zibi from anywhere:\n"
             f"  zibi --count\n"
             f"  zibi-run pytest tests/\n"
             f"  zibi --snatch",
            command="--init"
        )
        
        if errors:
            console.print("\n[yellow]Warnings:[/]")
            for error in errors:
                console.print(f"[yellow]⚠ {error}[/]")
    else:
        print_error("Installation failed. Check messages above.")
        raise typer.Exit(1)


@app.command("@uninstall")
def uninstall_command(
    shell: str = typer.Option(
        "auto",
        "--shell",
        help="Shell to uninstall from: auto, bash, zsh, or fish.",
    ),
    system: bool = typer.Option(
        True,
        "--system/--no-system",
        help="Remove system-wide command (default: yes)",
    ),
    shell_hooks: bool = typer.Option(
        True,
        "--hooks/--no-hooks",
        help="Remove shell hooks (default: yes)",
    ),
) -> None:
    """Uninstall zibi from your system.
    
    This command removes:
    1. The system-wide zibi command
    2. Shell integration hooks from bash/zsh/fish configs
    
    You can selectively remove components with --system/--no-system and --hooks/--no-hooks.
    
    Example:
        zibi --uninstall              # Remove everything
        zibi --uninstall --no-system  # Keep command, remove hooks only
    """
    if shell not in {"auto", "bash", "zsh", "fish"}:
        print_error("Shell must be one of: auto, bash, zsh, fish.")
        raise typer.Exit(1)
    
    results = []
    errors = []
    
    # Step 1: Remove system-wide command
    if system:
        console.print("[bold cyan]Removing system-wide zibi command...[/]")
        success, message = uninstall_system_wide()
        if success:
            results.append(message)
            console.print(f"[green]{message}[/]")
        else:
            errors.append(message)
            console.print(f"[yellow]{message}[/]")
    
    # Step 2: Remove shell hooks
    if shell_hooks:
        console.print("[bold cyan]Removing shell integration hooks...[/]")
        success, message = uninstall_shell_hooks(shell)
        if success:
            results.append(message)
            console.print(f"[green]{message}[/]")
        else:
            errors.append(message)
            console.print(f"[yellow]{message}[/]")
    
    # Final status
    if results:
        summary = "\n".join(results)
        print_info(
            f"{summary}\n\n"
            f"✓ Uninstallation complete!\n"
            f"zibi has been removed from your system.",
            command="--uninstall"
        )
        
        if errors:
            console.print("\n[yellow]Warnings:[/]")
            for error in errors:
                console.print(f"[yellow]⚠ {error}[/]")
    else:
        console.print("[yellow]Nothing to uninstall.[/]")



def history_command(limit: int = typer.Option(20, "--limit", min=1, help="Number of entries to show.")) -> None:
    entries = list_history(limit)
    if not entries:
        print_info("zibi's diary is empty. Nothing copied yet.", command="--log empty state")
        return
    console.print(_history_table(entries))


@app.command("@fetch")
def recall_command(index: int) -> None:
    def action() -> None:
        result = get_entry_by_index(index)
        if result is None:
            total = count_history()
            raise ZibiError(
                _valid_range_message(),
                command="--fetch / recall index out of range",
                replacements={"n": index, "max": total}
            )
        _, entry = result
        write_clipboard(entry.content)
        console.print(f"[bold green]Recalled history entry {index}.[/]")
        console.print(f'Preview: "{preview(entry.content)}"')

    _run(action)


@app.command("@grep")
def search_command(query: str) -> None:
    entries = search_history(query)
    if not entries:
        print_warning(f'No history entries matched "{query}".')
        return
    console.print(_history_table(entries, title=f'Search Results for "{query}"'))


@app.command("@pin")
def pin_command(index: int) -> None:
    def action() -> None:
        result = get_entry_by_index(index)
        if result is None:
            total = count_history()
            raise ZibiError(
                _valid_range_message(),
                command="--pin index out of range",
                replacements={"n": index, "max": total}
            )
        _, entry = result
        set_pinned(entry.id, True)
        default_msg = f'Pinned entry {index}. Preview: "{preview(entry.content)}"'
        print_success(default_msg, command="--pin")

    _run(action)


@app.command("@kill")
def delete_command(index: int) -> None:
    def action() -> None:
        result = get_entry_by_index(index)
        if result is None:
            total = count_history()
            raise ZibiError(
                _valid_range_message(),
                command="--kill / delete index out of range",
                replacements={"n": index, "max": total}
            )
        _, entry = result
        if not Confirm.ask(
            f"Delete entry {index}? '{preview(entry.content)}' — gone forever. Sure?",
            default=False,
        ):
            print_warning("Entry was not deleted.")
            return
        delete_history_entry(entry.id)
        print_success(f"Deleted entry {index}.", command="--kill")

    _run(action)


@app.command("@pins")
def pins_command() -> None:
    entries = list_history(pinned_only=True)
    if not entries:
        print_warning("No pinned entries yet.")
        return
    console.print(_history_table(entries, title="Pinned Clipboard Entries"))


@app.command("@transform")
def transform_command(mode: Optional[str] = typer.Argument(None)) -> None:
    def action() -> None:
        if mode is None or mode == "@help":
            console.print(_transform_modes_panel())
            return
        # BUG FIX: always read live clipboard state and warn cleanly when it is empty.
        content = read_clipboard()
        if content == "":
            print_warning("Clipboard is empty.")
            return
        transformed = transform_text(content, mode)
        # BUG FIX: line and word counts are read-only inspections.
        if mode == "wordcount":
            console.print(f"[bold cyan]Word count: {transformed}[/]")
            return
        if mode == "lines":
            console.print(f"[bold cyan]Line count: {transformed}[/]")
            return
        write_clipboard(transformed)
        _save_if_enabled(transformed, "manual")
        default_msg = f'Transformed clipboard with "{mode}" ({len(transformed)} chars). Preview: "{preview(transformed)}"'
        print_success(default_msg, command="--transform")

    _run(action)


@app.command("@qr")
def qr_command() -> None:
    def action() -> None:
        # BUG FIX: read the live clipboard at execution time and handle cleared state.
        content = read_clipboard()
        if content == "":
            print_warning("Clipboard is empty.")
            return
        console.print(render_qr_ascii(content))

    _run(action)


@app.command("@yeet")
def share_command() -> None:
    def action() -> None:
        # BUG FIX: read fresh clipboard content and use the configured share service.
        content = read_clipboard()
        if content == "":
            print_warning("Clipboard is empty.")
            return
        cfg = load_config()
        with console.status("[bold cyan]Uploading clipboard text..."):
            try:
                url = share_text(content, cfg.share_service)
            except ZibiError as exc:
                # If the configured service fails and it's termbin, try paste.rs as fallback
                if cfg.share_service == "termbin":
                    print_warning(f"{str(exc)}\n\nAttempting fallback to paste.rs...")
                    url = share_text(content, "paste.rs")
                else:
                    raise
        write_clipboard(url)
        _save_if_enabled(url, "share")
        default_msg = f"Shared clipboard text and copied URL:\n{url}"
        # Determine which share service for the message key
        share_service = "termbin" if cfg.share_service == "termbin" else "paste.rs"
        command = f"--share ({share_service})"
        print_success(default_msg, command=command)

    _run(action)


@app.command("@spy")
def watch_command() -> None:
    def action() -> None:
        last = read_clipboard()
        print_info("", command="--watch running")
        cfg = load_config()
        while True:
            time.sleep(0.75)
            current = read_clipboard()
            if current != last:
                last = current
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print_info(
                    f"[dim][{timestamp}][/] Something changed: {preview(current, 100)}",
                    command="--watch new content detected",
                    replacements={"timestamp": timestamp, "preview": preview(current, 100)}
                )
                # Always save clipboard changes to history in spy mode
                # (regardless of auto_save_history setting)
                add_history(
                    current,
                    "clipboard",
                    max_entries=cfg.max_history_entries,
                    deduplicate_consecutive=cfg.deduplicate_consecutive,
                )

    _run(action)


@app.command("@clear")
def clear_command() -> None:
    def action() -> None:
        total = count_history()
        pinned = len(list_history(pinned_only=True))
        deletable = total - pinned
        if not Confirm.ask(
            "This will empty the clipboard. Whatever is in there, gone. Sure?",
            default=False,
        ):
            print_warning("Clipboard and history were not changed.")
            return
        # BUG FIX: clear live clipboard and non-pinned history while preserving pins.
        write_clipboard("")
        deleted = wipe_unpinned()
        default_msg = f"Clipboard cleared. Deleted {deleted} non-pinned history entries; kept {pinned} pinned."
        print_success(default_msg, command="--clear")

    _run(action)


@app.command("@wipe")
def wipe_command() -> None:
    total = count_history()
    if not Confirm.ask(
        f"This will burn ALL non-pinned history. {total} entries gone forever. Sure?",
        default=False,
    ):
        print_warning("Clipboard and history were not changed.")
        return
    # BUG FIX: wipe removes the live clipboard and every history entry, including pins.
    write_clipboard("")
    deleted = wipe_all()
    default_msg = f"Clipboard cleared. Deleted all {deleted} history entries."
    print_success(default_msg, command="--wipe")


@app.command("@count")
def count_command() -> None:
    total = count_history()
    print_info(f"zibi is hoarding {total} entries for you.", command="--count", replacements={"n": total})


@app.command("@top")
def latest_command() -> None:
    # BUG FIX: @latest intentionally reads history, not the live clipboard.
    entry = latest_entry()
    if entry is None:
        return
    sys.stdout.write(entry.content)


@app.command("@stats")
def stats_command() -> None:
    data = db_stats()
    by_source = data["by_source"]
    source_table = Table(box=box.MINIMAL, show_header=False)
    source_table.add_column("Source", style="magenta")
    source_table.add_column("Count", justify="right")
    for source in ["manual", "pipe", "file", "copyp"]:
        source_table.add_row(source, str(dict(by_source).get(source, 0)))

    words = top_words(list(data["contents"]))
    words_text = "\n".join(f"{word}: {count}" for word, count in words) if words else "No words yet."
    dashboard = Table.grid(expand=True)
    dashboard.add_column(ratio=1)
    dashboard.add_column(ratio=1)
    dashboard.add_row(
        Panel(f"[bold]{data['total']}[/]\nTotal entries saved", border_style="cyan"),
        Panel(f"[bold]{data['avg_len']:.1f}[/]\nAverage entry length", border_style="green"),
    )
    dashboard.add_row(
        Panel(words_text, title="Top Words", border_style="magenta"),
        Panel(source_table, title="Entries by Source", border_style="yellow"),
    )
    dashboard.add_row(
        Panel(WEEKDAYS.get(str(data["busiest_day"]), "No entries yet"), title="Busiest Day", border_style="blue"),
        Panel(f"Pinned entries: [bold]{data['pinned']}[/]", border_style="cyan"),
    )
    console.print(Panel(dashboard, title="[bold cyan]zibi's report on your clipboard addiction:[/]", border_style="cyan"))


@app.command("@config")
def config_command() -> None:
    # BUG FIX: expose both upload services and persist the selected service live.
    cfg = load_config()
    max_entries = IntPrompt.ask("Max history entries before auto-pruning", default=cfg.max_history_entries)
    if max_entries < 1:
        max_entries = cfg.max_history_entries
    auto_save = Confirm.ask("Auto-save history on copy", default=cfg.auto_save_history)
    dedupe = Confirm.ask("Deduplicate consecutive identical copies", default=cfg.deduplicate_consecutive)
    share = Prompt.ask(
        "Share service (termbin: TCP termbin.com:9999, paste.rs: HTTPS POST)",
        choices=["termbin", "paste.rs"],
        default=cfg.share_service,
    )
    new_cfg = Config(
        max_history_entries=max_entries,
        auto_save_history=auto_save,
        deduplicate_consecutive=dedupe,
        share_service=share,
    )
    save_config(new_cfg)
    default_msg = f"Configuration saved to {CONFIG_PATH}"
    print_success(default_msg, command="--config")


@app.command("@build")
def version_command() -> None:
    console.print(
        Panel(
            f"[bold cyan]zibi[/] {__version__}\nPython {platform.python_version()}",
            title="Version",
            border_style="cyan",
        )
    )


def main() -> None:
    # Translate --command to @command for internal routing
    # This allows users to type: zibi --copy, zibi --paste, etc.
    # While internally Typer uses @copy, @paste, etc. (@ is not a reserved CLI char)
    argv = sys.argv[1:]  # Skip script name
    
    # Mapping of user-facing --commands to internal @commands
    command_map = {
        "--help": "@help",
        "--copy": "@copy",
        "--paste": "@paste",
        "--snatch": "@snatch",
        "--init": "@init",
        "--uninstall": "@uninstall",
        "--log": "@log",
        "--fetch": "@fetch",
        "--grep": "@grep",
        "--pin": "@pin",
        "--pins": "@pins",
        "--kill": "@kill",
        "--transform": "@transform",
        "--qr": "@qr",
        "--yeet": "@yeet",
        "--spy": "@spy",
        "--clear": "@clear",
        "--wipe": "@wipe",
        "--count": "@count",
        "--top": "@top",
        "--stats": "@stats",
        "--config": "@config",
        "--build": "@build",
    }
    
    # Translate the first argument if it's a --command
    if argv and argv[0] in command_map:
        argv[0] = command_map[argv[0]]
        sys.argv = [sys.argv[0]] + argv
    
    app()


if __name__ == "__main__":
    main()

