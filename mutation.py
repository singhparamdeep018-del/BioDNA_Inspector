"""
mutation.py
------------
Mutation generator backend: insertion, deletion, and substitution of
DNA nucleotides, plus helpers to package mutated sequences into FASTA
records/files.

All functions are pure (no input()/print()) and validate their
arguments, raising MutationError on bad input instead of crashing.
This lets both the terminal app and the Streamlit app share identical
mutation logic.
"""

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO

from utils import is_valid_base, is_valid_position


class MutationError(ValueError):
    """Raised when a mutation cannot be applied due to invalid input."""


def insert_base(sequence, position, base):
    """
    Insert `base` at 1-based `position` in `sequence`.
    `position` may range from 1 to len(sequence) + 1 (append at the end).
    """
    seq_str = str(sequence)
    base = str(base).upper()
    if not is_valid_base(base):
        raise MutationError(f'Invalid nucleotide "{base}". Must be one of A, T, C, G.')
    if not is_valid_position(position, len(seq_str), allow_end=True):
        raise MutationError(
            f'Invalid position {position}. Must be between 1 and {len(seq_str) + 1}.'
        )
    return seq_str[:position - 1] + base + seq_str[position - 1:]


def delete_base(sequence, position):
    """Delete the nucleotide at 1-based `position` in `sequence`."""
    seq_str = str(sequence)
    if len(seq_str) == 0:
        raise MutationError('Cannot delete from an empty sequence.')
    if not is_valid_position(position, len(seq_str), allow_end=False):
        raise MutationError(
            f'Invalid position {position}. Must be between 1 and {len(seq_str)}.'
        )
    return seq_str[:position - 1] + seq_str[position:]


def substitute_base(sequence, position, base):
    """Replace the nucleotide at 1-based `position` in `sequence` with `base`."""
    seq_str = str(sequence)
    base = str(base).upper()
    if not is_valid_base(base):
        raise MutationError(f'Invalid nucleotide "{base}". Must be one of A, T, C, G.')
    if not is_valid_position(position, len(seq_str), allow_end=False):
        raise MutationError(
            f'Invalid position {position}. Must be between 1 and {len(seq_str)}.'
        )
    return seq_str[:position - 1] + base + seq_str[position:]


def apply_mutation(sequence, mutation_type, position, base=None):
    """
    Dispatch to the correct mutation function based on `mutation_type`
    ('insert', 'delete', or 'substitute'). Raises MutationError for an
    unknown mutation type or invalid arguments.
    """
    mutation_type = str(mutation_type).lower()
    if mutation_type == 'insert':
        return insert_base(sequence, position, base)
    if mutation_type == 'delete':
        return delete_base(sequence, position)
    if mutation_type == 'substitute':
        return substitute_base(sequence, position, base)
    raise MutationError(f'Unknown mutation type "{mutation_type}".')


def build_mutation_record(record_id, mutated_sequence, position, mutation_type):
    """Wrap a mutated sequence string into a Biopython SeqRecord for FASTA export."""
    return SeqRecord(
        Seq(mutated_sequence),
        id=record_id,
        description=f'{mutation_type.capitalize()} mutation at position {position}',
    )


def save_mutated_fasta(seq_records, filepath):
    """Write a list of SeqRecord objects to a FASTA file at `filepath`."""
    SeqIO.write(seq_records, filepath, 'fasta')
    return filepath
