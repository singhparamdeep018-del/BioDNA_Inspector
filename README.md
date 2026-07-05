# 🧬 BioDNA Inspector

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit&logoColor=white)
![Biopython](https://img.shields.io/badge/Biopython-Sequence%20Analysis-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A complete DNA sequence analysis, mutation, comparison, and reporting toolkit — available both as a **terminal application** and as a **Streamlit web application**, built on top of a single shared backend.

---

## 📖 Description

**BioDNA Inspector** lets you load FASTA files, analyze nucleotide composition, simulate mutations, compare and align sequences, visualize results with charts, and export a professional PDF report — all from one interactive tool.

The project ships two interfaces built on the same backend logic:
- A classic **terminal (CLI) application** (`main.py`)
- A modern **Streamlit web application** (`app.py`)

---

## ✨ Features

- 📁 **FASTA Loader** — load single or multi-sequence FASTA files with full validation
- 🔬 **DNA Analysis** — nucleotide counts (A/T/C/G), GC%/AT%, reverse, reverse complement, RNA transcription, protein translation
- 🧪 **Mutation Generator** — insertion, deletion, and substitution mutations at any position, with FASTA export
- 🔗 **Sequence Comparison** — identity %, match count, Hamming distance
- 🧬 **Pairwise Alignment** — global or local alignment via Biopython's `PairwiseAligner`
- 📊 **Graph Dashboard** — visualize nucleotide composition, GC%, and length across sequences, downloadable as PNG
- 📄 **PDF Report Generator** — a complete report with summaries, graphs, comparisons, and alignments

---





## ⚙️ Installation

### Requirements
- Python 3.9 or higher
- pip

### Setup

```bash
git clone https://github.com/your-username/BioDNA-Inspector.git
cd BioDNA-Inspector
pip install -r requirements.txt
```

---

## ▶️ How to Run

### Terminal version

```bash
python main.py
```

### Streamlit web version

```bash
streamlit run app.py
```

Then open the local URL shown in your terminal (usually `http://localhost:8501`).

---

## 🗂️ Project Structure

```
BioDNA_Inspector/
│
├── app.py             # Streamlit web application (frontend)
├── main.py             # Terminal application (frontend)
├── analysis.py          # FASTA loading + DNA composition analysis backend
├── mutation.py          # Insertion / deletion / substitution backend
├── comparison.py        # Sequence comparison + pairwise alignment backend
├── graph.py              # Matplotlib graph dashboard backend
├── report.py             # ReportLab PDF report backend
├── utils.py               # Shared validation & CLI helper functions
├── assets/                 # Static assets (logo, images)
├── reports/                # Generated PDF reports
├── graphs/                  # Generated graph PNGs
├── mutations/                # Generated mutated FASTA files
├── requirements.txt
└── README.md
```

`main.py` and `app.py` never duplicate logic — both call into the same `analysis.py`, `mutation.py`, `comparison.py`, `graph.py`, and `report.py` backend modules.

---

## 📚 Libraries Used

- [Biopython](https://biopython.org/) — FASTA parsing, sequence operations, pairwise alignment
- [Matplotlib](https://matplotlib.org/) — composition graph dashboard
- [ReportLab](https://www.reportlab.com/) — PDF report generation
- [Streamlit](https://streamlit.io/) — web application interface
- [Pandas](https://pandas.pydata.org/) — tabular display in the web app

---

## 🚧 Future Improvements

- Multiple sequence alignment (MSA) support
- Support for protein FASTA files
- Persistent history of past analyses / reports
- User accounts and saved sessions
- Dark mode for the web interface

---

## 👤 Author

**Param**
BSc Biotechnology, Chandigarh Group of Colleges (CGC), Jhanjeri, Mohali
Affiliated with IKGPTU (Punjab Technical University)

GitHub: [github.com/your-username](https://github.com/) *(placeholder — update with your profile)*

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
