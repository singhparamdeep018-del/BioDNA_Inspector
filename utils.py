"""
utils.py
---------
Shared utility functions used across the BioDNA Inspector project.

Contains:
    - Pure validation helpers (used by both the terminal app and the
      Streamlit web app, and by the backend modules themselves).
    - CLI-only convenience functions (input prompting, loading
      animation) used exclusively by main.py.

Keeping these in one place removes the duplicate validation / input
handling code that was scattered throughout the original script.
"""

import time

VALID_BASES = ('A', 'T', 'C', 'G')


# ---------------------------------------------------------------------
# Pure validators (safe to import from anywhere: CLI, Streamlit, tests)
# ---------------------------------------------------------------------

def is_valid_base(base):
    """Return True if `base` is a single valid DNA nucleotide (A/T/C/G)."""
    return isinstance(base, str) and base.strip().upper() in VALID_BASES


def is_valid_dna_sequence(sequence):
    """Return True if every character in `sequence` is a valid DNA base."""
    if not sequence:
        return False
    return all(ch.upper() in VALID_BASES for ch in str(sequence))


def is_valid_position(position, sequence_length, allow_end=True):
    """
    Validate a 1-based nucleotide position against a sequence length.

    `allow_end=True` permits position == sequence_length + 1, which is
    required for "insert after the last base" operations. Deletion and
    substitution should call this with `allow_end=False`.
    """
    if not isinstance(position, int):
        return False
    upper_bound = sequence_length + 1 if allow_end else sequence_length
    return 1 <= position <= upper_bound


def safe_int(value, default=None):
    """Try to convert `value` to an int, returning `default` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------
# CLI-only helpers (used exclusively by the terminal version, main.py)
# ---------------------------------------------------------------------

def prompt_int(prompt_text, min_value=None, max_value=None):
    """
    Repeatedly prompt the user for an integer until a valid one
    (optionally constrained to [min_value, max_value]) is supplied.
    Prevents the crashes caused by unvalidated int(input(...)) calls
    in the original script.
    """
    while True:
        raw = input(prompt_text)
        value = safe_int(raw)
        if value is None:
            print('Invalid input. Please enter a whole number.')
            continue
        if min_value is not None and value < min_value:
            print(f'Value must be at least {min_value}.')
            continue
        if max_value is not None and value > max_value:
            print(f'Value must be at most {max_value}.')
            continue
        return value


def prompt_yes_no(prompt_text):
    """Prompt until the user answers YES or NO (case-insensitive). Returns bool."""
    while True:
        answer = input(prompt_text).strip().upper()
        if answer == 'YES':
            return True
        if answer == 'NO':
            return False
        print("Please answer with 'Yes' or 'No'.")


def prompt_base(prompt_text):
    """Prompt until the user enters a valid nucleotide (A/T/C/G)."""
    while True:
        base = input(prompt_text).strip().upper()
        if is_valid_base(base):
            return base
        print('Invalid nucleotide. Please enter one of A, T, C, G.')


def prompt_choice(prompt_text, valid_choices):
    """Prompt until the user enters one of `valid_choices` (case-insensitive)."""
    normalized = {str(c).upper() for c in valid_choices}
    while True:
        choice = input(prompt_text).strip().upper()
        if choice in normalized:
            return choice
        print(f'Invalid choice. Please choose one of: {", ".join(sorted(normalized))}.')


def loading_animation(message='Processing', steps=5, delay=0.2):
    """Small cosmetic loading animation, preserved from the original CLI."""
    print(message, end='')
    for _ in range(steps):
        time.sleep(delay)
        print('.', end='', flush=True)
    print(' Done')
