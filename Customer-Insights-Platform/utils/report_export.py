"""Helpers for creating report exports in PDF, Image (PNG), Excel, and CSV formats."""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


EXPORT_DIR = Path(__file__).resolve().parent.parent / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── Brand palette ──────────────────────────────────────────────────────────────
BRAND_PRIMARY   = (0.388, 0.400, 0.945)   # #6366f1 indigo
BRAND_SECONDARY = (0.145, 0.388, 0.922)   # #2563eb blue
BRAND_DARK      = (0.047, 0.063, 0.157)   # #0f1028 near-black
BRAND_LIGHT     = (0.969, 0.973, 0.984)   # #f7f8fb
TEXT_MUTED      = (0.373, 0.404, 0.451)   # #5f6773
TEXT_PRIMARY    = (0.063, 0.086, 0.122)   # #10161f
SUCCESS         = (0.063, 0.725, 0.506)   # #10b981


def _pdf_branded(data: Any, title: str = "InsightForge Report", subtitle: str = "") -> bytes:
    """Generate a detailed, multi-section branded PDF report in tabular form."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
    )

    PAGE_W, PAGE_H = A4
    LEFT, RIGHT, TOP, BOTTOM = 18 * mm, 18 * mm, 20 * mm, 18 * mm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM,
    )

    def rgb(*t): return colors.Color(*t)

    c_primary   = rgb(*BRAND_PRIMARY)
    c_secondary = rgb(*BRAND_SECONDARY)
    c_dark      = rgb(*BRAND_DARK)
    c_light     = rgb(*BRAND_LIGHT)
    c_muted     = rgb(*TEXT_MUTED)
    c_white     = colors.white
    c_success   = rgb(*SUCCESS)

    styles = getSampleStyleSheet()

    h1 = ParagraphStyle(
        "H1", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=20,
        textColor=c_white, leading=24, spaceAfter=0,
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=12,
        textColor=c_dark, leading=16, spaceBefore=12, spaceAfter=6,
    )
    sub = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9,
        textColor=c_white, leading=13,
    )
    body = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8,
        textColor=rgb(*TEXT_PRIMARY), leading=12,
    )
    th_style = ParagraphStyle(
        "TH", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8,
        textColor=c_white, leading=11, alignment=0,
    )
    td_style = ParagraphStyle(
        "TD", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8,
        textColor=rgb(*TEXT_PRIMARY), leading=11,
    )
    td_num_style = ParagraphStyle(
        "TDNum", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8,
        textColor=rgb(*TEXT_PRIMARY), leading=11, alignment=2,
    )

    story = []
    now = datetime.now().strftime("%B %d, %Y %H:%M")
    content_w = PAGE_W - LEFT - RIGHT

    # ── HEADER BANNER ──────────────────────────────────────────────────────────
    header_table = Table(
        [[
            Paragraph("IF", ParagraphStyle("Logo", fontName="Helvetica-Bold", fontSize=18, textColor=c_white, alignment=1)),
            [Paragraph(title, h1), Paragraph(subtitle or "Detailed Analytical Report · OmniMall AI Platform", sub)],
            Paragraph(f"Generated<br/>{now}", ParagraphStyle("TS", fontName="Helvetica", fontSize=8, textColor=c_white, alignment=2, leading=11)),
        ]],
        colWidths=[14 * mm, content_w - 14 * mm - 38 * mm, 38 * mm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), c_primary),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (0, -1),  8),
        ("RIGHTPADDING",  (-1, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS",[8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5 * mm))

    # ── EXECUTIVE SUMMARY TABULAR BLOCK ────────────────────────────────────────
    story.append(Paragraph("1. Executive Metrics & Summary Table", h2))
    story.append(HRFlowable(width=content_w, thickness=1, color=c_primary, spaceAfter=6))

    if isinstance(data, pd.DataFrame) and not data.empty:
        df = data.copy()
        row_cnt, col_cnt = len(df), len(df.columns)
        num_cols = df.select_dtypes(include="number").columns.tolist()

        # Summary KPIs Table
        kpi_headers = [Paragraph(c, th_style) for c in ["Metric Name", "Value / Count", "Statistical Summary", "Status"]]
        kpi_data = [kpi_headers]

        kpi_data.append([
            Paragraph("Total Records Analyzed", td_style),
            Paragraph(f"{row_cnt:,} rows", td_num_style),
            Paragraph(f"Across {col_cnt} fields/columns", td_style),
            Paragraph("Verified", ParagraphStyle("OK", fontName="Helvetica-Bold", fontSize=8, textColor=c_success)),
        ])

        for col in num_cols[:4]:
            col_sum = df[col].sum()
            col_avg = df[col].mean()
            kpi_data.append([
                Paragraph(f"Field: {col}", td_style),
                Paragraph(f"{col_sum:,.2f}" if isinstance(col_sum, float) else f"{col_sum:,}", td_num_style),
                Paragraph(f"Mean: {col_avg:,.2f} | Min: {df[col].min():,} | Max: {df[col].max():,}", td_style),
                Paragraph("Optimal", ParagraphStyle("OK2", fontName="Helvetica-Bold", fontSize=8, textColor=c_primary)),
            ])

        sum_tbl = Table(kpi_data, colWidths=[45 * mm, 35 * mm, 70 * mm, 24 * mm])
        sum_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), c_primary),
            ("GRID",         (0, 0), (-1, -1), 0.5, rgb(0.88, 0.9, 0.93)),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [c_white, c_light]),
        ]))
        story.append(sum_tbl)
        story.append(Spacer(1, 5 * mm))

        # ── DETAILED DATA MATRIX TABLE ─────────────────────────────────────────
        story.append(Paragraph("2. Detailed Data Breakdown Matrix", h2))
        story.append(HRFlowable(width=content_w, thickness=1, color=c_primary, spaceAfter=6))

        df_display = df.head(45)
        display_cols = list(df_display.columns)[:7]  # Fit nicely
        n_c = len(display_cols)
        col_w = content_w / max(n_c, 1)

        mat_headers = [Paragraph(str(c), th_style) for c in display_cols]
        mat_rows = [mat_headers]

        for _, r in df_display.iterrows():
            row_cells = []
            for col in display_cols:
                v = r[col]
                if isinstance(v, (int, float)):
                    row_cells.append(Paragraph(f"{v:,.2f}" if isinstance(v, float) else f"{v:,}", td_num_style))
                else:
                    row_cells.append(Paragraph(str(v)[:45], td_style))
            mat_rows.append(row_cells)

        mat_tbl = Table(mat_rows, colWidths=[col_w] * n_c, repeatRows=1)
        mat_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), c_primary),
            ("GRID",         (0, 0), (-1, -1), 0.4, rgb(0.85, 0.88, 0.92)),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("LEFTPADDING",  (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [c_white, c_light]),
        ]))
        story.append(mat_tbl)
    else:
        story.append(Paragraph(str(data)[:600], body))

    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width=content_w, thickness=0.5, color=rgb(0.85, 0.87, 0.9), spaceAfter=4))
    story.append(Paragraph(f"OmniMall AI · Detailed Report · Page 1 of 1 · Generated {now}", footer_style))

    doc.build(story)
    return buf.getvalue()


def _png_report(data: Any, title: str = "InsightForge Report") -> bytes:
    """Generate a styled PNG dashboard snapshot of the data."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    import numpy as np

    PRIMARY = tuple(c / 255 for c in (99, 102, 241))    # #6366f1
    SECONDARY = tuple(c / 255 for c in (37, 99, 235))   # #2563eb
    SUCCESS_C = tuple(c / 255 for c in (16, 185, 129))  # #10b981
    WARN_C = tuple(c / 255 for c in (245, 158, 11))     # #f59e0b
    BG = "#f7f8fb"
    CARD_BG = "#ffffff"
    TEXT = "#0f1028"
    MUTED = "#6b7280"
    BORDER = "#e5e7eb"

    fig = plt.figure(figsize=(14, 10), facecolor=BG, dpi=150)
    fig.patch.set_facecolor(BG)

    gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
                  top=0.88, bottom=0.08, left=0.05, right=0.97)

    # ── HEADER BANNER ─────────────────────────────────────────────────────────
    header_ax = fig.add_axes([0, 0.9, 1, 0.1])
    header_ax.set_facecolor(PRIMARY)
    header_ax.set_xlim(0, 1)
    header_ax.set_ylim(0, 1)
    header_ax.axis("off")

    # Logo circle
    logo_circle = plt.Circle((0.032, 0.5), 0.28, color="white", alpha=0.2,
                               transform=header_ax.transAxes, zorder=2)
    header_ax.add_patch(logo_circle)
    header_ax.text(0.032, 0.5, "IF", transform=header_ax.transAxes,
                   ha="center", va="center", fontsize=12, fontweight="bold",
                   color="white", zorder=3)

    # Title
    header_ax.text(0.07, 0.65, title, transform=header_ax.transAxes,
                   fontsize=14, fontweight="bold", color="white", va="center")
    header_ax.text(0.07, 0.28, "OmniMall AI  ·  InsightForge Platform",
                   transform=header_ax.transAxes,
                   fontsize=9, color=(1, 1, 1, 0.80), va="center")

    now_str = datetime.now().strftime("%b %d, %Y  %H:%M")
    header_ax.text(0.99, 0.5, f"Generated {now_str}", transform=header_ax.transAxes,
                   fontsize=8, color="white", va="center", ha="right", alpha=0.85)

    # ── METRIC CARDS (row 0) ───────────────────────────────────────────────────
    if isinstance(data, pd.DataFrame) and not data.empty:
        numeric_cols = data.select_dtypes(include="number").columns.tolist()
        metric_vals = []
        for col in numeric_cols[:4]:
            metric_vals.append((col, data[col].sum(), data[col].mean()))
        while len(metric_vals) < 4:
            metric_vals.append(("—", 0, 0))

        metric_colors = [PRIMARY, SECONDARY, SUCCESS_C, WARN_C]
        metric_labels = ["Total", "Average"] * 2
        for i, (name, total, avg) in enumerate(metric_vals[:4]):
            ax = fig.add_subplot(gs[0, i % 3]) if i < 3 else None
            if ax is None:
                continue
            ax.set_facecolor(CARD_BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            for spine in ["top", "right", "bottom", "left"]:
                ax.spines[spine].set_visible(False)

            # Accent bar
            rect = mpatches.FancyBboxPatch((0, 0), 1, 1,
                boxstyle="round,pad=0.02", linewidth=1.2,
                edgecolor=BORDER, facecolor=CARD_BG, zorder=0)
            ax.add_patch(rect)
            accent = mpatches.FancyBboxPatch((0, 0.88), 1, 0.12,
                boxstyle="round,pad=0", linewidth=0,
                facecolor=metric_colors[i], zorder=1)
            ax.add_patch(accent)

            ax.text(0.5, 0.6, f"{total:,.0f}", ha="center", va="center",
                    fontsize=16, fontweight="bold", color=TEXT)
            ax.text(0.5, 0.32, name[:18], ha="center", va="center",
                    fontsize=9, color=MUTED)
            ax.text(0.5, 0.15, f"avg {avg:.1f}", ha="center", va="center",
                    fontsize=8, color=MUTED, alpha=0.7)

        # ── BAR CHART (row 1 left) ─────────────────────────────────────────────
        ax_bar = fig.add_subplot(gs[1, :2])
        ax_bar.set_facecolor(CARD_BG)
        if numeric_cols:
            col = numeric_cols[0]
            vals = data[col].head(10).values
            cats = (data.index[:10] if data.index.dtype != "object"
                    else data.index[:10].astype(str))
            xpos = range(len(vals))
            bars = ax_bar.bar(xpos, vals,
                              color=[PRIMARY if v >= vals.mean() else SECONDARY for v in vals],
                              width=0.65, edgecolor="white", linewidth=0.5, zorder=2)
            ax_bar.set_xticks(list(xpos))
            ax_bar.set_xticklabels([str(c)[:8] for c in cats],
                                    fontsize=7, rotation=25, ha="right")
            ax_bar.set_ylabel(col[:20], fontsize=8, color=MUTED)
            ax_bar.set_title(f"Distribution — {col}", fontsize=10,
                             fontweight="bold", color=TEXT, pad=8)
            ax_bar.tick_params(colors=MUTED, labelsize=7)
            ax_bar.spines["top"].set_visible(False)
            ax_bar.spines["right"].set_visible(False)
            ax_bar.spines["left"].set_color(BORDER)
            ax_bar.spines["bottom"].set_color(BORDER)
            ax_bar.set_facecolor(BG)
            ax_bar.yaxis.grid(True, color=BORDER, linewidth=0.5, zorder=0)

        # ── PIE CHART (row 1 right) ────────────────────────────────────────────
        ax_pie = fig.add_subplot(gs[1, 2])
        ax_pie.set_facecolor(CARD_BG)
        if len(numeric_cols) >= 2:
            pie_vals = [abs(data[c].sum()) for c in numeric_cols[:5]]
            pie_lbls = [c[:12] for c in numeric_cols[:5]]
            pie_colors = [PRIMARY, SECONDARY, SUCCESS_C, WARN_C, (0.6, 0.3, 0.9)]
            wedges, texts, autotexts = ax_pie.pie(
                pie_vals, labels=pie_lbls, autopct="%1.0f%%",
                colors=pie_colors[:len(pie_vals)],
                startangle=140, pctdistance=0.78,
                wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
            )
            for t in texts: t.set_fontsize(7); t.set_color(MUTED)
            for a in autotexts: a.set_fontsize(7); a.set_color("white"); a.set_fontweight("bold")
            ax_pie.set_title("Column share", fontsize=10, fontweight="bold", color=TEXT, pad=8)

        # ── DATA PREVIEW TABLE (row 2) ─────────────────────────────────────────
        ax_tbl = fig.add_subplot(gs[2, :])
        ax_tbl.axis("off")
        preview = data.head(6)
        cols_show = preview.columns[:7].tolist()
        preview = preview[cols_show]
        cell_text = preview.astype(str).values.tolist()
        col_headers = [str(c)[:14] for c in cols_show]

        tbl = ax_tbl.table(
            cellText=cell_text,
            colLabels=col_headers,
            cellLoc="center",
            loc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1, 1.5)
        for (row, col), cell in tbl.get_celld().items():
            cell.set_edgecolor(BORDER)
            if row == 0:
                cell.set_facecolor(PRIMARY)
                cell.set_text_props(color="white", fontweight="bold")
            elif row % 2 == 0:
                cell.set_facecolor("#f0f1ff")
            else:
                cell.set_facecolor(CARD_BG)
        ax_tbl.set_title("Data Preview", fontsize=10, fontweight="bold",
                          color=TEXT, pad=10, loc="left")

    else:
        ax = fig.add_subplot(gs[:, :])
        ax.text(0.5, 0.5, str(data)[:200], ha="center", va="center",
                fontsize=10, color=TEXT, wrap=True)
        ax.axis("off")

    # ── FOOTER ────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.01,
             f"OmniMall AI · InsightForge Platform · Confidential · {now_str}",
             ha="center", fontsize=7, color=MUTED, style="italic")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def build_export_bytes(
    data: Any,
    export_format: str,
    title: str = "InsightForge Report",
    subtitle: str = "",
) -> tuple[bytes, str]:
    """Generate export bytes and the file extension for a report payload."""
    fmt = export_format.lower().strip()

    if fmt == "pdf":
        return _pdf_branded(data, title=title, subtitle=subtitle), "pdf"

    if fmt in ("png", "image"):
        return _png_report(data, title=title), "png"

    if fmt == "excel":
        buffer = io.BytesIO()
        if isinstance(data, pd.DataFrame):
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                data.to_excel(writer, index=False, sheet_name="Report Data")
                ws = writer.sheets["Report Data"]
                # Style header row
                from openpyxl.styles import Font, PatternFill, Alignment
                header_fill = PatternFill("solid", fgColor="6366F1")
                header_font = Font(bold=True, color="FFFFFF", size=11)
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")
                ws.freeze_panes = "A2"
                # Auto-width
                for col in ws.columns:
                    max_len = max(len(str(cell.value or "")) for cell in col)
                    ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)
        else:
            pd.DataFrame([{"content": str(data)}]).to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        return buffer.getvalue(), "xlsx"

    if fmt == "csv":
        buffer = io.BytesIO()
        if isinstance(data, pd.DataFrame):
            data.to_csv(buffer, index=False)
        else:
            pd.DataFrame([{"content": str(data)}]).to_csv(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue(), "csv"

    raise ValueError(f"Unsupported export format: {export_format}")


def save_export(
    data: Any,
    export_format: str,
    filename: str | None = None,
    title: str = "InsightForge Report",
    subtitle: str = "",
) -> Path:
    """Persist an export to disk and return the output path."""
    fmt = export_format.lower().strip()
    ext_map = {"pdf": "pdf", "png": "png", "image": "png", "excel": "xlsx", "csv": "csv"}
    ext = ext_map.get(fmt, fmt)

    stem = filename or f"report-export"
    stem = Path(stem).stem  # strip any extension already in filename
    output_path = EXPORT_DIR / f"{stem}.{ext}"

    payload, actual_ext = build_export_bytes(data, fmt, title=title, subtitle=subtitle)
    output_path = EXPORT_DIR / f"{stem}.{actual_ext}"
    output_path.write_bytes(payload)
    return output_path


def filter_df_by_date_range(
    df: pd.DataFrame,
    date_col: str,
    start_date: Any = None,
    end_date: Any = None,
) -> pd.DataFrame:
    """Filter DataFrame by start and end date cleanly."""
    if df is None or df.empty or date_col not in df.columns:
        return df
    filtered_df = df.copy()
    try:
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
        if start_date:
            filtered_df = filtered_df[filtered_df[date_col].dt.date >= pd.to_datetime(start_date).date()]
        if end_date:
            filtered_df = filtered_df[filtered_df[date_col].dt.date <= pd.to_datetime(end_date).date()]
    except Exception:
        pass
    return filtered_df


def render_export_ui(
    df: pd.DataFrame,
    filename_prefix: str = "analytics_export",
    title: str = "Data Export",
    key_prefix: str = "exp",
) -> None:
    """Render export options widget with CSV, Excel, and PDF download buttons in Streamlit."""
    import streamlit as st

    if df is None or df.empty:
        st.info("No data available for export.")
        return

    st.markdown("<div style='margin: 12px 0 6px 0; font-weight:600; font-size:14px; color:#374151;'>📥 Export Dataset</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    # CSV Download
    csv_bytes, _ = build_export_bytes(df, "csv", title=title)
    c1.download_button(
        label="📄 Export CSV",
        data=csv_bytes,
        file_name=f"{filename_prefix}.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"{key_prefix}_csv",
    )

    # Excel Download
    try:
        excel_bytes, _ = build_export_bytes(df, "excel", title=title)
        c2.download_button(
            label="📊 Export Excel",
            data=excel_bytes,
            file_name=f"{filename_prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"{key_prefix}_xlsx",
        )
    except Exception:
        c2.download_button(
            label="📊 Export CSV (Excel)",
            data=csv_bytes,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"{key_prefix}_xlsx_fallback",
        )

    # PDF Download
    try:
        pdf_bytes, _ = build_export_bytes(df, "pdf", title=title)
        c3.download_button(
            label="📕 Export PDF",
            data=pdf_bytes,
            file_name=f"{filename_prefix}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"{key_prefix}_pdf",
        )
    except Exception:
        c3.info("PDF Engine initializing...")

