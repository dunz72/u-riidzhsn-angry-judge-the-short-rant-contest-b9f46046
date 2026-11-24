#!/usr/bin/env python3
"""Angry Judge: The Short Rant Contest — entry copier.

Reads the rant from ``entry.txt`` sitting next to this script and
writes it, byte for byte, to ``entry.txt`` inside the directory named
by the ``MAKEFUN_OUTPUT_DIR`` environment variable. When that
variable is absent or blank, a local ``output`` folder next to this
file is used.

Everything here is standard library only. The result is fully
deterministic: same input, same bytes, every run.
"""

import hashlib
import os
import sys
from pathlib import Path

ENTRY_NAME = "entry.txt"
ENV_VAR = "MAKEFUN_OUTPUT_DIR"
MAX_CHARS = 400


def script_dir():
    """Folder holding this script (and therefore entry.txt)."""
    return Path(__file__).resolve().parent


def source_path():
    """Full path of the rant file beside this script."""
    return script_dir() / ENTRY_NAME


def load_text(path):
    """Read a UTF-8 text file and return its contents."""
    return path.read_text(encoding="utf-8")


def read_rant():
    """Load the rant text from entry.txt beside this script."""
    return load_text(source_path())


def check_not_empty(text):
    """Reject a rant that is empty or only whitespace."""
    if not text.strip():
        raise ValueError("rant must not be empty or only whitespace")


def check_length(text):
    """Reject a rant longer than the contest limit."""
    if len(text) > MAX_CHARS:
        raise ValueError(
            "rant must be 1-%d characters, got %d" % (MAX_CHARS, len(text))
        )


def check_no_control_chars(text):
    """Reject invisible control characters other than newline/tab."""
    allowed = {"\n", "\t", "\r"}
    for ch in text:
        if ord(ch) < 32 and ch not in allowed:
            raise ValueError(
                "rant must not contain control character U+%04X" % ord(ch)
            )


def check_rant(text):
    """Guard the rant: real text, 1 to 400 characters, not only space."""
    check_not_empty(text)
    check_length(text)
    check_no_control_chars(text)


def configured_root():
    """Output dir from the environment, or None when unset/blank."""
    configured = os.environ.get(ENV_VAR, "").strip()
    if configured:
        return Path(configured)
    return None


def fallback_root():
    """Local ./output folder beside this script."""
    return script_dir() / "output"


def pick_output_root():
    """Return the folder that should hold the entry file.

    The MAKEFUN_OUTPUT_DIR variable wins when it is set to a
    non-empty value; otherwise fall back to ./output beside
    this script.
    """
    root = configured_root()
    if root is not None:
        return root
    return fallback_root()


def encode_rant(text):
    """Encode the rant as the exact bytes to write out."""
    return text.encode("utf-8")


def ensure_parent_dir(path):
    """Create the output file's parent folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def digest_of(data):
    """SHA-256 hex digest of a bytes object."""
    return hashlib.sha256(data).hexdigest()


def verify_written(path, data):
    """Confirm the file on disk matches the bytes we meant to write."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != digest_of(data):
        raise ValueError("SHA-256 mismatch after writing entry.txt")
    return digest


def write_entry(path, text):
    """Persist the rant exactly as read, then verify it by SHA-256."""
    data = encode_rant(text)
    ensure_parent_dir(path)
    path.write_bytes(data)
    return verify_written(path, data)


def report_written(path, text, digest):
    """Print a one-line summary of the written entry."""
    print("wrote %s (%d chars, sha256 %s)" % (path, len(text), digest))


def emit():
    """Read the rant, validate it, then copy it to the output dir."""
    rant = read_rant()
    check_rant(rant)
    root = pick_output_root()
    target = root / ENTRY_NAME
    digest = write_entry(target, rant)
    report_written(target, rant, digest)


def main(argv=None):
    """Entry point: emit the rant and report success."""
    del argv  # unused; kept for a conventional signature
    emit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
