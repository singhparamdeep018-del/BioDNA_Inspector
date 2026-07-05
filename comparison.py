"""
comparison.py
--------------
Sequence comparison (position-by-position identity) and pairwise
alignment (via Biopython's PairwiseAligner) backend functions.
"""

from Bio.Align import PairwiseAligner


class ComparisonError(ValueError):
    """Raised when two sequences cannot be compared or aligned."""


def compare_sequences(seq1, seq2):
    """
    Compare two equal-length sequences position by position.

    Returns a dict with match/mismatch counts, Hamming distance, and
    percentage identity. Raises ComparisonError if the sequences differ
    in length or are empty, matching the original tool's requirement of
    equal-length input for a direct comparison (rather than crashing).
    """
    s1, s2 = str(seq1), str(seq2)
    if len(s1) == 0 or len(s2) == 0:
        raise ComparisonError('Cannot compare empty sequences.')
    if len(s1) != len(s2):
        raise ComparisonError(
            f'Sequences must be the same length to compare directly '
            f'(got {len(s1)} and {len(s2)}).'
        )

    mismatches = sum(1 for a, b in zip(s1, s2) if a != b)
    matches = len(s1) - mismatches
    identity = round((matches / len(s1)) * 100, 2)

    return {
        'matches': matches,
        'mismatches': mismatches,
        'hamming_distance': mismatches,
        'identity': identity,
        'length': len(s1),
    }


def align_sequences(seq1, seq2, mode='global'):
    """
    Perform pairwise alignment of two sequences using Biopython's
    PairwiseAligner, with the same scoring scheme used in the original
    tool (match=+1, mismatch=-1, gap open=-2, gap extend=-1).

    `mode` must be 'global' or 'local'. Returns a dict with the
    formatted alignment string and the numeric alignment score.
    """
    mode = str(mode).lower().strip()
    if mode not in ('global', 'local'):
        raise ComparisonError('Alignment mode must be "global" or "local".')
    if len(str(seq1)) == 0 or len(str(seq2)) == 0:
        raise ComparisonError('Cannot align empty sequences.')

    aligner = PairwiseAligner()
    aligner.match_score = 1
    aligner.mismatch_score = -1
    aligner.open_gap_score = -2
    aligner.extend_gap_score = -1
    aligner.mode = mode

    alignments = aligner.align(str(seq1), str(seq2))
    best = alignments[0]

    return {
        'alignment_text': str(best),
        'score': best.score,
    }
