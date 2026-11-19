📄 DocDiff Auditor — Semantic Document Comparison EngineDocDiff Auditor is a lightweight, CPU-friendly semantic PDF auditing tool built to detect meaningful policy, contract, and specification changes across document revisions. Unlike traditional line-by-line diff utilities that break on reformatting, reordered clauses, or minor phrasing edits, DocDiff Auditor embeds document clauses into dense vector space and aligns them using cosine similarity.🎯 Why Semantic Diffing?Standard text diff tools (such as diff or Word redlines) compare documents at the character or token level. In real-world legal, compliance, and engineering workflows, this creates two major problems:False Positives (Noise): Moving a paragraph, changing whitespace, fixing punctuation, or rephrasing a sentence without altering its meaning floods reviewers with unnecessary redlines.Missed Semantic Shifts: Subtle obligation changes (e.g., changing a 99.9% uptime SLA to 99.5%, or extending data retention from 30 days to 90 days with storage fees) can get buried inside noisy formatting diffs.DocDiff Auditor solves this by comparing meaning instead of raw strings—automatically classifying every clause as Unchanged, Modified (Semantic Shift), Removed, or Added.✨ Key FeaturesDirect PDF Clause Extraction: Parses multi-page PDFs into clean, normalized paragraph and clause chunks using PyMuPDF (fitz).Semantic Vector Alignment: Uses the all-MiniLM-L6-v2 transformer model (sentence-transformers) to encode clauses into 384-dimensional embeddings and compute pairwise cosine similarity.Interactive Threshold Tuning: Real-time sidebar sliders allow auditors to calibrate sensitivity for exact matches vs. semantic shifts.One-Click Sample Audit Mode: Ships with a built-in baseline vs. revised Cloud SLA dataset so reviewers can test all four classification states immediately without uploading external files.Side-by-Side Visual Diff: Clean, filterable Streamlit dashboard displaying baseline text, revised text, status badges, and exact similarity scores.Exportable Audit Trails: Download structured comparison reports in CSV or JSON format for compliance logs or downstream workflows.100% Local & CPU-Ready: Runs entirely on CPU with @st.cache_resource model caching—no external LLM API keys or paid cloud inference required.🏗️ System Architectureflowchart TD
    A[Document A: Baseline PDF] --> C[PyMuPDF Extractor & Clause Chunker]
    B[Document B: Revised PDF] --> D[PyMuPDF Extractor & Clause Chunker]
    S[Built-in Sample SLA Mode] -.-> C
    S -.-> D

    C --> E[Sentence-Transformers: all-MiniLM-L6-v2]
    D --> E

    E --> F[384-D Clause Embeddings]
    F --> G[Pairwise Cosine Similarity Matrix]
    G --> H[Greedy / Best-Match Clause Alignment]

    H --> I{Threshold Classifier}
    I -->|Sim >= Upper Threshold| J[Unchanged]
    I -->|Lower <= Sim < Upper| K[Modified / Semantic Shift]
    I -->|No Match in Doc B| L[Removed]
    I -->|No Match in Doc A| M[Added]

    J & K & L & M --> N[Streamlit Audit Dashboard]
    N --> O[CSV / JSON Audit Report Export]
🔬 How It Works1. Document Extraction & Chunking (core/extractor.py)Each uploaded PDF is parsed page-by-page with PyMuPDF. Headers, excess whitespace, and broken line wraps are normalized, and text is segmented into logical clause/paragraph chunks while preserving document order.2. Dense Vector Embedding (core/comparator.py)Every chunk $c_i$ from Document A and $c_j$ from Document B is encoded using sentence-transformers/all-MiniLM-L6-v2 into unit-normalized vectors $\mathbf{u}_i, \mathbf{v}_j \in \mathbb{R}^{384}$.3. Cosine Similarity & ClassificationThe semantic similarity between clause $i$ in the baseline document and clause $j$ in the revised document is computed as:$$\text{sim}(\mathbf{u}_i, \mathbf{v}_j) = \frac{\mathbf{u}_i \cdot \mathbf{v}_j}{\Vert{}\mathbf{u}_i\Vert{} \, \Vert{}\mathbf{v}_j\Vert{}}$$Each clause is aligned to its highest-scoring counterpart and categorized using configurable thresholds (default values shown below):ClassificationConditionMeaningUnchanged$\text{sim} \ge 0.92$Identical or near-identical meaning (even if formatting or minor wording changed).Modified (Semantic Shift)$0.60 \le \text{sim} < 0.92$Same underlying clause topic, but material terms, numbers, or obligations shifted.Removed$\max_j \text{sim}(\mathbf{u}_i, \mathbf{v}_j) < 0.60$Clause existed in Baseline (Doc A) but has no semantic equivalent in Revised (Doc B).Added$\max_i \text{sim}(\mathbf{u}_i, \mathbf{v}_j) < 0.60$New clause introduced in Revised (Doc B) with no equivalent in Baseline (Doc A).📁 Project Structuredocdiff-auditor/
├── app.py                  # Streamlit UI, metrics dashboard, filters, and export controls
├── core/
│   ├── __init__.py
│   ├── extractor.py        # PyMuPDF text extraction and paragraph/clause chunking
│   ├── comparator.py       # Embedding generation, cosine similarity matrix, and alignment
│   └── sample_docs.py      # Built-in v1.0 vs. v2.0 contract clauses for instant demoing
├── requirements.txt        # Pinned lightweight Python dependencies
├── .gitignore              # Standard Python/venv ignore rules
└── README.md               # Project documentation
🚀 Quick Start (Local Setup)PrerequisitesPython 3.10 or higherpip package managerInstallation & Run# 1. Clone the repository
git clone https://github.com/yourusername/docdiff-auditor.git
cd docdiff-auditor

# 2. Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
The app will open automatically in your browser at http://localhost:8501.Note: On the first run, sentence-transformers will download the all-MiniLM-L6-v2 weights (~90 MB) and cache them locally. Subsequent runs start instantaneously.🧪 Usage GuideInstant Demo: Click "Load Sample Contract Diff" in the main panel or sidebar to run an immediate audit on a preloaded Cloud Service Level Agreement (v1.0 vs. v2.0) containing unchanged, modified, removed, and added clauses.Custom PDF Audit: Upload a Baseline PDF (Document A) and a Revised PDF (Document B) using the dual file uploaders.Tune Sensitivity:Increase the Unchanged Threshold (default 0.92) if you want to flag even subtle phrasing adjustments.Lower the Match Threshold (default 0.60) if a heavily rewritten clause is being split into separate Removed + Added entries.Filter & Export: Filter the results view by status (e.g., show only Modified and Added clauses) and export the full audit table as CSV or JSON.☁️ Deploying to Streamlit Community CloudPush this repository to a public GitHub repository.Visit share.streamlit.io and sign in with GitHub.Click New app, select your docdiff-auditor repository, set the main file path to app.py, and click Deploy.Because the app uses CPU-optimized PyTorch/Sentence-Transformers and lightweight PyMuPDF binaries, no extra packages.txt system libraries are required.🗺️ Limitations & Future RoadmapScanned PDFs: Currently optimized for digitally generated PDFs with selectable text. Adding an OCR fallback (Tesseract / PaddleOCR) is planned for scanned contracts.Cross-Encoder Reranking: Integrating an optional cross-encoder pass for borderline matches ($0.55 \le \text{sim} \le 0.70$) to improve alignment precision on dense legal tables.LLM Change Explanations: Optional local or API-based plain-English risk summaries explaining why a modified clause matters.Word-Level Highlighting Inside Modified Pairs: Highlighting exact numeric or entity shifts inside semantically matched paragraphs.👤 AuthorPushkar RamtekeB.Tech. Artificial Intelligence & Data Science — PES Modern College of Engineering, PuneGitHub · LinkedIn📄 LicenseThis project is licensed under the MIT License.
