"""
main.py
--------
BioDNA Inspector - Terminal Application

This is the refactored terminal (CLI) version of BioDNA Inspector.
It preserves every feature of the original script:

    1. Load FASTA file
    2. DNA Analysis
    3. Mutation Generator (insertion / deletion / substitution)
    4. Sequence Comparison + Pairwise Alignment
    5. Graph Dashboard generation
    6. PDF Report generation

What changed compared to the original script:
    - No module-level global variables (`record`, `ana`, `bias`, ...).
      All state is kept in a single AppState object passed explicitly
      between menu functions.
    - All DNA/mutation/comparison/graph/report logic now lives in
      dedicated backend modules (analysis.py, mutation.py, comparison.py,
      graph.py, report.py) that are shared with the Streamlit app
      (app.py) - no duplicated logic between the two interfaces.
    - Every user input is validated; invalid FASTA files, invalid menu
      choices, invalid sequence selections, and invalid positions/bases
      are all handled gracefully instead of crashing the program.
    - The menu loops correctly until the user chooses to exit, instead
      of the original's inconsistent "continue"/"break" chains.
"""

from dataclasses import dataclass, field

from analysis import (
    FastaLoadError,
    analyze_records,
    get_record_by_index,
    load_fasta,
)
from comparison import ComparisonError, align_sequences, compare_sequences
from graph import GraphError, save_analysis_graph
from mutation import (
    MutationError,
    apply_mutation,
    build_mutation_record,
    save_mutated_fasta,
)
from report import generate_pdf_report
from utils import loading_animation, prompt_base, prompt_choice, prompt_int, prompt_yes_no


@dataclass
class AppState:
    """Holds all session state for the terminal app (replaces globals)."""
    records: list = field(default_factory=list)
    source_filename: str = ''
    comparisons: list = field(default_factory=list)
    alignments: list = field(default_factory=list)
    graph_path: str = ''


# ---------------------------------------------------------------------
# Menu 1: Load FASTA
# ---------------------------------------------------------------------

def menu_load_fasta(state):
    """Prompt for a FASTA file path, load it, and print a short summary."""
    while True:
        filepath = input('Enter FASTA file path: ').strip()
        try:
            records = load_fasta(filepath)
        except FastaLoadError as exc:
            print(f'Error: {exc}')
            if not prompt_yes_no('Try another file? (Yes or No): '):
                return False
            continue

        state.records = records
        state.source_filename = filepath
        print(f'\nLoaded {len(records)} sequence(s) from "{filepath}":')
        for i, rec in enumerate(records, start=1):
            print(f'  {i}. {rec.id}  (length: {len(rec.sequence)} bp)')
        print('Data loaded successfully.\n')
        return True


# ---------------------------------------------------------------------
# Menu 2: DNA Analysis
# ---------------------------------------------------------------------

def menu_analysis(state):
    """Run composition analysis on all loaded sequences and print the results."""
    if not state.records:
        print('No sequences loaded yet. Please load a FASTA file first (Option 1).')
        return

    analyze_records(state.records)
    for rec in state.records:
        print('-' * 60)
        print('Sequence Name        :', rec.id)
        print('Sequence             :', rec.sequence)
        print('Length               :', rec.length)
        print('Adenine (A)          :', rec.adenine)
        print('Thymine (T)          :', rec.thymine)
        print('Cytosine (C)         :', rec.cytosine)
        print('Guanine (G)          :', rec.guanine)
        print(f'GC Percentage        : {rec.gc_percent}%')
        print(f'AT Percentage        : {rec.at_percent}%')
        print('Reverse              :', rec.reverse())
        print('Reverse Complement   :', rec.reverse_complement())
        print('RNA                  :', rec.rna())
        print('Protein              :', rec.protein())
    print('-' * 60)
    print('Analysis complete.\n')


# ---------------------------------------------------------------------
# Menu 3: Mutation Generator
# ---------------------------------------------------------------------

def _select_sequence(records, prompt_label='Select a sequence'):
    """Display all loaded sequences and let the user pick one safely."""
    for i, rec in enumerate(records, start=1):
        print(f'  {i}. {rec.id}')
    while True:
        index = prompt_int(f'{prompt_label} (1-{len(records)}): ', 1, len(records))
        record = get_record_by_index(records, index)
        if record is not None:
            return record
        print('Invalid selection. Please try again.')


def menu_mutation(state):
    """
    Interactive mutation generator: insertion, deletion, or substitution.
    Mutations can be chained (apply several in a row) before saving, exactly
    like the original tool, but with full input validation.
    """
    if not state.records:
        print('No sequences loaded yet. Please load a FASTA file first (Option 1).')
        return

    print('=' * 20, 'MUTATION GENERATOR', '=' * 20)
    print('1. Insert\n2. Delete\n3. Substitute')
    choice = prompt_choice('Enter choice (1/2/3): ', ['1', '2', '3'])
    mutation_type = {'1': 'insert', '2': 'delete', '3': 'substitute'}[choice]

    record = _select_sequence(state.records, 'Select the sequence to mutate')
    current_seq = str(record.sequence)
    loading_animation('Setting up')

    mutated_records = []
    while True:
        print(f'\nCurrent sequence ({record.id}), length {len(current_seq)}:')
        print(current_seq)

        if mutation_type == 'insert':
            position = prompt_int(
                f'Enter position to insert at (1-{len(current_seq) + 1}): ',
                1, len(current_seq) + 1,
            )
            base = prompt_base('Enter nucleotide to insert (A/T/C/G): ')
        elif mutation_type == 'substitute':
            position = prompt_int(
                f'Enter position to substitute (1-{len(current_seq)}): ',
                1, len(current_seq),
            )
            base = prompt_base('Enter replacement nucleotide (A/T/C/G): ')
        else:  # delete
            position = prompt_int(
                f'Enter position to delete (1-{len(current_seq)}): ',
                1, len(current_seq),
            )
            base = None

        try:
            current_seq = apply_mutation(current_seq, mutation_type, position, base)
        except MutationError as exc:
            print(f'Error: {exc}')
            continue

        print('Mutated sequence:', current_seq)
        print('New length      :', len(current_seq))

        if prompt_yes_no('Apply another mutation to this sequence? (Yes or No): '):
            continue

        if prompt_yes_no('Save the progress to a FASTA file? (Yes or No): '):
            mutated_records.append(
                build_mutation_record(record.id, current_seq, position, mutation_type)
            )
        break

    if mutated_records:
        output_path = f'mutations/Mutation_{mutation_type}.fasta'
        save_mutated_fasta(mutated_records, output_path)
        print(f'File created successfully: {output_path}\n')
    else:
        print('No mutations were saved.\n')


# ---------------------------------------------------------------------
# Menu 4: Sequence Comparison + Alignment
# ---------------------------------------------------------------------

def menu_compare(state):
    """
    Interactive comparison / alignment menu. Users can run any number of
    comparisons and/or alignments before returning to the main menu.
    """
    if len(state.records) < 2:
        print('You need at least 2 loaded sequences to compare. Please load a FASTA file first.')
        return

    print('=' * 15, 'SEQUENCE COMPARISON / ALIGNMENT', '=' * 15)
    while True:
        print('\n1. Compare\n2. Align\n3. Exit to main menu')
        choice = prompt_choice('Enter choice (1/2/3): ', ['1', '2', '3'])

        if choice == '3':
            break

        print('Select the first sequence:')
        rec1 = _select_sequence(state.records)
        print('Select the second sequence:')
        rec2 = _select_sequence(state.records)

        if choice == '1':
            loading_animation('Calculating')
            try:
                result = compare_sequences(rec1.sequence, rec2.sequence)
            except ComparisonError as exc:
                print(f'Error: {exc}')
                continue
            print('Hamming Distance :', result['hamming_distance'])
            print('Matches          :', result['matches'])
            print(f"Identity         : {result['identity']}%")
            state.comparisons.append({
                'id1': rec1.id, 'id2': rec2.id, 'identity': result['identity'],
            })
        else:  # Align
            mode = prompt_choice('Enter alignment mode (GLOBAL/LOCAL): ', ['GLOBAL', 'LOCAL']).lower()
            try:
                result = align_sequences(rec1.sequence, rec2.sequence, mode)
            except ComparisonError as exc:
                print(f'Error: {exc}')
                continue
            print(result['alignment_text'])
            print('Alignment Score  :', result['score'])
            state.alignments.append({
                'id1': rec1.id, 'id2': rec2.id, 'score': result['score'],
            })

        if not prompt_yes_no('Run another comparison/alignment? (Yes or No): '):
            break
    print()


# ---------------------------------------------------------------------
# Menu 5: Graph Dashboard
# ---------------------------------------------------------------------

def menu_graphs(state):
    """Generate the composition graph dashboard PNG for all analyzed sequences."""
    if not state.records:
        print('No sequences loaded yet. Please load a FASTA file first (Option 1).')
        return
    if not all(rec.analyzed for rec in state.records):
        analyze_records(state.records)

    try:
        path = save_analysis_graph(state.records, 'graphs/Analysis.png')
    except GraphError as exc:
        print(f'Error: {exc}')
        return

    state.graph_path = path
    print(f'Graph saved successfully to {path}\n')


# ---------------------------------------------------------------------
# Menu 6: PDF Report
# ---------------------------------------------------------------------

def menu_pdf(state):
    """Generate the full PDF report covering analysis, graphs, comparisons, and alignments."""
    if not state.records:
        print('No sequences loaded yet. Please load a FASTA file first (Option 1).')
        return
    if not all(rec.analyzed for rec in state.records):
        analyze_records(state.records)
    if not state.graph_path:
        state.graph_path = save_analysis_graph(state.records, 'graphs/Analysis.png')

    output_path = 'reports/Analysis.pdf'
    generate_pdf_report(
        records=state.records,
        comparisons=state.comparisons,
        alignments=state.alignments,
        graph_path=state.graph_path,
        output_path=output_path,
        source_filename=state.source_filename,
    )
    print(f'PDF report generated successfully: {output_path}\n')


# ---------------------------------------------------------------------
# Main menu loop
# ---------------------------------------------------------------------

MENU_TEXT = (
    '\n1. Load FASTA File\n'
    '2. DNA Analysis\n'
    '3. Mutation Generator\n'
    '4. Sequence Comparison\n'
    '5. Generate Graphs\n'
    '6. Generate PDF Report\n'
    '7. Exit\n'
)

MENU_ACTIONS = {
    '1': menu_load_fasta,
    '2': menu_analysis,
    '3': menu_mutation,
    '4': menu_compare,
    '5': menu_graphs,
    '6': menu_pdf,
}


def run():
    """Entry point for the terminal application."""
    print('=' * 60)
    print('                   BIO DNA INSPECTOR')
    print('=' * 60)
    print('NOTE: FASTA files must follow standard FASTA format.\n')

    state = AppState()
    while True:
        print(MENU_TEXT)
        choice = prompt_choice('Select an option (1-7): ', ['1', '2', '3', '4', '5', '6', '7'])
        if choice == '7':
            print('Goodbye!')
            break
        MENU_ACTIONS[choice](state)


if __name__ == '__main__':
    run()
