"""
PDF Report Generator — professional financial due diligence report.
Light theme with high contrast for crisp readability in all PDF viewers.

Install: pip install reportlab
"""
import io
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether,
)

# ── Design Tokens (Light, Print-Safe) ─────────────────────────
WHITE       = colors.HexColor("#FFFFFF")
PAGE_BG     = colors.HexColor("#FFFFFF")
SURFACE     = colors.HexColor("#F5F6FA")
SURFACE_2   = colors.HexColor("#ECEEF6")
NAVY        = colors.HexColor("#0D0D2B")
NAVY_LIGHT  = colors.HexColor("#1A1A44")
GOLD        = colors.HexColor("#B07D1A")       # darker gold — readable on white
GOLD_LIGHT  = colors.HexColor("#F5ECD4")       # pale gold for backgrounds
GOLD_MID    = colors.HexColor("#D4A843")
BULL        = colors.HexColor("#006B3C")        # dark green
BULL_BG     = colors.HexColor("#EBF8F2")
BULL_BORDER = colors.HexColor("#00A85A")
BEAR        = colors.HexColor("#B81C35")        # dark red
BEAR_BG     = colors.HexColor("#FEF0F2")
BEAR_BORDER = colors.HexColor("#E83A55")
AMBER       = colors.HexColor("#92600A")        # dark amber
AMBER_BG    = colors.HexColor("#FEF7EC")
PURPLE      = colors.HexColor("#4C3A9E")
PURPLE_BG   = colors.HexColor("#F0EEF9")
BORDER      = colors.HexColor("#D0D4E8")
TEXT_1      = colors.HexColor("#0D0D2B")        # primary — near black
TEXT_2      = colors.HexColor("#3A3A5C")        # secondary
TEXT_3      = colors.HexColor("#6B6B90")        # muted
TEXT_4      = colors.HexColor("#9898B8")        # very muted


# ── Style Factory ──────────────────────────────────────────────
def _styles():
    def ps(name, **kw):
        base = dict(
            fontName="Helvetica", fontSize=10, textColor=TEXT_1,
            leading=16, spaceAfter=4, spaceBefore=0, backColor=None,
        )
        base.update(kw)
        return ParagraphStyle(name, **base)

    return {
        # Cover
        "cover_ticker":  ps("ct",  fontName="Helvetica-Bold", fontSize=60,
                             textColor=NAVY, alignment=TA_CENTER, leading=66, spaceAfter=6),
        "cover_company": ps("cc",  fontName="Helvetica-Bold", fontSize=18,
                             textColor=NAVY_LIGHT, alignment=TA_CENTER, spaceAfter=4),
        "cover_sub":     ps("cs",  fontSize=9, textColor=TEXT_3,
                             alignment=TA_CENTER, leading=14, spaceAfter=3),
        "cover_verdict": ps("cv",  fontName="Helvetica-Bold", fontSize=30,
                             alignment=TA_CENTER, leading=36, spaceAfter=4),
        # Body
        "h1":            ps("h1",  fontName="Helvetica-Bold", fontSize=13,
                             textColor=NAVY, spaceAfter=10, spaceBefore=4, leading=18),
        "h2":            ps("h2",  fontName="Helvetica-Bold", fontSize=10,
                             textColor=TEXT_2, spaceAfter=6, leading=14),
        "label":         ps("lbl", fontName="Helvetica-Bold", fontSize=7,
                             textColor=TEXT_3, spaceAfter=2, leading=10,
                             letterSpacing=1.2),
        "body":          ps("bd",  fontSize=10, textColor=TEXT_1,
                             leading=17, spaceAfter=5),
        "body_sm":       ps("bsm", fontSize=9, textColor=TEXT_2,
                             leading=15, spaceAfter=3),
        "mono":          ps("mn",  fontName="Courier", fontSize=8.5,
                             textColor=TEXT_2, leading=14, spaceAfter=2),
        "kpi_val":       ps("kv",  fontName="Helvetica-Bold", fontSize=14,
                             textColor=TEXT_1, leading=18, spaceAfter=0),
        "tbl_header":    ps("th",  fontName="Helvetica-Bold", fontSize=8,
                             textColor=WHITE, leading=12),
        "tbl_label":     ps("tl",  fontName="Helvetica-Bold", fontSize=8,
                             textColor=TEXT_3, leading=12, spaceAfter=0),
        "tbl_val":       ps("tv",  fontName="Helvetica-Bold", fontSize=9,
                             textColor=TEXT_1, leading=13, spaceAfter=0),
        "footer":        ps("ft",  fontSize=7, textColor=TEXT_4,
                             alignment=TA_CENTER, leading=10),
        "disclaimer":    ps("dc",  fontSize=7.5, textColor=TEXT_3,
                             leading=12, spaceAfter=3),
    }


# ── Helpers ────────────────────────────────────────────────────
def _sp(h=0.3):
    return Spacer(1, h * cm)


def _hr(color=BORDER, thickness=0.5, space_before=4, space_after=8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=space_after, spaceBefore=space_before)


def _esc(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _parse_verdict(text: str) -> dict:
    verdict, confidence, position = "HOLD", "N/A", "N/A"
    for v in ["STRONG BUY", "BUY", "SHORT", "AVOID", "HOLD"]:
        if v in text.upper():
            verdict = v
            break
    m = re.search(r'CONFIDENCE[^:]*:\s*(\d+)\s*%', text, re.IGNORECASE)
    if m:
        confidence = f"{m.group(1)}%"
    m2 = re.search(r'POSITION SIZE[^:]*:\s*([^\n\.]+)', text, re.IGNORECASE)
    if m2:
        position = m2.group(1).strip()[:35]
    return {"verdict": verdict, "confidence": confidence, "position": position}


def _verdict_color(verdict: str) -> colors.Color:
    v = verdict.upper()
    if "STRONG BUY" in v: return BULL
    if "BUY"        in v: return colors.HexColor("#007A48")
    if "SHORT"      in v: return BEAR
    if "AVOID"      in v: return colors.HexColor("#C2410C")
    return AMBER


def _verdict_bg(verdict: str) -> colors.Color:
    v = verdict.upper()
    if "BUY" in v:               return BULL_BG
    if "SHORT" in v or "AVOID" in v: return BEAR_BG
    return AMBER_BG


def _section_colors(key: str):
    """Returns (accent_color, bg_color, border_color) for a section."""
    mapping = {
        "bull":    (BULL,   BULL_BG,   BULL_BORDER),
        "bear":    (BEAR,   BEAR_BG,   BEAR_BORDER),
        "debate":  (AMBER,  AMBER_BG,  colors.HexColor("#D97706")),
        "risk":    (AMBER,  AMBER_BG,  colors.HexColor("#D97706")),
        "judge":   (GOLD,   GOLD_LIGHT, GOLD_MID),
        "planner": (PURPLE, PURPLE_BG, colors.HexColor("#6D5BD0")),
    }
    for k, v in mapping.items():
        if k in key.lower():
            return v
    return (NAVY, SURFACE, BORDER)


# ── Metrics Table ──────────────────────────────────────────────
def _metrics_table(fd: dict, S: dict, cw: float) -> Table:
    chg30  = fd.get("price_change_30d", 0)
    chg3m  = fd.get("price_change_3m", 0)
    chg1y  = fd.get("price_change_1y", 0)
    sign   = lambda x: f"{'+'if float(x or 0)>=0 else ''}{x}%"

    def pct(v):
        try:   return f"{float(v)*100:.1f}%" if v not in ("N/A", None, "") else "N/A"
        except: return str(v)

    raw = [
        ("TICKER",          fd.get("ticker", "—")),
        ("PRICE",           f"${fd.get('current_price', '—')}"),
        ("30D RETURN",      sign(chg30)),
        ("3M RETURN",       sign(chg3m)),
        ("1Y RETURN",       sign(chg1y)),
        ("MARKET CAP",      fd.get("market_cap_fmt", "N/A")),
        ("P/E (TTM)",       fd.get("pe_ratio", "N/A")),
        ("FORWARD P/E",     fd.get("forward_pe", "N/A")),
        ("PEG RATIO",       fd.get("peg_ratio", "N/A")),
        ("P/BOOK",          fd.get("price_to_book", "N/A")),
        ("EPS (TTM)",       f"${fd.get('eps', 'N/A')}"),
        ("FORWARD EPS",     f"${fd.get('eps_forward', 'N/A')}"),
        ("GROSS MARGIN",    pct(fd.get("gross_margin"))),
        ("OPER. MARGIN",    pct(fd.get("operating_margin"))),
        ("PROFIT MARGIN",   pct(fd.get("profit_margin"))),
        ("REV. GROWTH",     pct(fd.get("revenue_growth"))),
        ("FREE CASH FLOW",  fd.get("free_cash_flow", "N/A")),
        ("TOTAL DEBT",      fd.get("total_debt", "N/A")),
        ("DEBT / EQUITY",   fd.get("debt_to_equity", "N/A")),
        ("CURRENT RATIO",   fd.get("current_ratio", "N/A")),
        ("BETA",            fd.get("beta", "N/A")),
        ("SHORT % FLOAT",   pct(fd.get("short_percent_float"))),
        ("ANALYST TARGET",  f"${fd.get('analyst_target', 'N/A')}"),
        ("CONSENSUS",       (fd.get("analyst_recommendation") or "N/A").upper()),
    ]

    def make_cell(label, value):
        lbl = Paragraph(label, S["tbl_label"])
        val_color = TEXT_1
        val_str   = _esc(str(value))
        # Color-code returns
        if "RETURN" in label or "CHANGE" in label:
            try:
                num = float(str(value).replace("%","").replace("+",""))
                val_color = BULL if num >= 0 else BEAR
            except Exception:
                pass
        if label == "CONSENSUS":
            v = str(value).upper()
            val_color = BULL if "BUY" in v else (BEAR if "SELL" in v or "SHORT" in v else AMBER)
        val = Paragraph(
            f'<font color="#{_chex(val_color)}">{val_str}</font>',
            S["tbl_val"]
        )
        return [lbl, val]

    # Pair into 3 columns (label | value | label | value | label | value)
    col_w = cw / 6
    rows  = []
    for i in range(0, len(raw), 3):
        row = []
        for j in range(3):
            if i + j < len(raw):
                lbl, val = raw[i + j]
                row += make_cell(lbl, val)
            else:
                row += [Paragraph("", S["tbl_label"]), Paragraph("", S["tbl_val"])]
        rows.append(row)

    tbl = Table(rows, colWidths=[col_w * 1.2, col_w * 0.8] * 3)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [WHITE, SURFACE]),
        ("BOX",           (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 9),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 9),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def _chex(c: colors.Color) -> str:
    """reportlab Color → hex string (no #)."""
    try:
        return "{:02X}{:02X}{:02X}".format(
            int(c.red * 255), int(c.green * 255), int(c.blue * 255)
        )
    except Exception:
        return "0D0D2B"


# ── Agent Section ──────────────────────────────────────────────
def _agent_section(elements, title: str, badge: str, body: str, S, key: str, cw: float):
    if not body.strip():
        return

    accent, bg, border = _section_colors(key)

    # Section header bar
    header = Table(
        [[Paragraph(
            f'<font color="#{_chex(accent)}"><b>{badge}&nbsp;&nbsp;{title.upper()}</b></font>',
            S["h1"]
        )]],
        colWidths=[cw],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("BOX",           (0, 0), (-1, -1), 0.8, border),
        ("LINEABOVE",     (0, 0), (-1,  0), 3,   accent),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    elements.append(KeepTogether([header, _sp(0.15)]))

    # Body text — paragraph by paragraph for proper line breaking
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            elements.append(_sp(0.1))
            continue
        # Bold numbered points (e.g., "1. Some text")
        if re.match(r'^\d+[\.\)]', stripped):
            elements.append(Paragraph(
                f'<b><font color="#{_chex(accent)}">{_esc(stripped[:2])}</font></b>'
                f'{_esc(stripped[2:])}',
                S["body"]
            ))
        else:
            elements.append(Paragraph(_esc(stripped), S["body"]))

    elements.append(_sp(0.5))


# ── Page Decoration ────────────────────────────────────────────
def _make_doc(buffer, state: dict):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2.4 * cm, bottomMargin=2.2 * cm,
        title=f"{state['ticker']} — AI Due Diligence Report",
        author="AI Hedge Fund Intern",
    )
    pw, ph = A4
    cw = pw - 4.4 * cm

    def on_page(canvas, doc):
        canvas.saveState()

        # ── Top bar ──
        canvas.setFillColor(NAVY)
        canvas.rect(0, ph - 1.5 * cm, pw, 1.5 * cm, fill=1, stroke=0)
        # Gold accent line
        canvas.setFillColor(GOLD_MID)
        canvas.rect(0, ph - 1.52 * cm, pw, 2, fill=1, stroke=0)
        # Header left
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(colors.HexColor("#D4A843"))
        canvas.drawString(2.2 * cm, ph - 0.95 * cm, "◈  AI HEDGE FUND INTERN")
        # Header right
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#9898B8"))
        canvas.drawRightString(
            pw - 2.2 * cm, ph - 0.95 * cm,
            f"{state['ticker']}  ·  Due Diligence  ·  {datetime.now().strftime('%d %b %Y')}"
        )

        # ── Bottom bar ──
        canvas.setFillColor(SURFACE)
        canvas.rect(0, 0, pw, 1.3 * cm, fill=1, stroke=0)
        canvas.setFillColor(BORDER)
        canvas.rect(0, 1.3 * cm, pw, 0.4, fill=1, stroke=0)
        # Page number
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(TEXT_3)
        canvas.drawCentredString(pw / 2, 0.48 * cm, f"Page {doc.page}")
        # Disclaimer line
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(TEXT_4)
        canvas.drawCentredString(pw / 2, 0.22 * cm, "AI-generated analysis only. Not financial advice.")

        canvas.restoreState()

    return doc, on_page, cw


# ══════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════
def generate_pdf(state: dict) -> bytes:
    """
    Generate a professional, high-contrast PDF due diligence report.

    Args:
        state: Analysis state dict from Streamlit session

    Returns:
        PDF as bytes for st.download_button()
    """
    buf = io.BytesIO()
    S   = _styles()
    doc, on_page, cw = _make_doc(buf, state)

    verdict_data = _parse_verdict(state.get("judge_verdict", ""))
    v_col = _verdict_color(verdict_data["verdict"])
    v_bg  = _verdict_bg(verdict_data["verdict"])
    v_hex = _chex(v_col)

    elements = []

    # ══════════════════════════════════════════════════════════
    # PAGE 1 — COVER
    # ══════════════════════════════════════════════════════════
    elements.append(_sp(2.5))

    # ── Ticker + Company ──
    elements.append(Paragraph(_esc(state["ticker"]), S["cover_ticker"]))
    elements.append(Paragraph(_esc(state.get("company_name", state["ticker"])), S["cover_company"]))
    elements.append(Paragraph("AI Hedge Fund Intern  ·  Multi-Agent Due Diligence Report", S["cover_sub"]))
    elements.append(_sp(0.6))
    elements.append(_hr(GOLD_MID, thickness=1.5))
    elements.append(_sp(0.4))

    # ── Verdict hero ──
    v_label = Paragraph(
        f'<font color="#{v_hex}"><b>{_esc(verdict_data["verdict"])}</b></font>',
        S["cover_verdict"]
    )
    v_sub = Paragraph(
        '<font color="#{}">{}</font>'.format(_chex(TEXT_3), "FINAL VERDICT"),
        ParagraphStyle("cvl", fontName="Helvetica", fontSize=8, textColor=TEXT_3,
                       alignment=TA_CENTER, letterSpacing=3)
    )
    verdict_card = Table([[v_label], [v_sub]], colWidths=[cw])
    verdict_card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), v_bg),
        ("BOX",           (0, 0), (-1, -1), 1.0, v_col),
        ("TOPPADDING",    (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    elements.append(verdict_card)
    elements.append(_sp(0.5))

    # ── Cover KPI row ──
    kpi_items = [
        ("CONFIDENCE",   verdict_data["confidence"]),
        ("POSITION SIZE", verdict_data["position"]),
        ("GENERATED",    datetime.now().strftime("%d %b %Y")),
        ("APPROVED",     "Yes" if state.get("human_approved") else "Pending"),
    ]
    kpi_row = []
    for label, val in kpi_items:
        kpi_row.append([
            Paragraph(label, S["tbl_label"]),
            Paragraph(f"<b>{_esc(str(val))}</b>", S["tbl_val"]),
        ])

    kpi_tbl = Table(
        [[cell for pair in kpi_row for cell in pair]],
        colWidths=[cw / 8] * 8,
    )
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), SURFACE),
        ("BOX",           (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(kpi_tbl)
    elements.append(_sp(0.6))
    elements.append(_hr(BORDER))

    # ── Pipeline overview on cover ──
    pipeline = [
        ("◈", "Data Pull",   "yfinance · SEC EDGAR · Tavily"),
        ("◎", "Planner",     "Research focus areas & strategy"),
        ("▲", "Bull Analyst","Buy case with price target"),
        ("▽", "Bear Analyst","Short case with downside target"),
        ("⚔", "Debate",      "Cross-examination & rebuttals"),
        ("◉", "Risk Audit",  "5 risk dimensions scored 1–10"),
        ("⊕", "CIO Judge",   "Final verdict with confidence %"),
    ]
    pipe_rows = []
    for icon, step, desc in pipeline:
        pipe_rows.append([
            Paragraph(f"<b>{icon}  {step}</b>", S["body_sm"]),
            Paragraph(_esc(desc), S["body_sm"]),
        ])

    pipe_tbl = Table(pipe_rows, colWidths=[cw * 0.3, cw * 0.7])
    pipe_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [WHITE, SURFACE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    elements.append(pipe_tbl)
    elements.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # PAGE 2 — FINANCIAL SNAPSHOT
    # ══════════════════════════════════════════════════════════
    def section_heading(text, sub=""):
        elems = [
            _hr(GOLD_MID, thickness=1.5, space_before=2, space_after=6),
            Paragraph(f"<b>{text.upper()}</b>", S["h1"]),
        ]
        if sub:
            elems.append(Paragraph(_esc(sub), S["body_sm"]))
        elems.append(_sp(0.15))
        return elems

    elements += section_heading("Financial Snapshot",
                                f"{state['ticker']} · {state.get('company_name','')}")

    fd = state.get("financial_data", {})
    if fd and not fd.get("error"):
        elements.append(_metrics_table(fd, S, cw))
        elements.append(_sp(0.4))

        if fd.get("description"):
            elements += section_heading("Business Description")
            elements.append(Paragraph(_esc(fd["description"]), S["body"]))
            elements.append(_sp(0.3))

        # Quarterly revenue table
        if fd.get("quarterly_revenue"):
            q_data = [(r["period"], r["value"]) for r in fd["quarterly_revenue"] if r.get("value")]
            if q_data:
                elements += section_heading("Quarterly Revenue (Recent)")
                q_rows = [["QUARTER", "REVENUE"]]
                for period, val in q_data[:6]:
                    try:
                        v = float(val)
                        fmt = f"${v/1e9:.2f}B" if abs(v) >= 1e9 else f"${v/1e6:.1f}M"
                    except Exception:
                        fmt = str(val)
                    q_rows.append([period, fmt])
                q_tbl = Table(q_rows, colWidths=[cw * 0.4, cw * 0.6])
                q_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                    ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE",      (0, 0), (-1, 0), 8),
                    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, SURFACE]),
                    ("BOX",           (0, 0), (-1, -1), 0.6, BORDER),
                    ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
                    ("TOPPADDING",    (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                    ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE",      (0, 1), (-1, -1), 9),
                    ("TEXTCOLOR",     (0, 1), (-1, -1), TEXT_1),
                ]))
                elements.append(q_tbl)
                elements.append(_sp(0.3))

        # Top holders
        if fd.get("top_holders"):
            elements += section_heading("Top Institutional Holders")
            h_rows = [["INSTITUTION", "SHARES", "% HELD"]]
            for h in fd["top_holders"]:
                h_rows.append([
                    _esc(h.get("holder", "—")),
                    f"{h.get('shares', 0):,}",
                    f"{h.get('pct_held', 0):.2f}%",
                ])
            h_tbl = Table(h_rows, colWidths=[cw * 0.55, cw * 0.25, cw * 0.20])
            h_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, 0), 8),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, SURFACE]),
                ("BOX",           (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE",      (0, 1), (-1, -1), 9),
                ("TEXTCOLOR",     (0, 1), (-1, -1), TEXT_1),
            ]))
            elements.append(h_tbl)
            elements.append(_sp(0.3))

    # SEC EDGAR
    if state.get("edgar_summary"):
        elements += section_heading("SEC EDGAR — Verified Filing Data",
                                    "Source: SEC XBRL API (10-K annual filings)")
        edgar_lines = [l.strip() for l in state["edgar_summary"].split("\n") if l.strip()]
        for line in edgar_lines[:50]:
            elements.append(Paragraph(_esc(line), S["mono"]))
        elements.append(_sp(0.3))

    # Tavily
    web = state.get("web_summary", "")
    if web and "TAVILY_API_KEY" not in web and "not set" not in web.lower():
        elements += section_heading("Real-Time Web Intelligence",
                                    "Source: Tavily Search API")
        web_lines = [l.strip() for l in web.split("\n") if l.strip()]
        for line in web_lines[:40]:
            elements.append(Paragraph(_esc(line), S["body_sm"]))
        elements.append(_sp(0.3))

    elements.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # PAGES 3+ — AGENT REPORTS
    # ══════════════════════════════════════════════════════════
    agent_sections = [
        ("Research Plan",   "◎", state.get("planner_output", ""), "planner"),
        ("Bull Case",       "▲", state.get("bull_analysis",  ""), "bull"),
        ("Bear Case",       "▽", state.get("bear_analysis",  ""), "bear"),
        ("Debate",          "⚔", state.get("debate_round",   ""), "debate"),
        ("Risk Audit",      "◉", state.get("risk_audit",     ""), "risk"),
    ]
    for title, icon, body, key in agent_sections:
        if body.strip():
            _agent_section(elements, title, icon, body, S, key, cw)
            elements.append(_hr(BORDER))

    elements.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # FINAL PAGE — CIO VERDICT
    # ══════════════════════════════════════════════════════════
    if state.get("judge_verdict"):
        # Verdict KPI cards
        kpi_data_2 = [
            ("FINAL VERDICT",  verdict_data["verdict"],    v_col),
            ("CONFIDENCE",     verdict_data["confidence"], GOLD),
            ("POSITION SIZE",  verdict_data["position"],   NAVY_LIGHT),
            ("STOCK",          state["ticker"],             NAVY),
        ]
        kpi_row_2 = []
        for label, val, col in kpi_data_2:
            kpi_row_2.append(Table([
                [Paragraph(label, S["tbl_label"])],
                [Paragraph(
                    f'<font color="#{_chex(col)}"><b>{_esc(str(val))}</b></font>',
                    ParagraphStyle("vkv", fontName="Helvetica-Bold", fontSize=16,
                                   textColor=col, leading=20)
                )],
            ], colWidths=[cw / 4 - 0.3 * cm]))

        kpi_outer = Table([kpi_row_2], colWidths=[cw / 4] * 4)
        kpi_outer.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), v_bg),
            ("BOX",           (0, 0), (-1, -1), 1.0, v_col),
            ("INNERGRID",     (0, 0), (-1, -1), 0.4, colors.Color(
                v_col.red, v_col.green, v_col.blue, alpha=0.3)),
            ("LINEABOVE",     (0, 0), (-1,  0), 3,   v_col),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ]))

        elements.append(Paragraph("⊕  CIO FINAL VERDICT", S["h1"]))
        elements.append(_hr(GOLD_MID, thickness=1.5))
        elements.append(kpi_outer)
        elements.append(_sp(0.5))

        _agent_section(elements, "Decision Rationale", "⊕",
                       state["judge_verdict"], S, "judge", cw)

    # ── Disclaimer ──────────────────────────────────────────────
    elements.append(_sp(0.5))
    elements.append(_hr(BORDER))
    elements.append(Paragraph(
        "<b>DISCLAIMER:</b> This report was generated by an AI multi-agent system "
        "for research and educational purposes only. It does not constitute financial "
        "advice, an offer to buy or sell securities, or a recommendation to make any "
        "investment decision. All data is sourced from public APIs (yfinance, SEC EDGAR, "
        "Tavily). Past performance is not indicative of future results. Always conduct "
        "your own due diligence before making any investment decisions.",
        S["disclaimer"]
    ))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()
