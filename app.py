"""
app.py
-------
BioDNA Inspector - Streamlit Web Application

A completely separate front-end that reuses the exact same backend
modules as main.py (analysis.py, mutation.py, comparison.py, graph.py,
report.py, utils.py). The terminal version is never imported or
modified by this file.

Run with:
    streamlit run app.py
"""

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from analysis import FastaLoadError, analyze_records, load_fasta_from_text
from comparison import ComparisonError, align_sequences, compare_sequences
from graph import GraphError, build_analysis_figure
from mutation import MutationError, apply_mutation, build_mutation_record
from report import generate_pdf_report
from utils import is_valid_base

# ----------------------------------------------------------------------
# Page configuration & global style
# ----------------------------------------------------------------------

st.set_page_config(
    page_title='BioDNA Inspector',
    page_icon='🧬',
    layout='wide',
    initial_sidebar_state='expanded',
)

PRIMARY = '#1B4F72'
ACCENT = '#17A398'

st.markdown(f"""
<style>
    .main-title {{
        font-size: 2.4rem;
        font-weight: 800;
        color: {PRIMARY};
        margin-bottom: 0;
    }}
    .subtitle {{
        color: #5D6D7E;
        font-size: 1.05rem;
        margin-top: 0;
    }}
    .metric-card {{
        background: #F4F8FB;
        border: 1px solid #E1E8ED;
        border-left: 5px solid {ACCENT};
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }}
    .feature-card {{
        background: #FFFFFF;
        border: 1px solid #E1E8ED;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .feature-card h4 {{
        color: {PRIMARY};
        margin-top: 0;
    }}
    section[data-testid="stSidebar"] {{
        background-color: #F7F9FA;
    }}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Session state initialization (replaces the terminal app's AppState)
# ----------------------------------------------------------------------

def init_state():
    defaults = {
        'records': [],
        'source_filename': '',
        'comparisons': [],
        'alignments': [],
        'graph_fig': None,
        'graph_path': '',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
os.makedirs('graphs', exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('mutations', exist_ok=True)


def get_records():
    return st.session_state['records']


# ----------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------

with st.sidebar:
    st.markdown('## 🧬 BioDNA Inspector')
    page = st.radio(
        'Navigation',
        [
            '🏠 Home',
            '📁 Upload FASTA',
            '🔬 DNA Analysis',
            '🧪 Mutation Generator',
            '🔗 Sequence Comparison',
            '📊 Graph Dashboard',
            '📄 PDF Report',
            'ℹ️ About',
        ],
    )
    st.markdown('---')
    st.markdown('### About')
    st.markdown(
        '**Developer:** Param  \n'
        '**GitHub:** [github.com/singhparamdeep018-del/BioDNA-Inspector](https://github.com/singhparamdeep018-del)  \n'
        '**Version:** 2.0.0'
    )
    if st.session_state['records']:
        st.markdown('---')
        st.success(f"{len(st.session_state['records'])} sequence(s) loaded")


# ----------------------------------------------------------------------
# Page: Home
# ----------------------------------------------------------------------

if page == '🏠 Home':
    st.markdown('<p class="main-title">🧬 BioDNA Inspector</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">A complete DNA sequence analysis, mutation, comparison, '
        'and reporting toolkit — built with Biopython, Matplotlib, and ReportLab.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('---')

    st.markdown(
        'BioDNA Inspector lets you load FASTA files, analyze nucleotide composition, '
        'simulate mutations, compare and align sequences, visualize results, and export '
        'a professional PDF report — all from one interactive dashboard.'
    )

    st.markdown('### Features')
    cols = st.columns(3)
    features = [
        ('📁', 'FASTA Loader', 'Upload single or multi-sequence FASTA files and preview them instantly.'),
        ('🔬', 'DNA Analysis', 'Composition counts, GC/AT %, reverse complement, RNA, and protein translation.'),
        ('🧪', 'Mutation Generator', 'Simulate insertion, deletion, and substitution mutations at any position.'),
        ('🔗', 'Sequence Comparison', 'Identity, matches, and Hamming distance between two sequences.'),
        ('🧬', 'Pairwise Alignment', 'Global or local alignment powered by Biopython\'s PairwiseAligner.'),
        ('📊', 'Graph Dashboard', 'Visualize nucleotide composition and length across all sequences.'),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f'<div class="feature-card"><h4>{icon} {title}</h4><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )
        if i % 3 == 2:
            st.write('')

    st.markdown('---')
    st.info('Start by going to **📁 Upload FASTA** in the sidebar to load your sequence data.')


# ----------------------------------------------------------------------
# Page: Upload FASTA
# ----------------------------------------------------------------------

elif page == '📁 Upload FASTA':
    st.markdown('## 📁 Upload FASTA File')
    uploaded = st.file_uploader('Choose a FASTA file', type=['fasta', 'fa', 'txt'])

    if uploaded is not None:
        text = uploaded.read().decode('utf-8', errors='replace')
        try:
            records = load_fasta_from_text(text, source_name=uploaded.name)
        except FastaLoadError as exc:
            st.error(f'Could not load file: {exc}')
        else:
            analyze_records(records)
            st.session_state['records'] = records
            st.session_state['source_filename'] = uploaded.name
            st.session_state['comparisons'] = []
            st.session_state['alignments'] = []
            st.session_state['graph_fig'] = None
            st.success(f'Loaded and analyzed {len(records)} sequence(s) from "{uploaded.name}".')

    records = get_records()
    if records:
        st.markdown(f'### {len(records)} Sequence(s) Found')
        overview = pd.DataFrame([
            {'ID': r.id, 'Length (bp)': r.length, 'Preview': str(r.sequence)[:50] + ('...' if r.length > 50 else '')}
            for r in records
        ])
        st.dataframe(overview, use_container_width=True, hide_index=True)

        with st.expander('Preview full sequences'):
            for r in records:
                st.text_area(r.id, str(r.sequence), height=80, key=f'preview_{r.id}')
    else:
        st.info('No FASTA file uploaded yet.')


# ----------------------------------------------------------------------
# Page: DNA Analysis
# ----------------------------------------------------------------------

elif page == '🔬 DNA Analysis':
    st.markdown('## 🔬 DNA Analysis')
    records = get_records()

    if not records:
        st.warning('Please upload a FASTA file first (📁 Upload FASTA).')
    else:
        summary_df = pd.DataFrame([r.summary_dict() for r in records])
        st.markdown('#### Composition Summary')
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown('#### Detailed View')
        for r in records:
            with st.expander(f'🧬 {r.id}  ·  {r.length} bp'):
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f'<div class="metric-card"><b>Adenine</b><br>{r.adenine}</div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="metric-card"><b>Thymine</b><br>{r.thymine}</div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="metric-card"><b>Cytosine</b><br>{r.cytosine}</div>', unsafe_allow_html=True)
                c4.markdown(f'<div class="metric-card"><b>Guanine</b><br>{r.guanine}</div>', unsafe_allow_html=True)

                c5, c6 = st.columns(2)
                c5.markdown(f'<div class="metric-card"><b>GC %</b><br>{r.gc_percent}%</div>', unsafe_allow_html=True)
                c6.markdown(f'<div class="metric-card"><b>AT %</b><br>{r.at_percent}%</div>', unsafe_allow_html=True)

                st.text_area('Reverse', str(r.reverse()), height=68, key=f'rev_{r.id}')
                st.text_area('Reverse Complement', str(r.reverse_complement()), height=68, key=f'rc_{r.id}')
                st.text_area('RNA', str(r.rna()), height=68, key=f'rna_{r.id}')
                st.text_area('Protein', str(r.protein()), height=68, key=f'prot_{r.id}')


# ----------------------------------------------------------------------
# Page: Mutation Generator
# ----------------------------------------------------------------------

elif page == '🧪 Mutation Generator':
    st.markdown('## 🧪 Mutation Generator')
    records = get_records()

    if not records:
        st.warning('Please upload a FASTA file first (📁 Upload FASTA).')
    else:
        seq_ids = [r.id for r in records]
        chosen_id = st.selectbox('Choose a sequence', seq_ids)
        record = next(r for r in records if r.id == chosen_id)
        seq_len = record.length

        st.text_area('Original sequence', str(record.sequence), height=80, disabled=True)

        mutation_type = st.radio('Mutation type', ['Insertion', 'Deletion', 'Substitution'], horizontal=True)
        mtype_key = {'Insertion': 'insert', 'Deletion': 'delete', 'Substitution': 'substitute'}[mutation_type]

        max_pos = seq_len + 1 if mtype_key == 'insert' else seq_len
        position = st.number_input('Position (1-based)', min_value=1, max_value=max(max_pos, 1), value=1, step=1)

        base = None
        if mtype_key in ('insert', 'substitute'):
            base = st.selectbox('Base', ['A', 'T', 'C', 'G'])

        if st.button('Preview Mutation', type='primary'):
            try:
                mutated = apply_mutation(str(record.sequence), mtype_key, int(position), base)
            except MutationError as exc:
                st.error(str(exc))
            else:
                st.session_state['last_mutation'] = {
                    'record_id': record.id,
                    'sequence': mutated,
                    'position': int(position),
                    'type': mtype_key,
                }
                st.success('Mutation applied (preview only — not saved yet).')
                st.text_area('Mutated sequence', mutated, height=80, key='mutated_preview')
                st.caption(f'New length: {len(mutated)} bp (was {seq_len} bp)')

        last = st.session_state.get('last_mutation')
        if last and last['record_id'] == record.id:
            seq_record = build_mutation_record(last['record_id'], last['sequence'], last['position'], last['type'])
            fasta_text = f'>{seq_record.id} {seq_record.description}\n{last["sequence"]}\n'
            st.download_button(
                'Download Mutated FASTA',
                data=fasta_text,
                file_name=f'{record.id}_{last["type"]}_mutation.fasta',
                mime='text/plain',
            )


# ----------------------------------------------------------------------
# Page: Sequence Comparison
# ----------------------------------------------------------------------

elif page == '🔗 Sequence Comparison':
    st.markdown('## 🔗 Sequence Comparison & Alignment')
    records = get_records()

    if len(records) < 2:
        st.warning('Please upload a FASTA file with at least 2 sequences.')
    else:
        seq_ids = [r.id for r in records]
        col1, col2 = st.columns(2)
        id1 = col1.selectbox('Sequence 1', seq_ids, key='cmp_seq1')
        id2 = col2.selectbox('Sequence 2', seq_ids, index=min(1, len(seq_ids) - 1), key='cmp_seq2')
        rec1 = next(r for r in records if r.id == id1)
        rec2 = next(r for r in records if r.id == id2)

        tab_compare, tab_align = st.tabs(['📐 Direct Comparison', '🧬 Pairwise Alignment'])

        with tab_compare:
            if st.button('Calculate Comparison'):
                try:
                    result = compare_sequences(rec1.sequence, rec2.sequence)
                except ComparisonError as exc:
                    st.error(str(exc))
                else:
                    st.session_state['comparisons'].append({'id1': id1, 'id2': id2, 'identity': result['identity']})
                    c1, c2, c3 = st.columns(3)
                    c1.metric('Identity', f"{result['identity']}%")
                    c2.metric('Matches', result['matches'])
                    c3.metric('Hamming Distance', result['hamming_distance'])

        with tab_align:
            mode = st.radio('Alignment mode', ['Global', 'Local'], horizontal=True)
            if st.button('Run Alignment'):
                try:
                    result = align_sequences(rec1.sequence, rec2.sequence, mode.lower())
                except ComparisonError as exc:
                    st.error(str(exc))
                else:
                    st.session_state['alignments'].append({'id1': id1, 'id2': id2, 'score': result['score']})
                    st.code(result['alignment_text'], language=None)
                    st.metric('Alignment Score', result['score'])


# ----------------------------------------------------------------------
# Page: Graph Dashboard
# ----------------------------------------------------------------------

elif page == '📊 Graph Dashboard':
    st.markdown('## 📊 Graph Dashboard')
    records = get_records()

    if not records:
        st.warning('Please upload a FASTA file first (📁 Upload FASTA).')
    else:
        if st.button('Generate / Refresh Graphs', type='primary'):
            try:
                fig = build_analysis_figure(records)
            except GraphError as exc:
                st.error(str(exc))
            else:
                st.session_state['graph_fig'] = fig
                path = 'graphs/Analysis.png'
                fig.savefig(path)
                st.session_state['graph_path'] = path

        if st.session_state['graph_fig'] is not None:
            st.pyplot(st.session_state['graph_fig'])
            with open(st.session_state['graph_path'], 'rb') as f:
                st.download_button('Download Graph as PNG', data=f.read(),
                                    file_name='BioDNA_Analysis.png', mime='image/png')
        else:
            st.info('Click "Generate / Refresh Graphs" to build the dashboard.')


# ----------------------------------------------------------------------
# Page: PDF Report
# ----------------------------------------------------------------------

elif page == '📄 PDF Report':
    st.markdown('## 📄 PDF Report Generator')
    records = get_records()

    if not records:
        st.warning('Please upload a FASTA file first (📁 Upload FASTA).')
    else:
        st.markdown('This report will include:')
        st.markdown(
            '- Title & date\n'
            '- Source filename\n'
            '- Sequence summary for every loaded sequence\n'
            '- Composition graphs (generated automatically if missing)\n'
            f"- {len(st.session_state['comparisons'])} comparison result(s)\n"
            f"- {len(st.session_state['alignments'])} alignment result(s)"
        )

        if st.button('Generate PDF Report', type='primary'):
            graph_path = st.session_state.get('graph_path')
            if not graph_path or not os.path.exists(graph_path):
                fig = build_analysis_figure(records)
                graph_path = 'graphs/Analysis.png'
                fig.savefig(graph_path)
                st.session_state['graph_path'] = graph_path

            output_path = 'reports/Analysis.pdf'
            generate_pdf_report(
                records=records,
                comparisons=st.session_state['comparisons'],
                alignments=st.session_state['alignments'],
                graph_path=graph_path,
                output_path=output_path,
                source_filename=st.session_state['source_filename'],
            )
            st.success('PDF report generated successfully.')
            with open(output_path, 'rb') as f:
                st.download_button('Download PDF Report', data=f.read(),
                                    file_name='BioDNA_Inspector_Report.pdf', mime='application/pdf')


# ----------------------------------------------------------------------
# Page: About
# ----------------------------------------------------------------------

elif page == 'ℹ️ About':
    st.markdown('## ℹ️ About BioDNA Inspector')
    st.markdown(
        '**BioDNA Inspector** is a DNA sequence analysis toolkit built as a college '
        'Biotechnology project, combining bioinformatics logic with an interactive '
        'web interface.'
    )
    st.markdown('#### Developer')
    st.markdown('Paramdeep Singh — BSc Biotechnology, Chandigarh Group of Colleges (CGC), Jhanjeri, Mohali')
    st.markdown('#### GitHub')
    st.markdown('[github.com/singhparamdeep018-del/BioDNA-Inspector](https://github.com/singhparamdeep018-del) ')
    st.markdown('#### Version')
    st.markdown('2.0.0')
    st.markdown('#### Libraries Used')
    st.markdown('- Biopython\n- Matplotlib\n- ReportLab\n- Streamlit\n- Pandas')
    st.caption(f'Last loaded: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
