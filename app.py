import re
import arxiv
import pdfplumber
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

st.set_page_config(page_title="Research Project Website Generator", page_icon="🔬", layout="centered")

openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def fetch_arxiv_paper(url: str) -> dict:
    """Extract ArXiv ID from URL and fetch paper metadata."""
    match = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]+)", url)
    if not match:
        raise ValueError("Could not find a valid ArXiv ID in the URL.")

    arxiv_id = match.group(1)
    client = arxiv.Client()
    results = list(client.results(arxiv.Search(id_list=[arxiv_id])))
    if not results:
        raise ValueError(f"No paper found for ArXiv ID: {arxiv_id}")

    paper = results[0]
    return {
        "title": paper.title,
        "authors": ", ".join(a.name for a in paper.authors),
        "abstract": paper.summary,
    }


st.title("Research Project Website Generator")
st.markdown(
    "Turn your research paper into a polished project website in seconds. "
    "Paste your links below and we'll do the rest."
)

st.divider()

mode = st.radio("Paper source", ["Fetch from ArXiv", "Manual Entry"], horizontal=True)

st.divider()

# --- Paper metadata inputs ---
if mode == "Fetch from ArXiv":
    arxiv_url = st.text_input("ArXiv URL", placeholder="https://arxiv.org/abs/2301.00001")
else:
    title_input = st.text_input("Title")
    authors_input = st.text_input("Authors", placeholder="Alice Smith, Bob Jones")
    abstract_input = st.text_area("Abstract", height=200)

# --- Always-visible link inputs ---
st.divider()
github_url = st.text_input("GitHub URL", placeholder="https://github.com/username/repo")
youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

# --- Optional PDF upload ---
st.divider()
uploaded_pdf = st.file_uploader(
    "Upload paper PDF (optional but recommended for accuracy)",
    type="pdf",
)
full_paper_text = ""
if uploaded_pdf is not None:
    with pdfplumber.open(uploaded_pdf) as pdf:
        full_paper_text = "\n".join(
            page.extract_text() or "" for page in pdf.pages
        )
    st.success(f"PDF loaded: {len(full_paper_text):,} characters extracted from {len(pdf.pages)} pages.")

st.divider()

if st.button("Generate Website", type="primary", use_container_width=True):
    if mode == "Fetch from ArXiv":
        if not arxiv_url:
            st.error("Please enter an ArXiv URL.")
            st.stop()
        with st.spinner("Fetching paper details..."):
            try:
                paper = fetch_arxiv_paper(arxiv_url)
                title, authors, abstract = paper["title"], paper["authors"], paper["abstract"]
            except ValueError as e:
                st.error(str(e))
                st.stop()
    else:
        if not title_input or not authors_input or not abstract_input:
            st.error("Please fill in the Title, Authors, and Abstract fields.")
            st.stop()
        title, authors, abstract = title_input, authors_input, abstract_input

    paper_text_section = f"""
--- FULL PAPER TEXT (primary source — use this above all else) ---
{full_paper_text.strip()}
--- END FULL PAPER TEXT ---
""" if full_paper_text and full_paper_text.strip() else """
--- FULL PAPER TEXT ---
Not provided. Ground ALL content strictly in the Abstract below. Do not invent any facts.
--- END FULL PAPER TEXT ---
"""

    final_prompt = f"""You are an expert web developer and academic researcher. \
Generate a single-file index.html research project page following the exact spec below.

=============================================================
SECTION 1 — STRICT CONTENT GROUNDING RULES (read first)
=============================================================

RULE 1 — PAPER TEXT IS THE ONLY SOURCE OF TRUTH.
You must extract all section content (Method, Results, BibTeX) \
directly and exclusively from the paper text supplied below. \
Do not use general knowledge, do not hallucinate, do not invent results.

RULE 2 — SPECIFICS MUST BE PRESERVED VERBATIM.
If the paper mentions specific named locations (e.g. "St. John, U.S. Virgin Islands"), \
specific model names (e.g. "DINOv2"), specific architectures, specific datasets, \
or specific quantitative metrics (e.g. "75% of the target in roughly half the time"), \
you MUST reproduce those exact details in the Methodology and Results sections. \
Never replace a specific fact with a generic placeholder.

RULE 3 — BIBTEX ACCURACY.
Read the first page of the paper text carefully to extract:
  (a) The exact publication year.
  (b) The full author list in the correct order with correct spellings.
  (c) The institutional affiliations for each author.
Build the BibTeX block from these extracted values only. \
Derive the citation key as: FirstAuthorLastName + Year + FirstContentWordOfTitle \
(e.g. chen2025autonomous). Use @article if published, @misc if arXiv preprint.

RULE 4 — AFFILIATIONS MUST BE REAL.
Extract author affiliations from the paper text. \
Do NOT use "[Affiliation N]" placeholders if the paper states affiliations. \
Only use placeholders if affiliations are genuinely absent from the provided text.

RULE 5 — TONE IS PROFESSIONAL AND ACADEMIC.
All prose written for the page (Method intro, Results summary, captions) \
must match the formal, precise, third-person tone of MIT REALM lab project pages. \
No marketing language. No vague filler sentences.

=============================================================
SECTION 2 — HTML / CSS ARCHITECTURE SPEC (replicate exactly)
=============================================================

### Head
- Tailwind CSS via CDN: <script src="https://cdn.tailwindcss.com"></script>
- Inter font from Google Fonts: weights 300, 400, 500, 600, 700.
- <body> classes: `font-family: Inter`, `antialiased`, `bg-white`, `text-gray-900`.

### Embedded <style> — define these classes with EXACT values:
  .author-link      {{ color: #1a56db; text-decoration: none; }}
                    {{ &:hover {{ text-decoration: underline; }} }}
  .badge-btn        {{ display: inline-flex; align-items: center; gap: 6px;
                       padding: 8px 18px; border-radius: 9999px; font-size: 0.875rem;
                       font-weight: 500; border: 1.5px solid #d1d5db;
                       background: #fff; color: #111827; transition: all 0.15s;
                       text-decoration: none; }}
                    {{ &:hover {{ background: #f3f4f6; border-color: #9ca3af; }} }}
  .badge-btn svg    {{ width: 18px; height: 18px; }}
  .section-title    {{ font-size: 1.5rem; font-weight: 700;
                       border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem;
                       margin-bottom: 1.5rem; color: #111827; }}
  .bibtex-block     {{ background: #f8fafc; border: 1px solid #e2e8f0;
                       border-radius: 0.5rem; padding: 1.25rem;
                       font-family: 'Courier New', monospace; font-size: 0.8rem;
                       line-height: 1.7; color: #334155;
                       white-space: pre; overflow-x: auto; }}
  .placeholder-video {{ background: linear-gradient(135deg, #e0e7ef 0%, #c7d2e7 100%);
                        border-radius: 0.75rem; display: flex; flex-direction: column;
                        align-items: center; justify-content: center;
                        color: #6b7280; font-size: 0.95rem;
                        border: 2px dashed #9ca3af; }}
  .placeholder-video svg {{ margin-bottom: 0.5rem; opacity: 0.5; }}
  .affil-sup        {{ font-size: 0.7em; vertical-align: super; color: #6b7280; }}

### Spacing rules (match project_page.html exactly — do NOT omit these)
- Every top-level section div: mb-12 (3rem bottom margin).
- BibTeX section: mb-16.
- Paragraphs inside Method and Results: text-gray-700 leading-relaxed text-[0.97rem] mb-4
  (1rem gap between consecutive paragraphs).
- Placeholder divs inside a section: mb-6 when followed by another element.
- 2-column sub-figure grids: gap-4 between cells.
- Section title (.section-title): margin-bottom 1.5rem (already in class; do not override).
- Body: py padding handled per-section; no global padding on <body>.

### Page Sections — all wrapped in `max-w-4xl mx-auto px-4`

1. HEADER (pt-14 pb-6 text-center)
   - <h1> title: text-2xl sm:text-3xl font-bold leading-snug text-gray-900 mb-6.
   - Authors row: flex-wrap justify-center gap-x-4 gap-y-1. Each author is an
     <a class="author-link"> followed immediately by <span class="affil-sup">N</span>.
     Assign sequential affiliation numbers starting at 1; group authors sharing
     the same institution under the same number.
   - Affiliations row: flex-wrap justify-center, text-sm text-gray-500 mb-7.
     Each item: <span><span class="affil-sup font-semibold text-gray-600">N</span> Name</span>.
   - Badge row: flex-wrap justify-center gap-3 — three <a class="badge-btn"> elements.
     Use these EXACT inline SVG paths (viewBox="0 0 24 24", width/height via CSS):

     Paper → href = ArXiv URL (or "#").
       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
         <polyline points="14 2 14 8 20 8"/>
         <line x1="16" y1="13" x2="8" y2="13"/>
         <line x1="16" y1="17" x2="8" y2="17"/>
         <polyline points="10 9 9 9 8 9"/>
       </svg>

     Code → href = GitHub URL (or "#").
       <svg viewBox="0 0 24 24" fill="currentColor">
         <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483
           0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466
           -.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832
           .092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688
           -.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844
           a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651
           .64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855
           0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0 0 22 12.017
           C22 6.484 17.522 2 12 2z"/>
       </svg>

     Video → href = YouTube URL (or "#").
       <svg viewBox="0 0 24 24" fill="currentColor">
         <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816
           .029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62
           4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
       </svg>

2. TEASER (max-w-4xl mx-auto px-4 mb-12)
   CSS reminder: .placeholder-video MUST have background: linear-gradient(135deg, #e0e7ef 0%,
   #c7d2e7 100%), border: 2px dashed #9ca3af, border-radius: 0.75rem, display: flex,
   flex-direction: column, align-items: center, justify-content: center. NO solid gray fills.
   - <div class="placeholder-video w-full" style="height:380px">
   - Icon: monitor/play SVG (56×56, stroke-based, stroke-width="1.5", viewBox="0 0 24 24",
     opacity-50, mb-2):
       <rect x="2" y="3" width="20" height="14" rx="2"/>
       <path d="M8 21h8M12 17v4"/>
       <circle cx="10" cy="9" r="1.5"/>
       <path d="M10 13l3-3 2 2 1-1 2 2"/>
   - <p class="font-medium text-gray-500">Teaser Figure / Video</p>
   - Caption: read the paper and write a 1-sentence description of what the teaser should show
     (e.g., the robot platform, survey environment, or system overview). Use paper-specific
     language. Do NOT write "Replace with your teaser image".

3. ABSTRACT (mb-12)
   - <h2 class="section-title">Abstract</h2>
   - <p class="text-gray-700 leading-relaxed text-[0.97rem]"> with the verbatim abstract text.

4. METHOD (mb-12)
   - <h2 class="section-title">Method</h2>
   - You are an academic web editor. Use the provided full_paper_text to write
     3–4 detailed paragraphs for this section. Identify and explain:
       (a) The core innovation (e.g., the use of DINOv2 patch-level embeddings for
           one-shot detection of both target species and environmental context).
       (b) Each major system component and how they interact (e.g., the one-shot
           detector pipeline, the adaptive planner, the belief map).
       (c) The specific experimental setup (e.g., AUV survey methodology, reef sites,
           data collection approach).
     Do NOT use generic filler text. Every sentence must reference a specific idea,
     model name, or design decision found in the paper.
   - Architecture placeholder: `.placeholder-video w-full` height 300px.
     CSS: same linear-gradient + dashed border as above. NO solid gray.
     Icon: connected-nodes/flowchart SVG (48×48, stroke-based, stroke-width="1.5",
     viewBox="0 0 24 24", opacity-50, mb-2):
       <rect x="3" y="3" width="7" height="7" rx="1"/>
       <rect x="14" y="3" width="7" height="7" rx="1"/>
       <rect x="3" y="14" width="7" height="7" rx="1"/>
       <rect x="14" y="14" width="7" height="7" rx="1"/>
       <path d="M10 6.5h4M6.5 10v4M17.5 10v4M10 17.5h4"/>
     Label: use the actual name of the system or pipeline from the paper
     (e.g., "One-Shot Context-Augmented Search Pipeline"). NOT "System Architecture Diagram".
     Caption: 1 sentence from the paper describing what this diagram would show.
   - 2-column grid (grid-cols-1 sm:grid-cols-2 gap-4): two component placeholders
     (height 200px). CSS: same linear-gradient + dashed border. NO solid gray.
     Label and caption each cell with the ACTUAL component names and roles from the paper
     (e.g., "One-Shot Detector — DINOv2 patch embeddings identify target and context species",
      "Adaptive Planner — belief map integrates context rewards to guide AUV trajectory").
     Do NOT use "Component A / Component B".

5. RESULTS (mb-12)
   - <h2 class="section-title">Results</h2>
   - You are an academic web editor. Use the provided full_paper_text to write
     3–4 detailed paragraphs for this section. You MUST include:
       (a) The key quantitative takeaway with the exact metric (e.g., "samples up to
           75% of the target species in roughly half the time required by exhaustive
           coverage").
       (b) The specific evaluation setup: named sites, baselines compared against,
           and any species or target types studied.
       (c) A discussion of where and why the method outperforms baselines, citing
           specific conditions from the paper.
     Do NOT use generic filler text. No invented numbers or locations.
   - Quantitative placeholder: `.placeholder-video w-full` height 260px.
     CSS: same linear-gradient + dashed border. NO solid gray.
     Icon: bar-chart SVG (44×44, stroke-based, stroke-width="1.5", viewBox="0 0 24 24",
     opacity-50, mb-2):
       <rect x="2" y="10" width="4" height="11"/>
       <rect x="9" y="6" width="4" height="15"/>
       <rect x="16" y="3" width="4" height="18"/>
       <path d="M2 21h20"/>
     Label: derive from the paper's actual evaluation metric
     (e.g., "Figure 3: Target Coverage (%) vs. Mission Time — St. John Reef Sites").
     NOT a generic label. Caption: 1 sentence stating the key finding with exact numbers.
   - <h3 class="text-lg font-semibold text-gray-800 mb-3">Qualitative Examples</h3>
   - 2×2 grid of `.placeholder-video` divs (height 180px). CSS: same linear-gradient +
     dashed border. NO solid gray.
     Each cell: play-button SVG (32×32, filled, viewBox="0 0 24 24", opacity-50, mb-1):
       <polygon points="5 3 19 12 5 21 5 3"/>
     Label each cell with a specific figure caption derived from the paper, following the
     format "Figure N: [Condition] — [Site/Species/Baseline]"
     (e.g., "Figure 4: Context planner vs. target-only baseline — Site 1, Acropora palmata").
     Do NOT use "Site 1 — Target A" or any other generic label.

6. BIBTEX (mb-16)
   - <h2 class="section-title">BibTeX</h2>
   - <div class="bibtex-block"> with a well-formed @article or @misc entry.
     Fields: title, author (Last, First and ...), journal/booktitle, year, note if arXiv.
     ALL values extracted from the paper text — no invented fields.

7. FOOTER
   - border-t border-gray-100 py-6 text-center text-sm text-gray-400.
   - "Website template inspired by academic project pages. © [year] The Authors."

=============================================================
SECTION 3 — PAPER DATA
=============================================================
{paper_text_section}
Title:      {title}
Authors:    {authors}
Abstract:   {abstract}
ArXiv URL:  {arxiv_url if mode == "Fetch from ArXiv" else "N/A"}
GitHub URL: {github_url or "N/A"}
YouTube URL:{youtube_url or "N/A"}

=============================================================
COMPLETENESS REQUIREMENT — READ BEFORE GENERATING
=============================================================
You MUST output ALL 7 sections in full: Header, Teaser, Abstract, Method,
Results, BibTeX, Footer. Do NOT stop early. Do NOT truncate any section.
The BibTeX block and Footer MUST be present at the end of the file.
If you are running out of space, shorten prose paragraphs — but never omit
a section or leave a closing </div>, </body>, or </html> tag missing.

=============================================================
Output ONLY the raw HTML. Do not wrap in ```html or any markdown block.
============================================================="""

    with st.spinner("Generating project page with GPT-4o... this takes about 15 seconds."):
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            max_tokens=16000,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert web developer and academic web editor. "
                        "Generate a single-file index.html using Tailwind CSS via CDN. "
                        "Visual requirements (NON-NEGOTIABLE): "
                        "(1) Load the Inter font from Google Fonts (weights 300–700) and apply it to the body. "
                        "(2) Use ONLY the exact inline SVG paths supplied in the prompt for Paper, Code, and Video badges — do not substitute emoji or text. "
                        "(3) ALL figure/video placeholders MUST use the .placeholder-video class: "
                        "linear-gradient(135deg, #e0e7ef 0%, #c7d2e7 100%) background, "
                        "2px dashed #9ca3af border, border-radius 0.75rem, flex-column centering, "
                        "and a centered SVG icon with opacity 0.5. Do NOT use solid gray boxes. "
                        "(4) Apply every CSS class from the spec: .badge-btn, .section-title, "
                        ".bibtex-block, .placeholder-video, .author-link, .affil-sup. "
                        "Content requirements: Use the provided paper text as the absolute source of truth. "
                        "If the paper mentions specific methods (e.g. DINOv2), locations (e.g. St. John), "
                        "or quantitative results (e.g. 75%), these MUST appear verbatim in the Methodology "
                        "and Results sections. Write 3–4 real paragraphs per section — no filler text."
                    ),
                },
                {"role": "user", "content": final_prompt},
            ],
        )
        generated_html = response.choices[0].message.content

    st.success("Website generated!")
    st.download_button(
        label="Download index.html",
        data=generated_html,
        file_name="index.html",
        mime="text/html",
    )
    st.divider()
    st.subheader("Live Preview")
    components.html(generated_html, height=1000, scrolling=True)
