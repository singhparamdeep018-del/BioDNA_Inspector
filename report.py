"""
report.py
----------
PDF report generation backend (ReportLab). Builds a complete report
covering sequence summaries, the analysis graph, comparison results,
and alignment results - used by both main.py and app.py.
"""

from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


def generate_pdf_report(records, comparisons=None, alignments=None,
                         graph_path=None, output_path='reports/Analysis.pdf',
                         source_filename=''):
    """
    Build a PDF report summarizing analyzed sequences, an optional
    composition graph image, optional comparison results, and optional
    alignment results.

    Parameters
    ----------
    records : list[SequenceRecord]
        Analyzed sequences to summarize.
    comparisons : list[dict] | None
        Each dict expected to have keys: id1, id2, identity.
    alignments : list[dict] | None
        Each dict expected to have keys: id1, id2, score.
    graph_path : str | None
        Path to a PNG image (e.g. produced by graph.save_analysis_graph)
        to embed in the report.
    output_path : str
        Where to write the resulting PDF.
    source_filename : str
        Original FASTA filename, shown in the report header.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20,
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('<b>BioDNA Inspector Report</b>', styles['Title']))
    formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M')
    elements.append(Paragraph(
        f'<b>Date:</b> {formatted_date}<br/><b>File:</b> {source_filename}',
        styles['Normal'],
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph('<b>Sequence Summary</b>', styles['Heading2']))
    for rec in records:
        elements.append(Paragraph(
            f'Sequence ID: {rec.id}<br/>'
            f'Length: {rec.length} bp<br/>'
            f'Adenine: {rec.adenine} | Thymine: {rec.thymine} | '
            f'Cytosine: {rec.cytosine} | Guanine: {rec.guanine}<br/>'
            f'GC Content: {rec.gc_percent:.2f}% | AT Content: {rec.at_percent:.2f}%',
            styles['Normal'],
        ))
        elements.append(Spacer(1, 10))

    if graph_path:
        elements.append(Paragraph('<b>Composition Graphs</b>', styles['Heading2']))
        image = Image(graph_path)
        image.drawWidth = 6.5 * inch
        image.drawHeight = 3.5 * inch
        elements.append(image)
        elements.append(Spacer(1, 12))

    if comparisons:
        elements.append(Paragraph('<b>Comparison Report</b>', styles['Heading2']))
        for comp in comparisons:
            elements.append(Paragraph(
                f"Sequence 1: {comp['id1']} | Sequence 2: {comp['id2']}<br/>"
                f"Identity: {comp['identity']:.2f}%",
                styles['Normal'],
            ))
            elements.append(Spacer(1, 8))

    if alignments:
        elements.append(Paragraph('<b>Alignment Report</b>', styles['Heading2']))
        for align in alignments:
            elements.append(Paragraph(
                f"Sequence 1: {align['id1']} | Sequence 2: {align['id2']}<br/>"
                f"Alignment Score: {align['score']:.2f}",
                styles['Normal'],
            ))
            elements.append(Spacer(1, 8))

    doc.build(elements)
    return output_path
