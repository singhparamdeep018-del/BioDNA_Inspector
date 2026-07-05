"""
graph.py
---------
Graph dashboard backend: builds the six-panel nucleotide/GC/length
comparison chart used by both the terminal tool (saved straight to
disk) and the Streamlit dashboard (returned as a Matplotlib Figure
for on-screen display and PNG download).
"""

import matplotlib
matplotlib.use('Agg')  # headless backend - safe for servers / Streamlit
import matplotlib.pyplot as plt


# (attribute on SequenceRecord, panel title, bar color, y-axis label)
PANEL_CONFIG = [
    ('adenine', 'Adenine', 'red', 'Count'),
    ('thymine', 'Thymine', 'green', 'Count'),
    ('cytosine', 'Cytosine', 'blue', 'Count'),
    ('guanine', 'Guanine', 'goldenrod', 'Count'),
    ('gc_percent', 'GC Content %', 'darkcyan', 'Percentage'),
    ('length', 'Sequence Length', 'orchid', 'Length (bp)'),
]


class GraphError(ValueError):
    """Raised when a graph cannot be built (e.g. no analyzed records)."""


def build_analysis_figure(records):
    """
    Build and return a Matplotlib Figure with a 2x3 grid of bar charts
    covering Adenine, Thymine, Cytosine, Guanine, GC%, and Length across
    all analyzed records.
    """
    if not records:
        raise GraphError('No analyzed sequences available to graph.')

    ids = [r.id for r in records]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    flat_axes = axes.flatten()

    for ax, (attr, title, color, ylabel) in zip(flat_axes, PANEL_CONFIG):
        values = [r.length if attr == 'length' else getattr(r, attr) for r in records]
        ax.bar(ids, values, color=color)
        ax.set_title(title)
        ax.set_xlabel('Sequence')
        ax.set_ylabel(ylabel)
        ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    return fig


def save_analysis_graph(records, output_path='graphs/Analysis.png'):
    """Build the analysis figure and save it as a PNG file at `output_path`."""
    fig = build_analysis_figure(records)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path
