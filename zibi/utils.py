from __future__ import annotations

import base64
import contextlib
import re
import socket
import os
import urllib.parse
from collections import Counter
from pathlib import Path

import pyperclip
import qrcode
import requests
from rich.console import Console
from rich.panel import Panel


console = Console(stderr=False)
err_console = Console(stderr=True)


class ZibiError(Exception):
    """User-facing zibi error shown without a Python traceback.
    
    Can optionally include a command name for cycling error messages.
    """
    def __init__(self, message: str, command: str = None, replacements: dict = None):
        super().__init__(message)
        self.command = command
        self.replacements = replacements or {}


@contextlib.contextmanager
def _suppress_native_stderr():
    saved_fd = os.dup(2)
    try:
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            os.dup2(devnull.fileno(), 2)
            yield
    finally:
        os.dup2(saved_fd, 2)
        os.close(saved_fd)


def preview(text: str, length: int = 60) -> str:
    compact = text.replace("\r", "").replace("\n", " ")
    compact = re.sub(r"\s+", " ", compact).strip()
    if len(compact) <= length:
        return compact
    return compact[: max(0, length - 1)] + "…"


def read_clipboard() -> str:
    # BUG FIX: query pyperclip on every call so cleared clipboard state is never stale.
    try:
        with _suppress_native_stderr():
            return pyperclip.paste()
    except pyperclip.PyperclipException as exc:
        raise ZibiError(clipboard_help(str(exc))) from exc


def write_clipboard(text: str) -> None:
    try:
        with _suppress_native_stderr():
            pyperclip.copy(text)
    except pyperclip.PyperclipException as exc:
        raise ZibiError(clipboard_help(str(exc))) from exc


def clipboard_help(message: str) -> str:
    return (
        f"{message}\n\n"
        "Linux clipboard support may require xclip or xsel:\n"
        "  Debian/Ubuntu: sudo apt install xclip\n"
        "  Arch:          sudo pacman -S xclip"
    )


def transform_text(text: str, mode: str) -> str:
    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "trim":
        return text.strip()
    if mode == "reverse":
        return text[::-1]
    if mode == "base64":
        return base64.b64encode(text.encode("utf-8")).decode("ascii")
    if mode == "unbase64":
        try:
            return base64.b64decode(text.encode("ascii"), validate=True).decode("utf-8")
        except Exception as exc:
            raise ZibiError("Clipboard content is not valid UTF-8 base64 data.") from exc
    if mode == "urlencode":
        return urllib.parse.quote(text)
    if mode == "urldecode":
        return urllib.parse.unquote(text)
    if mode == "lines":
        return str(0 if text == "" else len(text.splitlines()))
    if mode == "wordcount":
        return str(len(re.findall(r"\b\w+\b", text)))
    raise ZibiError(
        "Unknown transform mode. Use one of: upper, lower, trim, reverse, base64, "
        "unbase64, urlencode, urldecode, lines, wordcount."
    )


def render_qr_ascii(text: str) -> str:
    # Check if the text is a URL/link
    if not (text.startswith("http://") or text.startswith("https://")):
        raise ZibiError(
            "QR codes are only supported for URLs/links.\n"
            "Current clipboard content is not a valid URL.\n"
            "Please copy a link to your clipboard and try again.",
            command="--qr clipboard is not a URL"
        )
    
    qr = qrcode.QRCode(border=1)
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    lines = []
    for row in matrix:
        lines.append("".join("██" if cell else "  " for cell in row))
    return "\n".join(lines)


def share_text(text: str, preferred: str = "termbin") -> str:
    # BUG FIX: route uploads strictly through the service selected in config.toml.
    if preferred == "paste.rs":
        return _share_paste_rs(text)
    if preferred == "termbin":
        return _share_termbin(text)
    raise ZibiError(f"Unknown share service: {preferred}")


def _share_termbin(text: str) -> str:
    payload = text.encode("utf-8")
    try:
        with socket.create_connection(("termbin.com", 9999), timeout=8) as sock:
            sock.sendall(payload)
            sock.shutdown(socket.SHUT_WR)
            response = sock.recv(4096).decode("utf-8", errors="replace").strip()
    except socket.timeout:
        raise ZibiError(
            "termbin.com timed out. This usually means port 9999 is blocked by your network.\n"
            "Try switching to 'paste.rs' with: zibi --config"
        )
    except Exception as exc:
        raise ZibiError(f"Failed to connect to termbin.com: {exc}")
    if not response.startswith("http"):
        raise ZibiError("termbin did not return a usable URL.")
    return response


def _share_paste_rs(text: str) -> str:
    try:
        response = requests.post(
            "https://paste.rs",
            data=text.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=12,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise ZibiError("paste.rs timed out. Please check your network connection.")
    except requests.exceptions.ConnectionError as exc:
        raise ZibiError(f"Failed to connect to paste.rs: {exc}")
    except requests.exceptions.HTTPError as exc:
        raise ZibiError(f"paste.rs returned an error: {exc}")
    except Exception as exc:
        raise ZibiError(f"Failed to upload to paste.rs: {exc}")
    url = response.text.strip()
    if not url.startswith("http"):
        raise ZibiError("paste.rs did not return a usable URL.")
    return url


def top_words(contents: list[str], limit: int = 5) -> list[tuple[str, int]]:
    words = re.findall(r"[A-Za-z0-9_]{2,}", "\n".join(contents).lower())
    stop = {"the", "and", "for", "with", "this", "that", "from", "http", "https"}
    counter = Counter(word for word in words if word not in stop)
    return counter.most_common(limit)


def print_error(message: str, command: str = None, replacements: dict = None) -> None:
    """
    Print an error message. If command is provided, use a cycling message instead.
    
    Args:
        message: Default message to display (used if command cycling is not available)
        command: Optional command name for cycling messages (e.g., "--qr clipboard is not a URL")
        replacements: Optional dict for placeholder replacement
    """
    # Try to get a cycling message if command is provided
    cycling_message = None
    if command:
        try:
            from . import message_manager
            cycling_message = message_manager.get_error_message(command, replacements)
        except Exception:
            # Fallback to default message if cycling system fails
            pass
    
    # Use cycling message if available, otherwise use provided message
    display_message = cycling_message if cycling_message else message
    err_console.print(Panel(str(display_message), title="[bold red]Error", border_style="red"))


def print_warning(message: str) -> None:
    console.print(Panel(str(message), title="[bold yellow]Warning", border_style="yellow"))


def print_success(message: str, command: str = None, replacements: dict = None) -> None:
    """
    Print a success message. If command is provided, use a cycling message instead.
    
    Args:
        message: Default message to display (used if command cycling is not available)
        command: Optional command name for cycling messages (e.g., "--copy")
        replacements: Optional dict for placeholder replacement
    """
    # Try to get a cycling message if command is provided
    cycling_message = None
    if command:
        try:
            from . import message_manager
            cycling_message = message_manager.get_success_message(command, replacements)
        except Exception:
            # Fallback to default message if cycling system fails
            pass
    
    # Use cycling message if available, otherwise use provided message
    display_message = cycling_message if cycling_message else message
    console.print(Panel(str(display_message), title="[bold green]Success", border_style="green"))


def read_text_file(path: Path, original_path: str | None = None) -> str:
    # Use as_posix() to show paths with forward slashes for consistency across platforms
    display_path = original_path or path.as_posix()
    if not path.exists():
        raise ZibiError(f"File not found: {display_path}")
    if not path.is_file():
        raise ZibiError(f"Path is not a file: {display_path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ZibiError(f"File is not valid UTF-8 text: {display_path}") from exc
