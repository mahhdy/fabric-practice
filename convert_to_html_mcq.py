#!/usr/bin/env python3
"""
Specialized builder for 02-MCQ-50 with live selectable options, doubt toggle,
instant bubble matrix, and end-of-page ordered table.
"""

import re
import markdown

def build_mcq_interactive_html(md_text: str, answers_dict: dict, notes_dict: dict) -> str:
    header_match = re.search(r"^(#.*?)(?=\*\*Q1\.\*\*)", md_text, re.DOTALL)
    header_md = header_match.group(1) if header_match else "# ۵۰ سوال تستی\n"
    header_html = markdown.markdown(header_md)

    stats_html = """
    <div class="summary-header" style="background: var(--surface-card); border: 1.5px solid var(--border); border-radius: 14px; padding: 1.1rem 1.6rem; margin-bottom: 1.8rem; position: sticky; top: 3.8rem; z-index: 90; backdrop-filter: blur(10px); box-shadow: var(--shadow-sm);">
        <div id="score-display" style="font-size: 1.05rem; font-weight: 700;">
            تعداد پاسخ داده شده: <span style="color: var(--accent); font-size: 1.25rem; font-weight: 800;">۰ از ۵۰</span>
        </div>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
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

        correct_ans = answers_dict.get(q_num, "")
        note = notes_dict.get(q_num, "")

        note_text = f"پاسخ صحیح: <strong>گزینه {correct_ans}</strong>"
        if note:
            note_text += f"<br>💡 <strong>نکته آزمون:</strong> {note}"

        note_html = f'<div class="theory-model-answer" id="exp-{q_num}" style="margin-top: 0.8rem;">{note_text}</div>'

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

    # Matrix
    matrix_cells = []
    for q in range(1, 51):
        matrix_cells.append(
            f'<a class="matrix-cell" id="m-cell-{q}" href="#mcq-{q}">'
            f'<span class="cell-q">Q{q}</span>'
            f'<span class="cell-val">-</span>'
            f'</a>'
        )
    matrix_html = "\n".join(matrix_cells)

    # 5 Sub-tables
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
    <div class="summary-section" id="answer-sheet-section">
        <div class="summary-header">
            <h2>📊 جدول پاسخ‌نامه نهایی (ثبت زنده ۱ تا ۵۰)</h2>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
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
