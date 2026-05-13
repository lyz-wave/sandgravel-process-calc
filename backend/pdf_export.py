"""PDF export: calculation report + equipment selection report."""
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                 Spacer, PageBreak, Image)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── CJK font registration ──────────────────────────────
_FONT_PATH = Path(os.environ.get("SystemRoot", "C:/Windows")) / "Fonts" / "simhei.ttf"
if _FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont("SimHei", str(_FONT_PATH)))
    CN = "SimHei"
else:
    CN = "Helvetica"  # fallback (no CJK)

_MONO_PATH = Path(os.environ.get("SystemRoot", "C:/Windows")) / "Fonts" / "consola.ttf"
if _MONO_PATH.exists():
    pdfmetrics.registerFont(TTFont("Consolas", str(_MONO_PATH)))
    MONO = "Consolas"
else:
    MONO = "Courier"

# ── Colors ──────────────────────────────────────────────
DARK_BG   = HexColor("#0e141c")
HEADER_BG = HexColor("#141c26")
AMBER     = HexColor("#f59e0b")
BLUE      = HexColor("#3b82f6")
GREEN     = HexColor("#10b981")
RED       = HexColor("#ef4444")
WHITE     = HexColor("#e2e6ec")
MUTED     = HexColor("#8896a8")
BORDER    = HexColor("#1e2d3d")
TABLE_BG1 = HexColor("#0e141c")
TABLE_BG2 = HexColor("#111820")

WIDTH, HEIGHT = A4  # 210 x 297 mm

# ── Styles ──────────────────────────────────────────────
styles = getSampleStyleSheet()

def _cn_style(name, **kw):
    return ParagraphStyle(name, fontName=CN, **kw)

S_TITLE    = _cn_style("cn_title", fontSize=18, leading=24, textColor=WHITE, alignment=TA_CENTER, spaceAfter=4*mm)
S_SUBTITLE = _cn_style("cn_sub", fontSize=9, leading=13, textColor=MUTED, alignment=TA_CENTER, spaceAfter=10*mm)
S_H1       = _cn_style("cn_h1", fontSize=13, leading=18, textColor=AMBER, spaceBefore=8*mm, spaceAfter=4*mm)
S_H2       = _cn_style("cn_h2", fontSize=10, leading=14, textColor=BLUE, spaceBefore=5*mm, spaceAfter=3*mm)
S_BODY     = _cn_style("cn_body", fontSize=8, leading=13, textColor=MUTED)
S_CELL     = _cn_style("cn_cell", fontSize=7.5, leading=10, textColor=WHITE, alignment=TA_CENTER)
S_CELL_L   = _cn_style("cn_cell_l", fontSize=7.5, leading=10, textColor=WHITE, alignment=TA_LEFT)
S_HEADER   = _cn_style("cn_header", fontSize=7, leading=9, textColor=MUTED, alignment=TA_CENTER)
S_FOOTER   = _cn_style("cn_footer", fontSize=7, leading=10, textColor=MUTED, alignment=TA_CENTER)


def _build_report(filename: str, title: str, balance_section, equip_section, meta_section):
    """Shared builder for dark-themed engineering PDF report."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           leftMargin=18*mm, rightMargin=18*mm,
                           topMargin=18*mm, bottomMargin=18*mm)
    story = []

    # ── Cover / Header ──
    story.append(Spacer(1, 12*mm))
    story.append(Paragraph("砂石加工系统工艺计算平台", S_TITLE))
    story.append(Paragraph(title, S_SUBTITLE))
    story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", S_SUBTITLE))

    # Horizontal rule
    story.append(Spacer(1, 4*mm))
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6*mm))

    # ── Section: Calculation / Balance ──
    if balance_section:
        story.append(Paragraph(balance_section["heading"], S_H1))
        story.append(Spacer(1, 2*mm))

        col_widths = balance_section.get("col_widths", None)
        t = Table(balance_section["rows"], colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), MUTED),
            ('FONTNAME', (0, 0), (-1, 0), CN),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), TABLE_BG1),
            ('FONTNAME', (0, 1), (-1, -1), CN),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('TEXTCOLOR', (0, 1), (-1, -1), WHITE),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
            ('LINEBELOW', (0, 0), (-1, 0), 1, BORDER),
            # Alternating rows
            *[('BACKGROUND', (0, i), (-1, i), TABLE_BG2 if i % 2 == 1 else TABLE_BG1)
              for i in range(1, len(balance_section["rows"]))],
            # Alignment: first col left, rest right
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            # First col of header centered
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        story.append(t)

        if balance_section.get("note"):
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(balance_section["note"], S_BODY))

    # ── Section: Equipment ──
    if equip_section:
        story.append(Paragraph(equip_section["heading"], S_H1))
        story.append(Spacer(1, 2*mm))

        t2 = Table(equip_section["rows"], colWidths=equip_section.get("col_widths", None), repeatRows=1)
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), MUTED),
            ('FONTNAME', (0, 0), (-1, 0), CN),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), CN),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('TEXTCOLOR', (0, 1), (-1, -1), WHITE),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
            ('LINEBELOW', (0, 0), (-1, 0), 1, BORDER),
            *[('BACKGROUND', (0, i), (-1, i), TABLE_BG2 if i % 2 == 1 else TABLE_BG1)
              for i in range(1, len(equip_section["rows"]))],
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        story.append(t2)

        if equip_section.get("note"):
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(equip_section["note"], S_BODY))

    # ── Meta / Convergence info ──
    if meta_section:
        story.append(Spacer(1, 6*mm))
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=4*mm))
        story.append(Paragraph(meta_section, S_FOOTER))

    doc.build(story)


STREAM_CN: dict[str, str] = {
    "raw_feed": "原矿给料",
    "jaw_feed": "颚破给料",
    "jaw_product": "颚破产物",
    "cone_feed": "圆锥破给料",
    "cone_product": "圆锥破产物",
    "vsi_feed": "立轴破给料",
    "vsi_product": "立轴破产物",
    "pre_screen_feed": "预筛分给料",
    "screen1_feed": "第一筛分给料",
    "screen2_feed": "第二筛分给料",
    "screen1_overflow": "第一筛分溢流",
    "screen2_overflow": "第二筛分溢流",
}

def _cn_name(key: str) -> str:
    return STREAM_CN.get(key, key)


def export_calculation_pdf(result, path: str, config_name: str = ""):
    """Generate full engineering report PDF from BalanceResult."""
    SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5']
    config_label = f"({config_name})" if config_name else ""

    # ── Balance table ──
    header = ["物料流", "t/h"] + SIZE_LABELS
    rows = [header]
    for name, s in result.streams.items():
        rows.append([_cn_name(name), f"{s.tonnage:.1f}"] + [f"{v:.2f}%" for v in s.grading.to_list()])

    avail_w = WIDTH - 36*mm
    col_w = [avail_w * 0.20, avail_w * 0.10] + [avail_w * 0.70 / 6] * 6
    balance = dict(heading=f"物料平衡表 {config_label}", rows=rows, col_widths=col_w,
                   note=f"共 {len(result.streams)} 个物料流 · 迭代 {result.iterations} 次 · 收敛误差 {result.convergence_error:.6f}")

    # ── Equipment table ──
    eq_header = ["型号", "台数", "单机能力(t/h)", "实际通过量(t/h)", "负荷率"]
    eq_rows = [eq_header]
    for eq in result.equipment:
        lf = eq.load_factor
        lf_str = f"{lf*100:.1f}% {'⚠ 超负荷' if lf > 1 else ''}"
        eq_rows.append([
            eq.model, str(eq.quantity), f"{eq.unit_capacity:.0f}",
            f"{eq.actual_throughput:.1f}", lf_str,
        ])

    eq_col_w = [avail_w * 0.26, avail_w * 0.10, avail_w * 0.22, avail_w * 0.22, avail_w * 0.20]
    equip = dict(heading="设备选型报告", rows=eq_rows, col_widths=eq_col_w,
                 note=f"共 {len(result.equipment)} 项设备")

    # ── Meta ──
    meta = f"砂石加工系统工艺计算平台 · {config_label} · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 迭代{result.iterations}次"

    _build_report(path, f"工艺计算报告 {config_label}", balance, equip, meta)


def export_equipment_pdf(result, path: str, config_name: str = ""):
    """Generate equipment-only selection report PDF."""
    config_label = f"({config_name})" if config_name else ""
    avail_w = WIDTH - 36*mm

    eq_header = ["型号", "台数", "单机能力(t/h)", "实际通过量(t/h)", "负荷率"]
    eq_rows = [eq_header]
    for eq in result.equipment:
        lf = eq.load_factor
        lf_str = f"{lf*100:.1f}% {'⚠ 超负荷' if lf > 1 else ''}"
        eq_rows.append([
            eq.model, str(eq.quantity), f"{eq.unit_capacity:.0f}",
            f"{eq.actual_throughput:.1f}", lf_str,
        ])

    eq_col_w = [avail_w * 0.26, avail_w * 0.10, avail_w * 0.22, avail_w * 0.22, avail_w * 0.20]
    equip = dict(heading="设备选型报告", rows=eq_rows, col_widths=eq_col_w,
                 note=f"共 {len(result.equipment)} 项设备")

    meta = f"砂石加工系统工艺计算平台 · 设备选型报告 {config_label} · {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    _build_report(path, f"设备选型报告 {config_label}", None, equip, meta)
