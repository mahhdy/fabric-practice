#!/usr/bin/env python3
"""
Convert Markdown files to beautifully formatted HTML with proper BiDi support.
Handles Persian (RTL) text mixed with English (LTR) technical terms.
Includes interactive MCQ exam with real-time end-of-page ordered answer sheet table,
bubble matrix, text string generator, search in cheatsheet, copy-to-clipboard,
localStorage answer persistence, and dark mode toggle.
"""

import os
import re
import json
from pathlib import Path
import markdown

SCRIPT_DIR = Path(__file__).parent

# ─── Load Answer Key & Notes ──────────────────────────────────────────────────

def load_answer_key():
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

ANSWERS_DICT, NOTES_DICT = load_answer_key()

# ─── CSS ───────────────────────────────────────────────────────────────────────

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

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
    max-width: 980px;
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
    gap: 0.4rem;
    flex-wrap: wrap;
    align-items: center;
}

.nav-links a {
    color: #cbd5e1;
    font-size: 0.88rem;
    font-weight: 500;
    padding: 0.35rem 0.75rem;
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
    font-size: 0.9rem;
    font-family: inherit;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: background 0.15s;
}

.btn-icon:hover {
    background: rgba(255,255,255,0.2);
}

/* ─── Search Bar (Cheatsheet) ──────────────────────────────────────── */

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

/* ─── Paragraphs, Lists & Blockquotes ──────────────────────────────── */

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

blockquote p {
    margin: 0.2rem 0;
}

/* ─── Inline Code & Code Blocks ────────────────────────────────────── */

code {
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace;
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

/* ─── Index Grid ───────────────────────────────────────────────────── */

.file-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

/* ─── Print ────────────────────────────────────────────────────────── */

@media print {
    body { background: white !important; color: black !important; }
    .container { max-width: 100%; padding: 0; }
    .content-card { box-shadow: none; border: none; padding: 0; }
    .top-nav, #back-to-top, .search-container, .mcq-stats { display: none !important; }
    pre { background: #f1f5f9 !important; color: #000 !important; }
}

@media (max-width: 768px) {
    .container { padding: 0.8rem; }
    .content-card { padding: 1.4rem; border-radius: 12px; }
    .top-nav { padding: 0.6rem 1rem; }
    .mcq-options { grid-template-columns: 1fr; }
    .matrix-grid { grid-template-columns: repeat(5, 1fr); }
}
"""

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

// Cheatsheet Search Filter
function filterCheatsheet() {
    const query = document.getElementById('cheatsheet-search').value.toLowerCase().trim();
    const sections = document.querySelectorAll('.content-card > *');
    let currentH2 = null;
    let sectionVisible = false;

    sections.forEach(el => {
        if (el.tagName === 'H2') {
            if (currentH2 && !sectionVisible) {
                currentH2.style.display = 'none';
            }
            currentH2 = el;
            sectionVisible = el.innerText.toLowerCase().includes(query);
            el.style.display = '';
        } else if (currentH2) {
            const matches = el.innerText.toLowerCase().includes(query);
            if (matches) sectionVisible = true;
            el.style.display = (query === '' || matches || sectionVisible) ? '' : 'none';
        }
    });

    if (currentH2 && !sectionVisible && query !== '') {
        currentH2.style.display = 'none';
    }
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
</script>
"""

# ─── File Metadata ────────────────────────────────────────────────────────────

FILE_META = {
    "00-Cheatsheet": {
        "title": "برگه تقلب Fabric",
        "desc": "خلاصه‌ی جامع معماری، ابزارها، دلتا لیک و مفاهیم آزمون DP-600/700",
        "badge": "📋 مرجع سریع",
        "order": 0,
    },
    "01-Theory-Questions": {
        "title": "سوالات نظری و تشریحی",
        "desc": "۳۱ سوال عمیق و تخصصی سبک مصاحبه‌های فنی داده",
        "badge": "📝 تشریحی (۳۱ سوال)",
        "order": 1,
    },
    "02-MCQ-50": {
        "title": "آزمون تستی ۵۰ سوالی",
        "desc": "کوئیز تعاملی با جدول ثبت زنده پاسخ‌ها، تصحیح خودکار و تولید کد پاسخ‌نامه",
        "badge": "⚡ آزمون تعاملی + جدول پاسخ‌نامه",
        "order": 2,
    },
    "03-Practical-Labs": {
        "title": "تمرین‌های عملی (Labs)",
        "desc": "۱۳ سناریوی عملی واقعی شامل مهندسی داده، مدل‌سازی و پایپ‌لاین",
        "badge": "🔬 ۱۳ لب کاربردی",
        "order": 3,
    },
    "04-Resources": {
        "title": "منابع و نقشه‌ی راه",
        "desc": "بهترین مراجع، ابزارهای کاربردی، وبلاگ‌ها و مسیر مطالعه",
        "badge": "📚 منابع معتبر",
        "order": 4,
    },
    "_AnswerKey_DontOpen": {
        "title": "کلید آزمون تستی و نکات پنهان",
        "desc": "پاسخ‌نامه‌ی آزمون تستی به همراه مشکلات تعبیه‌شده در داده‌های عملی",
        "badge": "🔑 پاسخ‌نامه",
        "order": 5,
    },
}

NAV_ITEMS = [
    ("index.html", "📂 فهرست"),
    ("00-Cheatsheet.html", "📋 برگه تقلب"),
    ("01-Theory-Questions.html", "📝 سوالات نظری"),
    ("02-MCQ-50.html", "⚡ آزمون تستی"),
    ("03-Practical-Labs.html", "🔬 تمرین‌های عملی"),
    ("04-Resources.html", "📚 منابع"),
    ("_AnswerKey_DontOpen.html", "🔑 کلید"),
]

def build_nav_html(active_file: str) -> str:
    links = []
    for href, label in NAV_ITEMS:
        cls = ' class="active"' if href == active_file else ""
        links.append(f'<a href="{href}"{cls}>{label}</a>')
    return (
        '<div class="top-nav">\n'
        '  <div class="brand">📘 Fabric Prep <span class="badge-logo">DP-600 / DP-700</span></div>\n'
        '  <div class="nav-links">\n'
        "    " + "\n    ".join(links) + "\n"
        "  </div>\n"
        '  <button class="btn-icon" id="theme-toggle-btn" onclick="toggleTheme()" title="تغییر تم">🌙 تم تاریک</button>\n'
        "</div>\n"
    )

# ─── BiDi Post-Processing ─────────────────────────────────────────────────────

def is_mostly_latin(text: str) -> bool:
    clean = re.sub(r"[^a-zA-Z\u0600-\u06FF]", "", text)
    if not clean:
        return False
    latin = len(re.findall(r"[a-zA-Z]", clean))
    return (latin / len(clean)) > 0.65

def add_dir_auto_and_align_lists(html: str) -> str:
    def fix_list(match):
        tag = match.group(1)
        attrs = match.group(2) or ""
        content = match.group(3)
        if is_mostly_latin(content):
            return f'<{tag} dir="ltr"{attrs}>{content}</{tag}>'
        return f'<{tag} dir="rtl"{attrs}>{content}</{tag}>'

    html = re.sub(r"<(ol|ul)([^>]*)>(.*?)</\1>", fix_list, html, flags=re.DOTALL)

    tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "li", "blockquote"]
    for tag in tags:
        html = re.sub(
            rf"<({tag})(\s[^>]*)?>",
            lambda m: (
                m.group(0)
                if "dir=" in (m.group(2) or "")
                else f'<{m.group(1)} dir="auto"{m.group(2) or ""}>'
            ),
            html,
        )
    return html

def isolate_inline_code(html: str) -> str:
    parts = re.split(r"(<pre[\s>].*?</pre>)", html, flags=re.DOTALL)
    for i, part in enumerate(parts):
        if part.startswith("<pre"):
            if 'dir="ltr"' not in part:
                parts[i] = part.replace("<pre", '<pre dir="ltr"', 1)
            continue
        parts[i] = re.sub(
            r"<code>(.*?)</code>",
            r'<bdi dir="ltr"><code>\1</code></bdi>',
            part,
        )
    return "".join(parts)

# ─── Specialized MCQ Parser with End-of-Page Answer Table ─────────────────────

def build_mcq_interactive_html(md_text: str) -> str:
    header_match = re.search(r"^(#.*?)(?=\*\*Q1\.\*\*)", md_text, re.DOTALL)
    header_md = header_match.group(1) if header_match else "# ۵۰ سوال تستی\n"
    
    header_html = markdown.markdown(header_md, extensions=["sane_lists"])
    header_html = add_dir_auto_and_align_lists(header_html)

    # Top stats and action bar
    stats_html = """
    <div class="mcq-stats">
        <div class="mcq-stats-score" id="score-display">
            تعداد پاسخ داده شده: <span class="score-value">۰ از ۵۰</span>
        </div>
        <div class="mcq-actions">
            <a href="#answer-sheet-section" class="btn-action">📊 جدول پاسخ‌نامه انتهایی</a>
            <button class="btn-action btn-primary" onclick="checkAnswers()">✓ تصحیح پاسخ‌ها</button>
            <button class="btn-action" onclick="resetQuiz()">↺ شروع مجدد</button>
        </div>
    </div>
    """

    pattern = r"\*\*Q(\d+)\.\*\*\s*(.*?)\n\s*A\)\s*(.*?)\s+B\)\s*(.*?)\s+C\)\s*(.*?)\s+D\)\s*(.*?)(?=(?:\n\s*\*\*Q\d+\.\*\*|\Z))"
    cards = []

    for match in re.finditer(pattern, md_text, re.DOTALL):
        q_num = int(match.group(1))
        question_text = match.group(2).strip()
        opt_a = match.group(3).strip()
        opt_b = match.group(4).strip()
        opt_c = match.group(5).strip()
        opt_d = match.group(6).strip()

        correct_ans = ANSWERS_DICT.get(q_num, "")
        note = NOTES_DICT.get(q_num, "")

        note_text = f"پاسخ صحیح: <strong>گزینه {correct_ans}</strong>"
        if note:
            note_text += f"<br>💡 <strong>نکته آزمون:</strong> {note}"

        note_html = f'<div class="mcq-explanation" id="exp-{q_num}">{note_text}</div>'

        card = f"""
        <div class="mcq-card" id="mcq-{q_num}" data-q="{q_num}" data-correct="{correct_ans}">
            <div class="mcq-header">
                <span class="mcq-number">Q{q_num}</span>
                <div class="mcq-question">{question_text}</div>
            </div>
            <div class="mcq-options">
                <div class="mcq-opt" data-opt="A" onclick="selectOption({q_num}, 'A')">
                    <span class="mcq-opt-letter">A)</span> <span>{opt_a}</span>
                </div>
                <div class="mcq-opt" data-opt="B" onclick="selectOption({q_num}, 'B')">
                    <span class="mcq-opt-letter">B)</span> <span>{opt_b}</span>
                </div>
                <div class="mcq-opt" data-opt="C" onclick="selectOption({q_num}, 'C')">
                    <span class="mcq-opt-letter">C)</span> <span>{opt_c}</span>
                </div>
                <div class="mcq-opt" data-opt="D" onclick="selectOption({q_num}, 'D')">
                    <span class="mcq-opt-letter">D)</span> <span>{opt_d}</span>
                </div>
            </div>
            <div class="mcq-footer">
                <div class="mcq-toolbar-left">
                    <button class="btn-tool" id="doubt-btn-{q_num}" onclick="toggleDoubt({q_num})">
                        ❓ شک دارم
                    </button>
                    <button class="btn-tool" onclick="clearQuestion({q_num})">
                        ✕ پاک کردن
                    </button>
                </div>
                <button class="mcq-toggle-answer" onclick="toggleExplanation({q_num})">
                    🔍 نمایش / پنهان پاسخ و نکته
                </button>
                {note_html}
            </div>
        </div>
        """
        cards.append(card)

    # ─── End-of-Page Answer Sheet Component ───────────────────────────────────
    
    # 1. Bubble Matrix (1 to 50 clickable cells)
    matrix_cells = []
    for q in range(1, 51):
        matrix_cells.append(
            f'<a class="matrix-cell" id="m-cell-{q}" href="#mcq-{q}">'
            f'<span class="cell-q">Q{q}</span>'
            f'<span class="cell-val">-</span>'
            f'</a>'
        )
    matrix_html = "\n".join(matrix_cells)

    # 2. Detailed Multi-Column Table (5 blocks of 10 questions: 1-10, 11-20, 21-30, 31-40, 41-50)
    sub_tables = []
    for block in range(5):
        start_q = block * 10 + 1
        end_q = start_q + 9
        rows = []
        for q in range(start_q, end_q + 1):
            rows.append(
                f'<tr>'
                f'<td><strong>Q{q}</strong></td>'
                f'<td class="cell-choice" id="t-choice-{q}">-</td>'
                f'<td id="t-correct-{q}">-</td>'
                f'<td><a class="link-jump" href="#mcq-{q}">پرش ↗</a></td>'
                f'</tr>'
            )
        sub_tables.append(
            f'<div class="sub-table-card">'
            f'<div class="sub-table-header">سوالات {start_q} تا {end_q}</div>'
            f'<table class="sub-table">'
            f'<thead><tr><th>سوال</th><th>انتخاب شما</th><th>کلید</th><th>لینک</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody>'
            f'</table>'
            f'</div>'
        )
    table_grid_html = "\n".join(sub_tables)

    end_sheet_html = f"""
    <div class="answer-sheet-container" id="answer-sheet-section">
        <div class="answer-sheet-header">
            <h2>📊 جدول پاسخ‌نامه نهایی (ثبت زنده ۱ تا ۵۰)</h2>
            <div class="mcq-actions">
                <button class="btn-action btn-primary" onclick="checkAnswers()">✓ تصحیح پاسخ‌ها</button>
                <a href="#score-display" class="btn-action">↑ بازگشت به بالای آزمون</a>
            </div>
        </div>
        <p dir="auto" style="color: var(--text-secondary); margin-bottom: 1.2rem;">
            با کلیک روی هر گزینه یا تغییر آن، انتخاب شما بلافاصله و به ترتیب در جدول و ماتریس زیر ثبت می‌شود. با کلیک روی هر خانه می‌توانید مستقیماً به سوال مربوطه بپرید.
        </p>

        <!-- Matrix Card -->
        <div class="matrix-card">
            <div class="matrix-title">
                <span>⚡ شبکه پاسخ‌نامه سریع (Bubble Grid)</span>
                <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">
                    🟡 زرد = شک دارم | 🔵 آبی = پاسخ داده شده | 🟢 سبز = صحیح | 🔴 قرمز = نادرست
                </span>
            </div>
            <div class="matrix-grid">
                {matrix_html}
            </div>
        </div>

        <!-- Ordered Detailed Grid Table -->
        <div class="answer-table-grid">
            {table_grid_html}
        </div>

        <!-- Export String Box -->
        <div class="export-card">
            <div class="export-header">
                <span class="export-title">📋 رشته پاسخ‌ها (جهت ارسال بر اساس دستورالعمل 1:A, 2:C, ...):</span>
                <button class="btn-action" id="copy-export-btn" onclick="copyExportString()">
                    📋 کپی متن پاسخ‌ها
                </button>
            </div>
            <textarea id="export-text" class="export-textarea" readonly placeholder="به محض انتخاب اولین گزینه، خروجی در اینجا تشکیل می‌شود..."></textarea>
        </div>
    </div>
    """

    return header_html + stats_html + "\n".join(cards) + end_sheet_html

# ─── Convert Single Markdown ──────────────────────────────────────────────────

def convert_md_to_html(md_path: Path) -> str:
    stem = md_path.stem
    text = md_path.read_text(encoding="utf-8")
    meta = FILE_META.get(stem, {"title": stem})

    if stem == "02-MCQ-50":
        body = build_mcq_interactive_html(text)
    else:
        md = markdown.Markdown(
            extensions=[
                "tables",
                "fenced_code",
                "codehilite",
                "toc",
                "smarty",
                "sane_lists",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "guess_lang": False,
                    "noclasses": True,
                },
            },
        )
        body = md.convert(text)
        body = add_dir_auto_and_align_lists(body)
        body = isolate_inline_code(body)

        if stem == "00-Cheatsheet":
            search_box = """
            <div class="search-container">
                <input type="text" id="cheatsheet-search" class="search-input" 
                       placeholder="🔍 جستجو در مفاهیم برگه تقلب (مثلاً: Direct Lake, RLS, VACUUM, Delta, Spark)..." 
                       oninput="filterCheatsheet()">
            </div>
            """
            body = re.sub(r"(</h1>)", r"\1\n" + search_box, body, count=1)

    nav = build_nav_html(stem + ".html")

    return f"""<!DOCTYPE html>
<html lang="fa" dir="auto" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta.get("title", stem)} | Fabric Prep</title>
    <style>
{CSS}
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
{JS_SCRIPTS}
</body>
</html>
"""

# ─── Index Page ───────────────────────────────────────────────────────────────

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
        "<h1>📘 راهنمای جامع آمادگی Fabric (DP-600 / DP-700)</h1>\n"
        '<p dir="auto">این مجموعه به صورت اختصاصی برای یادگیری، تمرین و آمادگی مصاحبه‌های مهندسی و تحلیل داده در پلتفرم Microsoft Fabric طراحی شده است. تمام فایل‌ها با فرمت واکنش‌گرا و قابلیت تفکیک خودکار متون دوزبانه (فارسی و انگلیسی) تنظیم شده‌اند.</p>\n'
        '<div class="file-grid">\n'
        + "\n".join(cards)
        + "\n</div>"
    )

    nav = build_nav_html("index.html")

    return f"""<!DOCTYPE html>
<html lang="fa" dir="auto" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فهرست راهنما | Fabric Prep</title>
    <style>
{CSS}
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
{JS_SCRIPTS}
</body>
</html>
"""

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    md_files = sorted(SCRIPT_DIR.glob("*.md"))
    print(f"Converting {len(md_files)} markdown files...")

    for md_path in md_files:
        html_content = convert_md_to_html(md_path)
        out_path = md_path.with_suffix(".html")
        out_path.write_text(html_content, encoding="utf-8")
        print(f"  ✓ {md_path.name} -> {out_path.name}")

    index_html = build_index_html()
    index_path = SCRIPT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print("  ✓ index.html")

    print("\nAll files successfully converted with advanced BiDi & UX enhancements!")

if __name__ == "__main__":
    main()
