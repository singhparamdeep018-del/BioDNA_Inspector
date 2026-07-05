"""
analysis.py
------------
Core data model and DNA analysis backend for BioDNA Inspector.

Contains the SequenceRecord class (a clean replacement for the original
`Sequ` class) and the functions used to load FASTA files and compute
DNA composition statistics.

These functions never call input()/print() directly and never raise
uncaught exceptions for bad user data - they return data or raise a
dedicated FastaLoadError, so they can be reused unchanged by both
main.py (terminal) and app.py (Streamlit).
"""

import io
from dataclasses import dataclass

from Bio import SeqIO
from Bio.Seq import Seq


@dataclass
class SequenceRecord:
    """
    Represents a single DNA sequence loaded from a FASTA file, together
    with its computed composition statistics.

    Replaces the original `Sequ` class with a cleaner design that has
    no dependency on module-level globals (`record`, `ana`, etc. in the
    original script).
    """
    id: str
    sequence: Seq
    source_file: str
    adenine: int = 0
    thymine: int = 0
    cytosine: int = 0
    guanine: int = 0
    gc_percent: float = 0.0
    at_percent: float = 0.0
    analyzed: bool = False

    @property
    def length(self):
        return len(self.sequence)

    def compute_statistics(self):
        """Compute nucleotide counts and GC/AT percentages for this record."""
        seq_str = str(self.sequence).upper()
        length = len(seq_str) or 1  # guard against division by zero
        self.adenine = seq_str.count('A')
        self.thymine = seq_str.count('T')
        self.cytosine = seq_str.count('C')
        self.guanine = seq_str.count('G')
        self.gc_percent = round(((self.guanine + self.cytosine) / length) * 100, 2)
        self.at_percent = round(100 - self.gc_percent, 2)
        self.analyzed = True
        return self

    def reverse(self):
        """Return the sequence reversed (not complemented)."""
        return self.sequence[::-1]

    def reverse_complement(self):
        return self.sequence.reverse_complement()

    def rna(self):
        return self.sequence.transcribe()

    def protein(self):
        """
        Translate the DNA sequence to protein.

        Trailing bases that don't form a complete codon are trimmed first
        to avoid Biopython's "partial codon" warning - the original script
        did not handle this and could emit noisy warnings on non-multiple-
        of-3 sequences.
        """
        seq = self.sequence
        trimmed_len = len(seq) - (len(seq) % 3)
        if trimmed_len == 0:
            return Seq('')
        return seq[:trimmed_len].translate()

    def summary_dict(self):
        """Return a dictionary summary, convenient for tables / UI display."""
        return {
            'ID': self.id,
            'Length': self.length,
            'Adenine (A)': self.adenine,
            'Thymine (T)': self.thymine,
            'Cytosine (C)': self.cytosine,
            'Guanine (G)': self.guanine,
            'GC %': self.gc_percent,
            'AT %': self.at_percent,
        }


class FastaLoadError(Exception):
    """Raised when a FASTA file/text cannot be found, parsed, or is empty."""


def _records_from_parsed(parsed_entries, source_name):
    if not parsed_entries:
        raise FastaLoadError(
            'No valid sequences found. Please check the file follows FASTA format.'
        )
    return [
        SequenceRecord(id=entry.id, sequence=entry.seq, source_file=source_name)
        for entry in parsed_entries
    ]


def load_fasta(filepath):
    """
    Parse a FASTA file on disk and return a list of SequenceRecord objects.

    Raises FastaLoadError with a descriptive message on any failure
    (missing file, unreadable file, empty/invalid FASTA content) instead
    of letting the caller crash.
    """
    try:
        with open(filepath) as handle:
            parsed = list(SeqIO.parse(handle, 'fasta'))
    except FileNotFoundError:
        raise FastaLoadError(f'File not found: {filepath}')
    except OSError as exc:
        raise FastaLoadError(f'Could not read file: {exc}')

    return _records_from_parsed(parsed, filepath)


def load_fasta_from_text(fasta_text, source_name='uploaded_file'):
    """
    Parse FASTA content already held in memory (e.g. bytes/text from a
    Streamlit file upload). Mirrors load_fasta() but works on a string
    instead of a file path.
    """
    try:
        parsed = list(SeqIO.parse(io.StringIO(fasta_text), 'fasta'))
    except Exception as exc:  # noqa: BLE001 - surface any parse error uniformly
        raise FastaLoadError(f'Could not parse FASTA content: {exc}')

    return _records_from_parsed(parsed, source_name)


def analyze_records(records):
    """Compute statistics for every SequenceRecord in `records` (in place) and return the list."""
    for record in records:
        record.compute_statistics()
    return records


def get_record_by_index(records, index):
    """
    Safely fetch a record by 1-based index (as used throughout the CLI menus).
    Returns None instead of raising IndexError on an invalid selection -
    this is what prevents the "invalid sequence selection" crashes.
    """
    if not isinstance(index, int) or not (1 <= index <= len(records)):
        return None
    return records[index - 1]
