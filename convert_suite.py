#!/usr/bin/env python3
"""
Comprehensive HTML generator for Microsoft Fabric (DP-600 / DP-700) Study Suite.
Features:
- Complete BiDi isolation with distinct concept cards
- Interactive 50-question MCQ Exam with live end-of-page answer sheet table
- Interactive 31-question Theory Q&A with live textarea, answer persistence,
  embedded expert model answers, and end-of-page markdown export
- Dedicated comprehensive 31 Theory Answers reference guide
- Interactive Practical Labs workbook (13 labs) with submission checklist & notes
- Search bars, copy buttons, dark mode, back-to-top, and sticky nav
"""

import os
import re
import json
from pathlib import Path
import markdown

SCRIPT_DIR = Path(__file__).parent

# ─── Load MCQ Answer Key & Notes ──────────────────────────────────────────────

def load_mcq_answers():
    answers = {}
    notes = {}
    answer_file = SCRIPT_DIR / "_AnswerKey_DontOpen.md"
    if not answer_file.exists():
        return answers, notes

    text = answer_file.read_text(encoding="utf-8")
    for match in re.finditer(r"(\d+)\s*:\s*([A-D])", text):
        answers[int(match.group(1))] = match.group(2)

    notes_section = re.search(r"Notes for grader.*?:(.*?)(?=##|\Z)", text, re.DOTALL)
    if notes_section:
        for line in notes_section.group(1).splitlines():
            line = line.strip()
            note_match = re.match(r"-\s*Q(\d+)\s*:\s*(.*)", line)
            if note_match:
                notes[int(note_match.group(1))] = note_match.group(2)
    return answers, notes

MCQ_ANSWERS, MCQ_NOTES = load_mcq_answers()

# ─── Load Theory Answers ──────────────────────────────────────────────────────

def load_theory_answers():
    answers = {}
    file_path = SCRIPT_DIR / "01-Theory-Answers.md"
    if not file_path.exists():
        return answers

    text = file_path.read_text(encoding="utf-8")
    fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    pattern = r"### سوال\s*([0-9۰-۹]+)\s*:\s*(.*?)\n(.*?)(?=(?:### سوال|\Z))"

    for match in re.finditer(pattern, text, re.DOTALL):
        q_num = int(match.group(1).translate(fa_to_en))
        title = match.group(2).strip()
        body_md = match.group(3).strip()
        body_html = markdown.markdown(body_md, extensions=["tables", "fenced_code"])
        answers[q_num] = {
            "title": title,
            "html": body_html,
            "raw": body_md
        }
    return answers

THEORY_ANSWERS = load_theory_answers()

# ─── Global Modern CSS ─────────────────────────────────────────────────────────

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg: #f8fafc;
    --surface: #ffffff;
    --surface-card: #ffffff;
    --text: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    --accent-light: #eff6ff;
    --accent-ring: rgba(37, 99, 235, 0.2);
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --code-bg: #f1f5f9;
    --code-text: #dc2626;
    --pre-bg: #0f172a;
    --pre-text: #f1f5f9;
    --blockquote-bg: #f0fdf4;
    --blockquote-border: #16a34a;
    --blockquote-text: #166534;
    --table-header-bg: #f1f5f9;
    --table-alt-bg: #f8fafc;
    --success: #16a34a;
    --success-light: #dcfce7;
    --warning: #d97706;
    --warning-light: #fef3c7;
    --error: #dc2626;
    --error-light: #fee2e2;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
}

[data-theme="dark"] {
    --bg: #0b1120;
    --surface: #1e293b;
    --surface-card: #1e293b;
    --text: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent: #3b82f6;
    --accent-hover: #60a5fa;
    --accent-light: #1e3a8a;
    --accent-ring: rgba(59, 130, 246, 0.3);
    --border: #334155;
    --border-strong: #475569;
    --code-bg: #334155;
    --code-text: #f87171;
    --pre-bg: #030712;
    --pre-text: #e2e8f0;
    --blockquote-bg: #14532d20;
    --blockquote-border: #22c55e;
    --blockquote-text: #86efac;
    --table-header-bg: #1e293b;
    --table-alt-bg: #162032;
    --success: #22c55e;
    --success-light: #14532d40;
    --warning: #f59e0b;
    --warning-light: #78350f40;
    --error: #ef4444;
    --error-light: #7f1d1d40;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.4);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.5);
}

*, *::before, *::after { box-sizing: border-box; }

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, sans-serif;
    background: var(--bg);
    color: var(--text);
    direction: rtl;
    text-align: right;
    line-height: 1.85;
    margin: 0;
    padding: 0;
    transition: background 0.25s, color 0.25s;
    -webkit-font-smoothing: antialiased;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 1.5rem 1.5rem 4rem;
}

.content-card {
    background: var(--surface);
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    padding: 2.5rem 3rem;
    margin-top: 1rem;
    position: relative;
}

/* ─── Top Bar & Navigation ─────────────────────────────────────────── */

.top-nav {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: white;
    padding: 0.75rem 2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    flex-wrap: wrap;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow);
}

.brand {
    font-weight: 800;
    font-size: 1.05rem;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
    text-decoration: none;
}

.brand span.badge-logo {
    background: #3b82f6;
    color: white;
    font-size: 0.72rem;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    font-weight: 700;
}

.nav-links {
    display: flex;
    gap: 0.35rem;
    flex-wrap: wrap;
    align-items: center;
}

.nav-links a {
    color: #cbd5e1;
    font-size: 0.86rem;
    font-weight: 500;
    padding: 0.32rem 0.7rem;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.15s;
}

.nav-links a:hover {
    background: rgba(255,255,255,0.15);
    color: white;
}

.nav-links a.active {
    background: #3b82f6;
    color: white;
    font-weight: 600;
}

.btn-icon {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
    border-radius: 8px;
    padding: 0.4rem 0.7rem;
    cursor: pointer;
    font-size: 0.88rem;
    font-family: inherit;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: background 0.15s;
}

.btn-icon:hover {
    background: rgba(255,255,255,0.2);
}

/* ─── Search Bar ───────────────────────────────────────────────────── */

.search-container {
    margin: 1.5rem 0 2rem;
    position: relative;
}

.search-input {
    width: 100%;
    padding: 0.85rem 1.2rem;
    padding-left: 2.8rem;
    border-radius: 12px;
    border: 2px solid var(--border);
    background: var(--surface);
    color: var(--text);
    font-family: inherit;
    font-size: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    outline: none;
}

.search-input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px var(--accent-ring);
}

/* ─── Headings ─────────────────────────────────────────────────────── */

h1 {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text);
    border-bottom: 3px solid var(--accent);
    padding-bottom: 0.6rem;
    margin: 0 0 1.5rem 0;
    line-height: 1.4;
}

h2 {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    border-bottom: 2px solid var(--border);
    padding-bottom: 0.45rem;
    margin: 2.2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

h3 {
    font-size: 1.18rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin: 1.6rem 0 0.8rem 0;
}

/* ─── Concept Cards (Cheatsheet) ───────────────────────────────────── */

.concept-card {
    background: var(--surface-card);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
}

.concept-card:hover {
    border-color: var(--accent);
    box-shadow: var(--shadow);
}

.concept-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
    flex-wrap: wrap;
}

.concept-badge {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    color: white;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 0.35rem 0.85rem;
    border-radius: 8px;
    direction: ltr;
    display: inline-block;
    box-shadow: var(--shadow-sm);
}

.concept-body {
    font-size: 0.95rem;
    color: var(--text);
    line-height: 1.85;
}

.concept-body ul {
    margin: 0.3rem 0;
    padding-right: 1.4rem;
}

.concept-body li {
    margin-bottom: 0.4rem;
}

/* ─── Lists & Blockquotes ──────────────────────────────────────────── */

p {
    margin: 0.7rem 0 1rem 0;
}

ul, ol {
    padding-right: 1.8rem;
    padding-left: 0;
    margin: 0.6rem 0 1.2rem 0;
}

ol[dir="ltr"], ul[dir="ltr"] {
    direction: ltr;
    text-align: left;
    padding-left: 1.8rem;
    padding-right: 0;
}

li {
    margin-bottom: 0.45rem;
    line-height: 1.9;
}

blockquote {
    background: var(--blockquote-bg);
    border-right: 4px solid var(--blockquote-border);
    border-left: none;
    margin: 1.2rem 0;
    padding: 0.9rem 1.2rem;
    border-radius: 0 10px 10px 0;
    color: var(--blockquote-text);
    font-weight: 500;
}

blockquote[dir="ltr"] {
    border-left: 4px solid var(--blockquote-border);
    border-right: none;
    border-radius: 10px 0 0 10px;
    direction: ltr;
    text-align: left;
}

/* ─── Inline Code & Code Blocks ────────────────────────────────────── */

code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88em;
    background: var(--code-bg);
    color: var(--code-text);
    padding: 0.2em 0.5em;
    border-radius: 6px;
    border: 1px solid var(--border);
    direction: ltr;
    unicode-bidi: isolate;
    white-space: nowrap;
}

pre {
    direction: ltr;
    text-align: left;
    background: var(--pre-bg);
    color: var(--pre-text);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    overflow-x: auto;
    margin: 1.2rem 0;
    box-shadow: var(--shadow-sm);
    line-height: 1.6;
    position: relative;
}

pre code {
    background: none;
    border: none;
    color: inherit;
    padding: 0;
    font-size: 0.88rem;
    white-space: pre;
    direction: ltr;
}

.copy-btn {
    position: absolute;
    top: 0.6rem;
    right: 0.6rem;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e2e8f0;
    font-size: 0.75rem;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.15s;
}

.copy-btn:hover {
    background: rgba(255,255,255,0.25);
    color: white;
}

/* ─── Tables ───────────────────────────────────────────────────────── */

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.2rem 0 1.8rem 0;
    font-size: 0.95rem;
    box-shadow: var(--shadow-sm);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
}

thead {
    background: var(--table-header-bg);
}

th {
    font-weight: 700;
    text-align: right;
    padding: 0.85rem 1.1rem;
    border-bottom: 2px solid var(--border-strong);
    color: var(--text);
    white-space: nowrap;
}

td {
    padding: 0.75rem 1.1rem;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}

tbody tr:nth-child(even) {
    background: var(--table-alt-bg);
}

tbody tr:hover {
    background: var(--accent-light);
    transition: background 0.15s;
}

/* ─── Action Buttons ───────────────────────────────────────────────── */

.btn-action {
    background: var(--surface);
    border: 1.5px solid var(--border-strong);
    color: var(--text);
    padding: 0.45rem 0.9rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    text-decoration: none;
}

.btn-action:hover {
    background: var(--accent-light);
    border-color: var(--accent);
    color: var(--accent);
}

.btn-primary {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-hover);
    color: white;
}

/* ─── MCQ Interactive Cards ────────────────────────────────────────── */

.mcq-stats {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 1.6rem;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 3.8rem;
    z-index: 90;
    backdrop-filter: blur(10px);
}

.mcq-stats-score {
    font-size: 1.05rem;
    font-weight: 700;
}

.mcq-stats-score span.score-value {
    color: var(--accent);
    font-size: 1.25rem;
}

.mcq-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.btn-action {
    background: var(--surface);
    border: 1.5px solid var(--border-strong);
    color: var(--text);
    padding: 0.45rem 0.9rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

.btn-action:hover {
    background: var(--accent-light);
    border-color: var(--accent);
    color: var(--accent);
}

.btn-primary {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-hover);
    color: white;
}

.mcq-card {
    background: var(--surface-card);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
    direction: ltr;
    text-align: left;
    transition: border-color 0.2s, box-shadow 0.2s;
    scroll-margin-top: 8rem;
}

.mcq-card:hover {
    border-color: var(--border-strong);
}

.mcq-card.is-flagged {
    border-color: var(--warning);
    background: linear-gradient(to right, var(--warning-light) 0%, var(--surface-card) 6%);
}

.mcq-card.is-answered {
    border-color: var(--accent);
}

.mcq-header {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin-bottom: 1rem;
}

.mcq-number {
    background: var(--accent-light);
    color: var(--accent);
    font-weight: 800;
    font-size: 0.88rem;
    padding: 0.25rem 0.65rem;
    border-radius: 8px;
    white-space: nowrap;
    border: 1px solid var(--accent);
}

.mcq-question {
    font-size: 1.02rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.6;
    flex: 1;
}

.mcq-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 0.7rem;
    margin-top: 0.9rem;
}

.mcq-opt {
    background: var(--bg);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.92rem;
    cursor: pointer;
    text-align: left;
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    color: var(--text);
    transition: all 0.15s;
    user-select: none;
}

.mcq-opt:hover {
    background: var(--accent-light);
    border-color: var(--accent);
}

.mcq-opt.selected {
    border-color: var(--accent);
    background: var(--accent-light);
    font-weight: 600;
    box-shadow: 0 0 0 1px var(--accent);
}

.mcq-opt.correct {
    background: var(--success-light) !important;
    border-color: var(--success) !important;
    color: var(--text) !important;
    font-weight: 700;
    box-shadow: 0 0 0 1px var(--success);
}

.mcq-opt.incorrect {
    background: var(--error-light) !important;
    border-color: var(--error) !important;
    color: var(--text) !important;
    box-shadow: 0 0 0 1px var(--error);
}

.mcq-opt-letter {
    font-weight: 800;
    color: var(--text-muted);
    min-width: 1.4rem;
}

.mcq-opt.selected .mcq-opt-letter {
    color: var(--accent);
}

.mcq-opt.correct .mcq-opt-letter {
    color: var(--success);
}

.mcq-opt.incorrect .mcq-opt-letter {
    color: var(--error);
}

.mcq-footer {
    margin-top: 1.1rem;
    padding-top: 0.9rem;
    border-top: 1px dashed var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    flex-wrap: wrap;
}

.mcq-toolbar-left {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.btn-tool {
    background: none;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    font-family: inherit;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

.btn-tool:hover {
    background: var(--bg);
    border-color: var(--border-strong);
    color: var(--text);
}

.btn-tool.flagged {
    background: var(--warning-light);
    border-color: var(--warning);
    color: var(--warning);
    font-weight: 700;
}

.mcq-toggle-answer {
    background: none;
    border: none;
    color: var(--accent);
    cursor: pointer;
    font-family: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

.mcq-toggle-answer:hover {
    text-decoration: underline;
}

.mcq-explanation {
    display: none;
    margin-top: 0.6rem;
    padding: 0.85rem 1.1rem;
    background: var(--blockquote-bg);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 0.9rem;
    color: var(--text);
    line-height: 1.6;
    width: 100%;
}

/* ─── End-of-Page Answer Sheet Table ────────────────────────────────── */

.answer-sheet-container {
    margin-top: 3.5rem;
    padding-top: 2rem;
    border-top: 3px solid var(--accent);
}

.answer-sheet-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.2rem;
}

.answer-sheet-header h2 {
    margin: 0;
    border: none;
    padding: 0;
    font-size: 1.5rem;
}

/* Bubble Matrix Grid */
.matrix-card {
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
}

.matrix-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.matrix-grid {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 0.45rem;
    direction: ltr;
}

.matrix-cell {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.4rem 0.2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
}

.matrix-cell:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
    border-color: var(--accent);
}

.matrix-cell .cell-q {
    font-size: 0.72rem;
    color: var(--text-muted);
}

.matrix-cell .cell-val {
    font-size: 0.95rem;
    font-weight: 800;
    color: var(--text-muted);
}

.matrix-cell.answered {
    background: var(--accent-light);
    border-color: var(--accent);
}
.matrix-cell.answered .cell-val {
    color: var(--accent);
}

.matrix-cell.flagged {
    background: var(--warning-light) !important;
    border-color: var(--warning) !important;
}
.matrix-cell.flagged .cell-val {
    color: var(--warning) !important;
}

.matrix-cell.correct {
    background: var(--success-light) !important;
    border-color: var(--success) !important;
}
.matrix-cell.correct .cell-val {
    color: var(--success) !important;
}

.matrix-cell.incorrect {
    background: var(--error-light) !important;
    border-color: var(--error) !important;
}
.matrix-cell.incorrect .cell-val {
    color: var(--error) !important;
}

/* Detailed Multi-Column Table */
.answer-table-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
    direction: ltr;
}

.sub-table-card {
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.sub-table-header {
    background: var(--table-header-bg);
    padding: 0.5rem 0.8rem;
    font-weight: 700;
    font-size: 0.82rem;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border);
    text-align: center;
}

.sub-table {
    width: 100%;
    margin: 0;
    border-collapse: collapse;
    font-size: 0.85rem;
    box-shadow: none;
    border: none;
}

.sub-table th, .sub-table td {
    padding: 0.45rem 0.6rem;
    text-align: center;
    border-bottom: 1px solid var(--border);
}

.sub-table th {
    font-size: 0.76rem;
    color: var(--text-muted);
    font-weight: 600;
    background: var(--bg);
}

.sub-table tbody tr:hover {
    background: var(--accent-light);
}

.cell-choice {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 0.92rem;
    color: var(--text-muted);
}

.cell-choice.active {
    color: var(--accent);
}

.cell-choice.flagged {
    color: var(--warning);
}

.cell-choice.correct {
    color: var(--success);
}

.cell-choice.incorrect {
    color: var(--error);
}

.link-jump {
    color: var(--accent);
    text-decoration: none;
    font-size: 0.78rem;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    border: 1px solid var(--border);
    transition: all 0.1s;
}

.link-jump:hover {
    background: var(--accent);
    color: white;
}

/* Output String Card */
.export-card {
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-top: 1.5rem;
}

.export-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.export-title {
    font-weight: 700;
    font-size: 0.95rem;
}

.export-textarea {
    width: 100%;
    height: 70px;
    padding: 0.7rem 0.9rem;
    border-radius: 8px;
    border: 1.5px solid var(--border);
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    line-height: 1.5;
    resize: none;
    direction: ltr;
    text-align: left;
    outline: none;
}

.export-textarea:focus {
    border-color: var(--accent);
}


/* ─── Theory Q&A Interactive Cards ─────────────────────────────────── */

.theory-card {
    background: var(--surface-card);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
    scroll-margin-top: 8rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.theory-card:hover {
    border-color: var(--border-strong);
}

.theory-card.is-answered {
    border-color: var(--accent);
}

.theory-header {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
}

.theory-num {
    background: var(--accent-light);
    color: var(--accent);
    font-weight: 800;
    font-size: 0.9rem;
    padding: 0.25rem 0.7rem;
    border-radius: 8px;
    white-space: nowrap;
    border: 1px solid var(--accent);
}

.theory-question {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.6;
    flex: 1;
    direction: ltr;
    text-align: left;
}

.theory-guide {
    background: var(--bg);
    border-right: 3px solid var(--accent);
    padding: 0.6rem 0.9rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.theory-textarea {
    width: 100%;
    min-height: 120px;
    padding: 0.85rem 1.1rem;
    border-radius: 10px;
    border: 1.5px solid var(--border);
    background: var(--surface);
    color: var(--text);
    font-family: inherit;
    font-size: 0.95rem;
    line-height: 1.7;
    resize: vertical;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.theory-textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-ring);
}

.theory-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.8rem;
    flex-wrap: wrap;
    gap: 0.6rem;
}

.theory-status {
    font-size: 0.82rem;
    color: var(--text-muted);
}

.theory-model-answer {
    display: none;
    margin-top: 1.2rem;
    padding: 1.2rem 1.5rem;
    background: var(--blockquote-bg);
    border-radius: 10px;
    border-right: 4px solid var(--success);
    font-size: 0.92rem;
    line-height: 1.85;
}

.theory-model-answer h4 {
    margin: 0.8rem 0 0.3rem 0;
    color: var(--success);
    font-size: 1rem;
}

/* ─── Practical Labs Workbook Cards ────────────────────────────────── */

.lab-card {
    background: var(--surface-card);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
    scroll-margin-top: 8rem;
}

.lab-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.8rem;
}

.lab-num {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: white;
    font-weight: 800;
    font-size: 0.9rem;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    white-space: nowrap;
}

.lab-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: var(--text);
}

.lab-checklist {
    background: var(--bg);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin-top: 1rem;
}

.lab-checklist-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.lab-check-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.35rem;
    font-size: 0.9rem;
    cursor: pointer;
}

/* ─── End-of-Page Summary Tables ───────────────────────────────────── */

.summary-section {
    margin-top: 3.5rem;
    padding-top: 2rem;
    border-top: 3px solid var(--accent);
}

.summary-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.2rem;
}

.summary-header h2 {
    margin: 0;
    border: none;
    padding: 0;
    font-size: 1.45rem;
}

/* ─── Back to top button ───────────────────────────────────────────── */

#back-to-top {
    position: fixed;
    bottom: 2rem;
    left: 2rem;
    background: var(--accent);
    color: white;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: none;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    box-shadow: var(--shadow-lg);
    z-index: 99;
    transition: transform 0.2s, background 0.2s;
}

#back-to-top:hover {
    background: var(--accent-hover);
    transform: scale(1.08);
}

/* ─── Index Grid ───────────────────────────────────────────────────── */

.file-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
    gap: 1.3rem;
    margin-top: 1.8rem;
}

.file-card {
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.6rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
}

.file-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-3px);
    border-color: var(--accent);
}

.file-card h3 {
    margin: 0 0 0.5rem 0;
    color: var(--accent);
    font-size: 1.15rem;
    border: none;
}

.file-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.92rem;
    flex: 1;
}

.file-card .badge {
    align-self: flex-start;
    display: inline-block;
    background: var(--accent-light);
    color: var(--accent);
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    margin-top: 1rem;
}

@media print {
    body { background: white !important; color: black !important; }
    .container { max-width: 100%; padding: 0; }
    .content-card { box-shadow: none; border: none; padding: 0; }
    .top-nav, #back-to-top, .search-container, .btn-action { display: none !important; }
    pre { background: #f1f5f9 !important; color: #000 !important; }
}

@media (max-width: 768px) {
    .container { padding: 0.8rem; }
    .content-card { padding: 1.4rem; border-radius: 12px; }
    .top-nav { padding: 0.6rem 1rem; }
}
"""

# ─── Navigation Bar Items ─────────────────────────────────────────────────────

NAV_ITEMS = [
    ("index.html", "📂 فهرست"),
    ("00-Cheatsheet.html", "📋 برگه تقلب"),
    ("01-Theory-Questions.html", "📝 سوالات نظری"),
    ("01-Theory-Answers.html", "💡 پاسخ‌نامه تشریحی"),
    ("02-MCQ-50.html", "⚡ آزمون تستی"),
    ("03-Practical-Labs.html", "🔬 تمرین‌های عملی"),
    ("04-Resources.html", "📚 منابع"),
    ("_AnswerKey_DontOpen.html", "🔑 کلید تست"),
]

def build_nav_html(active_file: str) -> str:
    links = []
    for href, label in NAV_ITEMS:
        cls = ' class="active"' if href == active_file else ""
        links.append(f'<a href="{href}"{cls}>{label}</a>')
    return (
        '<div class="top-nav">\n'
        '  <a href="index.html" class="brand">📘 Fabric Prep <span class="badge-logo">DP-600 / DP-700</span></a>\n'
        '  <div class="nav-links">\n'
        "    " + "\n    ".join(links) + "\n"
        "  </div>\n"
        '  <button class="btn-icon" id="theme-toggle-btn" onclick="toggleTheme()" title="تغییر تم">🌙 تم تاریک</button>\n'
        "</div>\n"
    )

# ─── JavaScript Runtime ────────────────────────────────────────────────────────

JS_SCRIPTS = r"""
<script>
// Theme Toggle
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('fabric-theme', newTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.innerHTML = isDark ? '☀️ تم روشن' : '🌙 تم تاریک';
}

(function() {
    const saved = localStorage.getItem('fabric-theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', saved);
    window.addEventListener('DOMContentLoaded', updateThemeIcon);
})();

// Copy Code Button & Back to Top
window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('pre').forEach(pre => {
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.innerText = 'کپی';
        btn.onclick = () => {
            const code = pre.querySelector('code')?.innerText || pre.innerText;
            navigator.clipboard.writeText(code).then(() => {
                btn.innerText = 'کپی شد! ✓';
                setTimeout(() => btn.innerText = 'کپی', 2000);
            });
        };
        pre.appendChild(btn);
    });

    const btt = document.getElementById('back-to-top');
    if (btt) {
        window.onscroll = () => {
            if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
                btt.style.display = 'flex';
            } else {
                btt.style.display = 'none';
            }
        };
        btt.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

// Search Filter (Cheatsheet & Theory Answers)
function filterContent(inputId, cardClass) {
    const query = document.getElementById(inputId).value.toLowerCase().trim();
    document.querySelectorAll('.' + cardClass).forEach(el => {
        const text = el.innerText.toLowerCase();
        el.style.display = (query === '' || text.includes(query)) ? '' : 'none';
    });
}

// ─── Theory Questions Q&A Runtime ──────────────────────────────────────────

const TOTAL_THEORY = 31;
let theoryAnswers = {};

try {
    const saved = localStorage.getItem('fabric-theory-answers');
    if (saved) theoryAnswers = JSON.parse(saved);
} catch(e) {}

function saveTheoryAnswer(qNum) {
    const txt = document.getElementById('tq-input-' + qNum)?.value || '';
    if (txt.trim()) {
        theoryAnswers[qNum] = txt;
    } else {
        delete theoryAnswers[qNum];
    }
    try {
        localStorage.setItem('fabric-theory-answers', JSON.stringify(theoryAnswers));
    } catch(e) {}
    updateTheoryCard(qNum);
    updateTheorySummary();
}

function clearTheoryAnswer(qNum) {
    const input = document.getElementById('tq-input-' + qNum);
    if (input) input.value = '';
    delete theoryAnswers[qNum];
    try {
        localStorage.setItem('fabric-theory-answers', JSON.stringify(theoryAnswers));
    } catch(e) {}
    updateTheoryCard(qNum);
    updateTheorySummary();
}

function updateTheoryCard(qNum) {
    const card = document.getElementById('theory-q-' + qNum);
    const statusEl = document.getElementById('tq-status-' + qNum);
    const val = theoryAnswers[qNum] || '';
    const words = val.trim() ? val.trim().split(/\s+/).length : 0;

    if (card) {
        if (words > 0) card.classList.add('is-answered');
        else card.classList.remove('is-answered');
    }

    if (statusEl) {
        if (words > 0) {
            statusEl.innerHTML = `✓ پاسخ داده شده (${words} کلمه)`;
            statusEl.style.color = 'var(--success)';
        } else {
            statusEl.innerHTML = 'در انتظار نگارش پاسخ...';
            statusEl.style.color = 'var(--text-muted)';
        }
    }
}

function toggleModelAnswer(qNum) {
    const el = document.getElementById('model-ans-' + qNum);
    if (!el) return;
    el.style.display = el.style.display === 'block' ? 'none' : 'block';
}

function updateTheorySummary() {
    let answeredCount = 0;
    for (let q = 1; q <= TOTAL_THEORY; q++) {
        const val = theoryAnswers[q] || '';
        const words = val.trim() ? val.trim().split(/\s+/).length : 0;
        const cellStatus = document.getElementById('ts-status-' + q);
        if (cellStatus) {
            if (words > 0) {
                cellStatus.innerHTML = `<span style="color: var(--success); font-weight: 700;">✓ ثبت شد (${words} کلمه)</span>`;
                answeredCount++;
            } else {
                cellStatus.innerHTML = `<span style="color: var(--text-muted);">-</span>`;
            }
        }
    }

    const scoreEl = document.getElementById('theory-progress-display');
    if (scoreEl) {
        scoreEl.innerHTML = `تعداد پاسخ‌های ثبت‌شده: <span style="color: var(--accent); font-weight: 800;">${answeredCount} از ${TOTAL_THEORY}</span> (${Math.round(answeredCount / TOTAL_THEORY * 100)}%)`;
    }
}

function exportTheoryMarkdown() {
    let md = '# پاسخ‌های من به سوالات نظری Fabric (answers-theory.md)\n\n';
    let count = 0;
    for (let q = 1; q <= TOTAL_THEORY; q++) {
        const ans = theoryAnswers[q];
        const card = document.getElementById('theory-q-' + q);
        const qText = card?.querySelector('.theory-question')?.innerText || `Question ${q}`;
        if (ans && ans.trim()) {
            count++;
            md += `## سوال ${q}: ${qText}\n\n${ans.trim()}\n\n---\n\n`;
        }
    }

    if (count === 0) {
        alert('شما هنوز پاسخی برای هیچ‌کدام از سوالات یادداشت نکرده‌اید.');
        return;
    }

    navigator.clipboard.writeText(md).then(() => {
        alert(`متن ${count} پاسخ با فرمت Markdown در کلیپ‌بورد کپی شد.`);
    });
}

function downloadTheoryMarkdown() {
    let md = '# پاسخ‌های من به سوالات نظری Fabric (answers-theory.md)\n\n';
    let count = 0;
    for (let q = 1; q <= TOTAL_THEORY; q++) {
        const ans = theoryAnswers[q];
        const card = document.getElementById('theory-q-' + q);
        const qText = card?.querySelector('.theory-question')?.innerText || `Question ${q}`;
        if (ans && ans.trim()) {
            count++;
            md += `## سوال ${q}: ${qText}\n\n${ans.trim()}\n\n---\n\n`;
        }
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'answers-theory.md';
    link.click();
}

function resetAllTheoryAnswers() {
    if (!confirm('آیا از پاک کردن تمامی پاسخ‌های تشریحی خود مطمئن هستید؟')) return;
    theoryAnswers = {};
    try {
        localStorage.removeItem('fabric-theory-answers');
    } catch(e) {}
    for (let q = 1; q <= TOTAL_THEORY; q++) {
        const inp = document.getElementById('tq-input-' + q);
        if (inp) inp.value = '';
        updateTheoryCard(q);
    }
    updateTheorySummary();
}

// ─── Practical Labs Runtime ────────────────────────────────────────────────

const TOTAL_LABS = 13;
let labAnswers = {};

try {
    const saved = localStorage.getItem('fabric-lab-answers');
    if (saved) labAnswers = JSON.parse(saved);
} catch(e) {}

function saveLabAnswer(labNum) {
    const txt = document.getElementById('lab-input-' + labNum)?.value || '';
    if (txt.trim()) {
        labAnswers[labNum] = txt;
    } else {
        delete labAnswers[labNum];
    }
    try {
        localStorage.setItem('fabric-lab-answers', JSON.stringify(labAnswers));
    } catch(e) {}
    updateLabSummary();
}

function updateLabSummary() {
    let answered = 0;
    for (let l = 1; l <= TOTAL_LABS; l++) {
        const val = labAnswers[l] || '';
        const cell = document.getElementById('lab-sum-status-' + l);
        if (cell) {
            if (val.trim()) {
                cell.innerHTML = '<span style="color: var(--success); font-weight: 700;">✓ تکمیل شده</span>';
                answered++;
            } else {
                cell.innerHTML = '<span style="color: var(--text-muted);">-</span>';
            }
        }
    }
    const scoreEl = document.getElementById('lab-progress-display');
    if (scoreEl) {
        scoreEl.innerHTML = `تعداد تمرین‌های انجام‌شده: <span style="color: var(--accent); font-weight: 800;">${answered} از ${TOTAL_LABS}</span>`;
    }
}

function exportLabMarkdown() {
    let md = '# گزارش تمرین‌های عملی Fabric Labs (answers-labs.md)\n\n';
    for (let l = 1; l <= TOTAL_LABS; l++) {
        const ans = labAnswers[l];
        if (ans && ans.trim()) {
            md += `## Lab ${l}\n\n${ans.trim()}\n\n---\n\n`;
        }
    }
    navigator.clipboard.writeText(md).then(() => {
        alert('گزارش تمام تمرین‌های عملی در کلیپ‌بورد کپی شد.');
    });
}

// ─── MCQ Interactive State & Live Answer Sheet Table ───────────────────────

const TOTAL_QUESTIONS = 50;
let userAnswers = {};
let userDoubts = {};
let isSubmitted = false;

// Load saved answers from localStorage
try {
    const savedAns = localStorage.getItem('fabric-mcq-answers');
    if (savedAns) userAnswers = JSON.parse(savedAns);
    const savedDoubts = localStorage.getItem('fabric-mcq-doubts');
    if (savedDoubts) userDoubts = JSON.parse(savedDoubts);
} catch(e) {}

function saveState() {
    try {
        localStorage.setItem('fabric-mcq-answers', JSON.stringify(userAnswers));
        localStorage.setItem('fabric-mcq-doubts', JSON.stringify(userDoubts));
    } catch(e) {}
}

function selectOption(qNum, optLetter) {
    if (userAnswers[qNum] === optLetter) {
        // Clicking same option deselects it
        delete userAnswers[qNum];
    } else {
        userAnswers[qNum] = optLetter;
    }
    saveState();
    updateQuestionCard(qNum);
    updateAnswerTable();
    updateScore();
}

function toggleDoubt(qNum) {
    userDoubts[qNum] = !userDoubts[qNum];
    saveState();
    updateQuestionCard(qNum);
    updateAnswerTable();
}

function clearQuestion(qNum) {
    delete userAnswers[qNum];
    delete userDoubts[qNum];
    saveState();
    updateQuestionCard(qNum);
    updateAnswerTable();
    updateScore();
}

function updateQuestionCard(qNum) {
    const card = document.getElementById('mcq-' + qNum);
    if (!card) return;

    const chosen = userAnswers[qNum];
    const isDoubt = !!userDoubts[qNum];

    // Options UI
    card.querySelectorAll('.mcq-opt').forEach(btn => {
        const optLetter = btn.getAttribute('data-opt');
        if (optLetter === chosen) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });

    // Doubt button UI
    const doubtBtn = document.getElementById('doubt-btn-' + qNum);
    if (doubtBtn) {
        if (isDoubt) {
            doubtBtn.classList.add('flagged');
            doubtBtn.innerHTML = '❓ شک دارم (علامت خورده)';
        } else {
            doubtBtn.classList.remove('flagged');
            doubtBtn.innerHTML = '❓ شک دارم';
        }
    }

    // Card border styling
    if (isDoubt) {
        card.classList.add('is-flagged');
    } else {
        card.classList.remove('is-flagged');
    }

    if (chosen) {
        card.classList.add('is-answered');
    } else {
        card.classList.remove('is-answered');
    }
}

function updateAnswerTable() {
    let resultItems = [];

    for (let q = 1; q <= TOTAL_QUESTIONS; q++) {
        const choice = userAnswers[q] || '-';
        const isDoubt = !!userDoubts[q];
        const displayVal = choice === '-' ? '-' : (choice + (isDoubt ? '?' : ''));

        // Update Matrix Cell
        const matrixCell = document.getElementById('m-cell-' + q);
        if (matrixCell) {
            const valEl = matrixCell.querySelector('.cell-val');
            if (valEl) valEl.innerText = displayVal;

            matrixCell.className = 'matrix-cell';
            if (choice !== '-') matrixCell.classList.add('answered');
            if (isDoubt) matrixCell.classList.add('flagged');

            if (isSubmitted) {
                const card = document.getElementById('mcq-' + q);
                const correct = card?.getAttribute('data-correct');
                if (choice === correct) matrixCell.classList.add('correct');
                else if (choice !== '-') matrixCell.classList.add('incorrect');
            }
        }

        // Update Table Cell
        const tableCell = document.getElementById('t-choice-' + q);
        if (tableCell) {
            tableCell.innerText = displayVal;
            tableCell.className = 'cell-choice';
            if (choice !== '-') tableCell.classList.add('active');
            if (isDoubt) tableCell.classList.add('flagged');

            if (isSubmitted) {
                const card = document.getElementById('mcq-' + q);
                const correct = card?.getAttribute('data-correct');
                if (choice === correct) tableCell.classList.add('correct');
                else if (choice !== '-') tableCell.classList.add('incorrect');
            }
        }

        if (choice !== '-') {
            resultItems.push(`${q}:${displayVal}`);
        }
    }

    // Update String Export
    const exportEl = document.getElementById('export-text');
    if (exportEl) {
        exportEl.value = resultItems.join(', ');
    }
}

function checkAnswers() {
    isSubmitted = true;
    let correctCount = 0;
    const cards = document.querySelectorAll('.mcq-card');

    cards.forEach(card => {
        const qNum = parseInt(card.getAttribute('data-q'));
        const correctOpt = card.getAttribute('data-correct');
        const userChoice = userAnswers[qNum];

        card.querySelectorAll('.mcq-opt').forEach(btn => {
            const optLetter = btn.getAttribute('data-opt');
            btn.classList.remove('correct', 'incorrect');
            if (optLetter === correctOpt) {
                btn.classList.add('correct');
            } else if (optLetter === userChoice && userChoice !== correctOpt) {
                btn.classList.add('incorrect');
            }
        });

        if (userChoice === correctOpt) {
            correctCount++;
        }

        // Reveal notes
        const exp = card.querySelector('.mcq-explanation');
        if (exp) exp.style.display = 'block';

        // Reveal correct column in table
        const corrCell = document.getElementById('t-correct-' + qNum);
        if (corrCell) corrCell.innerText = correctOpt;
    });

    const scoreEl = document.getElementById('score-display');
    if (scoreEl) {
        scoreEl.innerHTML = `نمره نهایی: <span class="score-value">${correctCount} از ${TOTAL_QUESTIONS}</span> (${Math.round(correctCount / TOTAL_QUESTIONS * 100)}%)`;
    }

    updateAnswerTable();

    // Scroll smoothly to answer sheet to review
    document.getElementById('answer-sheet-section')?.scrollIntoView({ behavior: 'smooth' });
}

function resetQuiz() {
    if (!confirm('آیا از پاک کردن تمام انتخاب‌ها و شروع مجدد مطمئن هستید؟')) return;
    isSubmitted = false;
    userAnswers = {};
    userDoubts = {};
    saveState();

    document.querySelectorAll('.mcq-card').forEach(card => {
        card.classList.remove('is-answered', 'is-flagged');
        card.querySelectorAll('.mcq-opt').forEach(btn => {
            btn.classList.remove('selected', 'correct', 'incorrect');
        });
        const exp = card.querySelector('.mcq-explanation');
        if (exp) exp.style.display = 'none';
    });

    for (let q = 1; q <= TOTAL_QUESTIONS; q++) {
        const doubtBtn = document.getElementById('doubt-btn-' + q);
        if (doubtBtn) {
            doubtBtn.classList.remove('flagged');
            doubtBtn.innerHTML = '❓ شک دارم';
        }
        const corrCell = document.getElementById('t-correct-' + q);
        if (corrCell) corrCell.innerText = '-';
    }

    updateAnswerTable();
    const scoreEl = document.getElementById('score-display');
    if (scoreEl) scoreEl.innerHTML = `تعداد پاسخ داده شده: <span class="score-value">۰ از ۵۰</span>`;
}

function updateScore() {
    const answered = Object.keys(userAnswers).length;
    const scoreEl = document.getElementById('score-display');
    if (scoreEl && !isSubmitted) {
        scoreEl.innerHTML = `تعداد پاسخ داده شده: <span class="score-value">${answered} از ${TOTAL_QUESTIONS}</span>`;
    }
}

function toggleExplanation(qNum) {
    const exp = document.getElementById('exp-' + qNum);
    if (!exp) return;
    exp.style.display = exp.style.display === 'block' ? 'none' : 'block';
}

function copyExportString() {
    const txt = document.getElementById('export-text');
    if (!txt || !txt.value) return;
    navigator.clipboard.writeText(txt.value).then(() => {
        const btn = document.getElementById('copy-export-btn');
        if (btn) {
            btn.innerText = 'کپی شد! ✓';
            setTimeout(() => btn.innerText = '📋 کپی متن پاسخ‌ها', 2000);
        }
    });
}

// Restore state on load
window.addEventListener('DOMContentLoaded', () => {
    for (let q = 1; q <= TOTAL_QUESTIONS; q++) {
        updateQuestionCard(q);
    }
    updateAnswerTable();
    updateScore();
});

// Initialize on Load
window.addEventListener('DOMContentLoaded', () => {
    // Theory init
    for (let q = 1; q <= TOTAL_THEORY; q++) {
        const inp = document.getElementById('tq-input-' + q);
        if (inp && theoryAnswers[q]) {
            inp.value = theoryAnswers[q];
        }
        updateTheoryCard(q);
    }
    updateTheorySummary();

    // Lab init
    for (let l = 1; l <= TOTAL_LABS; l++) {
        const inp = document.getElementById('lab-input-' + l);
        if (inp && labAnswers[l]) {
            inp.value = labAnswers[l];
        }
    }
    updateLabSummary();
});
</script>
"""

# ─── Builder: Cheatsheet HTML ─────────────────────────────────────────────────

def build_cheatsheet_html(md_text: str) -> str:
    """Builds a pristine Cheatsheet with distinct concept cards."""
    # Convert concept badges: ### [ Concept Name ] -> styled card
    pattern = r"###\s*\[\s*(.*?)\s*\]\n(.*?)(?=(?:###|\n##|\Z))"

    search_box = """
    <div class="search-container">
        <input type="text" id="cheatsheet-search" class="search-input" 
               placeholder="🔍 جستجو در مفاهیم برگه تقلب (مثلاً: OneLake, Delta, RLS, Direct Lake, V-Order, KQL)..." 
               oninput="filterContent('cheatsheet-search', 'concept-card')">
    </div>
    """

    sections = re.split(r"\n(?=##\s+)", md_text)
    header_html = markdown.markdown(sections[0], extensions=["tables"])

    cards_html = []
    for sec in sections[1:]:
        sec_title_match = re.match(r"##\s+(.*?)\n", sec)
        sec_title = sec_title_match.group(1) if sec_title_match else ""
        cards_html.append(f'<h2 dir="auto">{sec_title}</h2>')

        # Check for tables
        if "|---" in sec:
            table_part = re.search(r"(\|.*?\n(?:\|.*?\n)+)", sec)
            if table_part:
                cards_html.append(markdown.markdown(table_part.group(1), extensions=["tables"]))

        # Match concept cards
        for match in re.finditer(pattern, sec, re.DOTALL):
            term = match.group(1).strip()
            body_md = match.group(2).strip()
            body_html = markdown.markdown(body_md, extensions=["fenced_code"])

            card = f"""
            <div class="concept-card">
                <div class="concept-header">
                    <span class="concept-badge">{term}</span>
                </div>
                <div class="concept-body" dir="auto">
                    {body_html}
                </div>
            </div>
            """
            cards_html.append(card)

    return header_html + search_box + "\n".join(cards_html)

# ─── Builder: Interactive Theory Questions HTML ───────────────────────────────

def build_theory_questions_html(md_text: str) -> str:
    """Builds interactive Q&A format for the 31 Theory Questions."""
    header_match = re.search(r"^(#.*?)(?=\n##\s+A\.)", md_text, re.DOTALL)
    header_md = header_match.group(1) if header_match else "# سوالات نظری و تشریحی\n"
    header_html = markdown.markdown(header_md)

    stats_bar = """
    <div class="summary-header" style="background: var(--surface-card); border: 1.5px solid var(--border); border-radius: 12px; padding: 1rem 1.5rem; margin: 1.5rem 0;">
        <div id="theory-progress-display" style="font-size: 1.05rem; font-weight: 700;">
            تعداد پاسخ‌های ثبت‌شده: <span style="color: var(--accent); font-weight: 800;">۰ از ۳۱</span>
        </div>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <a href="#theory-summary-section" class="btn-action">📊 جدول بازبینی و خروجی</a>
            <button class="btn-action btn-primary" onclick="exportTheoryMarkdown()">📋 کپی پاسخ‌ها (Markdown)</button>
            <button class="btn-action" onclick="downloadTheoryMarkdown()">💾 دانلود فایل .md</button>
        </div>
    </div>
    """

    sections = re.split(r"\n(?=##\s+[A-H]\.)", md_text)
    cards_html = []
    summary_rows = []

    for sec in sections[1:]:
        sec_title = sec.split("\n")[0].replace("##", "").strip()
        cards_html.append(f'<h2 dir="auto">{sec_title}</h2>')

        qs = list(re.finditer(r"\n(\d+)\.\s+(.*?)(?=(?:\n\d+\.|\Z))", sec, re.DOTALL))
        for qm in qs:
            q_num = int(qm.group(1))
            q_text = qm.group(2).strip()

            # Model answer lookup
            model_ans = THEORY_ANSWERS.get(q_num, {})
            model_html = model_ans.get("html", "<p>پاسخ در حال تدوین است.</p>")

            card = f"""
            <div class="theory-card" id="theory-q-{q_num}">
                <div class="theory-header">
                    <span class="theory-num">Q{q_num}</span>
                    <div class="theory-question">{q_text}</div>
                </div>
                <div class="theory-guide" dir="auto">
                    📌 <strong>چارچوب پاسخ ایده‌آل:</strong> ۱. تعریف دقیق ۲. معماری و نحوه کارکرد ۳. سناریوی عملیاتی، مثال و تحلیل Trade-off
                </div>
                <textarea class="theory-textarea" id="tq-input-{q_num}" 
                          placeholder="پاسخ، توضیحات یا سناریوی مد نظر خود را اینجا تایپ کنید (فارسی یا انگلیسی)..."
                          oninput="saveTheoryAnswer({q_num})"></textarea>
                <div class="theory-footer">
                    <div class="theory-status" id="tq-status-{q_num}">در انتظار نگارش پاسخ...</div>
                    <div style="display: flex; gap: 0.4rem;">
                        <button class="btn-action" onclick="toggleModelAnswer({q_num})">
                            💡 مشاهده پاسخ مدل و مرجع
                        </button>
                        <button class="btn-action" onclick="clearTheoryAnswer({q_num})">
                            ✕ پاک کردن
                        </button>
                    </div>
                </div>
                <div class="theory-model-answer" id="model-ans-{q_num}" dir="auto">
                    <div style="font-weight: 800; color: var(--success); margin-bottom: 0.6rem;">
                        ✓ نمونه پاسخ مدل و معمار داده (Model Answer):
                    </div>
                    {model_html}
                </div>
            </div>
            """
            cards_html.append(card)

            # Summary row
            summary_rows.append(
                f'<tr>'
                f'<td><strong>Q{q_num}</strong></td>'
                f'<td style="font-size: 0.88rem; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{q_text}</td>'
                f'<td id="ts-status-{q_num}">-</td>'
                f'<td><a class="btn-action" href="#theory-q-{q_num}">ویرایش ↗</a></td>'
                f'</tr>'
            )

    summary_section = f"""
    <div class="summary-section" id="theory-summary-section">
        <div class="summary-header">
            <h2>📊 جدول جمع‌بندی پاسخ‌های تشریحی (۱ تا ۳۱)</h2>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <button class="btn-action btn-primary" onclick="exportTheoryMarkdown()">📋 کپی پاسخ‌ها (Markdown)</button>
                <button class="btn-action" onclick="downloadTheoryMarkdown()">💾 دانلود فایل answers-theory.md</button>
                <button class="btn-action" onclick="resetAllTheoryAnswers()">↺ پاک کردن همه</button>
            </div>
        </div>
        <p dir="auto" style="color: var(--text-secondary); margin-bottom: 1.2rem;">
            پاسخ‌های شما به صورت خودکار در حافظه مرورگر ذخیره شده‌اند. با کلیک روی دکمه‌های بالا می‌توانید کل پاسخ‌ها را جهت ارائه، ارسال یا بایگانی دانلود یا کپی نمایید.
        </p>
        <table>
            <thead>
                <tr>
                    <th>شماره</th>
                    <th>موضوع سوال</th>
                    <th>وضعیت نگارش شما</th>
                    <th>عملیات</th>
                </tr>
            </thead>
            <tbody>
                {"".join(summary_rows)}
            </tbody>
        </table>
    </div>
    """

    return header_html + stats_bar + "\n".join(cards_html) + summary_section

# ─── Builder: Dedicated Theory Answers HTML ───────────────────────────────────

def build_theory_answers_html(md_text: str) -> str:
    """Builds the comprehensive reference guide for all 31 Theory Answers."""
    search_box = """
    <div class="search-container">
        <input type="text" id="answers-search" class="search-input" 
               placeholder="🔍 جستجو در متن پاسخ‌های تشریحی (مثلاً: OneLake, Medallion, Direct Lake, RLS, Star Schema, Smoothing)..." 
               oninput="filterContent('answers-search', 'theory-answer-card')">
    </div>
    """

    sections = re.split(r"\n(?=##\s+بخش)", md_text)
    header_html = markdown.markdown(sections[0])

    cards_html = []
    fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

    for sec in sections[1:]:
        sec_title = sec.split("\n")[0].replace("##", "").strip()
        cards_html.append(f'<h2 dir="auto">{sec_title}</h2>')

        pattern = r"### سوال\s*([0-9۰-۹]+)\s*:\s*(.*?)\n(.*?)(?=(?:### سوال|\Z))"
        for match in re.finditer(pattern, sec, re.DOTALL):
            q_num = match.group(1).translate(fa_to_en)
            title = match.group(2).strip()
            body_md = match.group(3).strip()
            body_html = markdown.markdown(body_md, extensions=["tables", "fenced_code"])

            card = f"""
            <div class="concept-card theory-answer-card" id="ans-{q_num}" style="margin-bottom: 2rem;">
                <div class="concept-header">
                    <span class="concept-badge">سوال {q_num}</span>
                    <span style="font-weight: 800; font-size: 1.05rem; color: var(--text);">{title}</span>
                </div>
                <div class="concept-body" dir="auto">
                    {body_html}
                </div>
            </div>
            """
            cards_html.append(card)

    return header_html + search_box + "\n".join(cards_html)

# ─── Builder: Practical Labs HTML ─────────────────────────────────────────────

def build_practical_labs_html(md_text: str) -> str:
    """Builds interactive workbook for the 13 Practical Labs."""
    header_match = re.search(r"^(#.*?)(?=\n##\s+Lab\s+1)", md_text, re.DOTALL)
    header_md = header_match.group(1) if header_match else "# تمرین‌های عملی (Labs)\n"
    header_html = markdown.markdown(header_md)

    stats_bar = """
    <div class="summary-header" style="background: var(--surface-card); border: 1.5px solid var(--border); border-radius: 12px; padding: 1rem 1.5rem; margin: 1.5rem 0;">
        <div id="lab-progress-display" style="font-size: 1.05rem; font-weight: 700;">
            تعداد تمرین‌های انجام‌شده: <span style="color: var(--accent); font-weight: 800;">۰ از ۱۳</span>
        </div>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <a href="#lab-summary-section" class="btn-action">📊 جدول خلاصه تمرین‌ها</a>
            <button class="btn-action btn-primary" onclick="exportLabMarkdown()">📋 کپی گزارش تمرین‌ها (Markdown)</button>
        </div>
    </div>
    """

    labs = list(re.finditer(r"##\s+Lab\s+(\d+)\s*-\s*(.*?)\n(.*?)(?=(?:##\s+Lab|\n---\n|\Z))", md_text, re.DOTALL))
    cards_html = []
    summary_rows = []

    for match in labs:
        lab_num = int(match.group(1))
        lab_title = match.group(2).strip()
        body_md = match.group(3).strip()
        body_html = markdown.markdown(body_md, extensions=["fenced_code"])

        card = f"""
        <div class="lab-card" id="lab-{lab_num}">
            <div class="lab-header">
                <span class="lab-num">Lab {lab_num}</span>
                <span class="lab-title">{lab_title}</span>
            </div>
            <div dir="auto" style="line-height: 1.85; margin-bottom: 1rem;">
                {body_html}
            </div>
            <div style="margin-top: 1rem;">
                <label style="font-weight: 700; font-size: 0.88rem; color: var(--text-secondary); display: block; margin-bottom: 0.4rem;">
                    📝 گزارش، اسکریپت، خروجی و نکات شما برای Lab {lab_num}:
                </label>
                <textarea class="theory-textarea" id="lab-input-{lab_num}" 
                          placeholder="کدها، تعداد ردیف‌ها، نتایج تست و توضیح تصمیم‌هاتون رو اینجا یادداشت کنید..."
                          oninput="saveLabAnswer({lab_num})"></textarea>
            </div>
        </div>
        """
        cards_html.append(card)

        summary_rows.append(
            f'<tr>'
            f'<td><strong>Lab {lab_num}</strong></td>'
            f'<td>{lab_title}</td>'
            f'<td id="lab-sum-status-{lab_num}">-</td>'
            f'<td><a class="btn-action" href="#lab-{lab_num}">ورود به تمرین ↗</a></td>'
            f'</tr>'
        )

    # Extra SQL/KQL section
    extra_match = re.search(r"##\s+تمرین SQL/KQL/DAX بیشتر.*", md_text, re.DOTALL)
    extra_html = markdown.markdown(extra_match.group(0)) if extra_match else ""

    summary_section = f"""
    <div class="summary-section" id="lab-summary-section">
        <div class="summary-header">
            <h2>📊 جدول وضعیت تکمیل ۱۳ لب عملی</h2>
            <button class="btn-action btn-primary" onclick="exportLabMarkdown()">📋 کپی کل گزارش‌ها</button>
        </div>
        <table>
            <thead>
                <tr>
                    <th>شماره لب</th>
                    <th>عنوان تمرین</th>
                    <th>وضعیت</th>
                    <th>عملیات</th>
                </tr>
            </thead>
            <tbody>
                {"".join(summary_rows)}
            </tbody>
        </table>
    </div>
    """

    return header_html + stats_bar + "\n".join(cards_html) + summary_section + extra_html

# ─── Template Wrapper ──────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="auto" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Fabric Prep</title>
    <style>
{css}
    </style>
</head>
<body>
{nav}
<div class="container">
    <div class="content-card">
{body}
    </div>
</div>
<button id="back-to-top" title="بازگشت به بالا">↑</button>
{js}
</body>
</html>
"""

# ─── Main Pipeline ────────────────────────────────────────────────────────────

FILE_META = {
    "00-Cheatsheet": {
        "title": "برگه تقلب Fabric",
        "desc": "مفاهیم کلیدی معماری، دلتا لیک و ابزارها با کارت‌های ساخت‌یافته و بدون تداخل متنی",
        "badge": "📋 مرجع سریع",
        "order": 0,
    },
    "01-Theory-Questions": {
        "title": "سوالات نظری و تشریحی",
        "desc": "۳۱ سوال تخصصی مصاحبه به همراه محیط نگارش، پاسخ مرجع و خروجی Markdown",
        "badge": "📝 ۳۱ سوال تشریحی",
        "order": 1,
    },
    "01-Theory-Answers": {
        "title": "پاسخ‌نامه جامع تشریحی",
        "desc": "پاسخ‌نامه مرجع و کارشناسی شده برای تمامی ۳۱ سوال نظری بر اساس ۳ اصل مصاحبه",
        "badge": "💡 پاسخ‌نامه کامل",
        "order": 2,
    },
    "02-MCQ-50": {
        "title": "آزمون تستی ۵۰ سوالی",
        "desc": "کوئیز تعاملی با گزینه‌های انتخابی، علامت شک، ماتریس حبابی و تصحیح هوشمند",
        "badge": "⚡ آزمون تعاملی ۵۰ تستی",
        "order": 3,
    },
    "03-Practical-Labs": {
        "title": "تمرین‌های عملی (Labs)",
        "desc": "دفترچه کار تعاملی برای ۱۳ تمرین عملی به همراه چک‌لیست و ثبت گزارش",
        "badge": "🔬 ۱۳ لب کاربردی",
        "order": 4,
    },
    "04-Resources": {
        "title": "منابع و نقشه‌ی راه",
        "desc": "بهترین مراجع، ابزارهای تخصصی، کانال‌های معتبر و مسیر یادگیری پیشنهادی",
        "badge": "📚 منابع معتبر",
        "order": 5,
    },
    "_AnswerKey_DontOpen": {
        "title": "کلید آزمون تستی و داده‌های پنهان",
        "desc": "پاسخ‌نامه تست‌ها و اشکالات تعبیه‌شده در فایل‌های داده تمرین عملی",
        "badge": "🔑 کلید پاسخ‌ها",
        "order": 6,
    },
}

def build_index_html() -> str:
    cards = []
    for stem, meta in sorted(FILE_META.items(), key=lambda x: x[1]["order"]):
        html_file = stem + ".html"
        cards.append(
            f'<a class="file-card" href="{html_file}">\n'
            f'  <h3>{meta["title"]}</h3>\n'
            f'  <p>{meta["desc"]}</p>\n'
            f'  <span class="badge">{meta["badge"]}</span>\n'
            f"</a>"
        )

    body = (
        "<h1>📘 پرتال جامع آمادگی آزمون و مصاحبه Microsoft Fabric</h1>\n"
        '<p dir="auto" style="font-size: 1.05rem; color: var(--text-secondary);">'
        'این مجموعه آموزشی و تعاملی به طور اختصاصی برای تسلط بر مهندسی داده، انبار داده و تحلیل هوش تجاری در پلتفرم Microsoft Fabric و آمادگی آزمون‌های بین‌المللی <strong>DP-600</strong> و <strong>DP-700</strong> طراحی شده است.'
        '</p>\n'
        '<div class="file-grid">\n'
        + "\n".join(cards)
        + "\n</div>"
    )

    nav = build_nav_html("index.html")
    return HTML_TEMPLATE.format(
        title="پرتال راهنما",
        css=CSS,
        nav=nav,
        body=body,
        js=JS_SCRIPTS
    )

def main():
    md_files = sorted(SCRIPT_DIR.glob("*.md"))
    print(f"Converting {len(md_files)} markdown files...")

    # Load 02-MCQ-50 generator from previous step
    # Import the specialized parser
    import importlib.util
    
    for md_path in md_files:
        stem = md_path.stem
        text = md_path.read_text(encoding="utf-8")
        meta = FILE_META.get(stem, {"title": stem})

        if stem == "00-Cheatsheet":
            body = build_cheatsheet_html(text)
        elif stem == "01-Theory-Questions":
            body = build_theory_questions_html(text)
        elif stem == "01-Theory-Answers":
            body = build_theory_answers_html(text)
        elif stem == "02-MCQ-50":
            # Read existing updated MCQ parser logic or run specialized builder
            # Use convert_to_html's build_mcq_interactive_html
            from convert_to_html_mcq import build_mcq_interactive_html
            body = build_mcq_interactive_html(text, MCQ_ANSWERS, MCQ_NOTES)
        elif stem == "03-Practical-Labs":
            body = build_practical_labs_html(text)
        else:
            body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])

        nav = build_nav_html(stem + ".html")
        out_path = md_path.with_suffix(".html")
        full_html = HTML_TEMPLATE.format(
            title=meta.get("title", stem),
            css=CSS,
            nav=nav,
            body=body,
            js=JS_SCRIPTS
        )
        out_path.write_text(full_html, encoding="utf-8")
        print(f"  ✓ {md_path.name} -> {out_path.name}")

    index_html = build_index_html()
    index_path = SCRIPT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print("  ✓ index.html")

    print("\nAll files successfully built and integrated!")

if __name__ == "__main__":
    main()
