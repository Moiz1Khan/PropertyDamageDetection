import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def build_property_pdf(property_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title2", parent=styles["Heading1"], fontSize=18, spaceAfter=6)
    sub = ParagraphStyle("Sub", parent=styles["Normal"], textColor=colors.HexColor("#555555"), spaceAfter=12)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=6)

    story = []
    story.append(Paragraph("OffmarketStream — Investment Summary", title))
    story.append(
        Paragraph(
            f"{property_data['address']}, {property_data['city']}, {property_data['state']}",
            sub,
        )
    )
    story.append(
        Paragraph(
            f"Strategy: {property_data['strategy'].upper()} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Rank Score: {property_data['rankScore']}/100 &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Status: {property_data['status']}",
            sub,
        )
    )

    metrics = [
        ["List Price", f"${property_data['listPrice']:,.0f}", "Max Offer", f"${property_data['maxOffer']:,.0f}"],
        ["ARV", f"${property_data['arv']:,.0f}", "Rehab Est.", f"${property_data['rehabCost']:,.0f}"],
        ["Est. Profit", f"${property_data['profit']:,.0f}", "ROI", f"{property_data['roi']:.1f}%"],
        ["Monthly Rent", f"${property_data['monthlyRent']:,.0f}", "Beds/Baths", f"{property_data['beds']}/{property_data['baths']}"],
    ]
    t = Table(metrics, colWidths=[1.4 * inch, 1.6 * inch, 1.4 * inch, 1.6 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e8e8e8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t)

    story.append(Paragraph("Damage Detection (YOLOv8)", h2))
    damage_rows = [["Type", "Room", "Severity", "Confidence"]]
    for d in property_data.get("damages") or []:
        conf = f"{d['score'] * 100:.0f}%" if d.get("score") is not None else "—"
        damage_rows.append([d["type"], d["room"], d["severity"], conf])
    if len(damage_rows) == 1:
        damage_rows.append(["None detected", "—", "—", "—"])
    dt = Table(damage_rows, colWidths=[2.2 * inch, 1.5 * inch, 1.2 * inch, 1.2 * inch])
    dt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(dt)

    items = property_data.get("rehabItems") or []
    if items:
        story.append(Paragraph("Rehab Estimate", h2))
        rows = [["Item", "Detail", "Cost"]] + [[i["label"], i["detail"], f"${i['cost']:,.0f}"] for i in items]
        rt = Table(rows, colWidths=[3.2 * inch, 2.0 * inch, 1.0 * inch])
        rt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ]))
        story.append(rt)

    story.append(Paragraph("Neighborhood", h2))
    nb = property_data.get("neighborhood") or {}

    def fmt(v, pattern):
        return "n/a" if v is None else pattern.format(v)

    story.append(
        Paragraph(
            f"Median price {fmt(nb.get('medianPrice'), '${:,.0f}')} · Median rent {fmt(nb.get('medianRent'), '${:,.0f}/mo')} · "
            f"Schools {fmt(nb.get('schoolRating'), '{}/10')} · Crime index {fmt(nb.get('crimeIndex'), '{}')} · "
            f"YoY appreciation {fmt(nb.get('appreciation'), '{}%')}",
            styles["Normal"],
        )
    )
    val = property_data.get("valuation") or {}
    if val.get("asIsSource"):
        story.append(Paragraph(
            f"ARV basis: current value from {val['asIsSource']} plus ${val.get('repairsValue', 0):,.0f} of repairs. "
            f"Rent from {val.get('rentSource', 'n/a')}.", styles["Normal"]))
    for w in property_data.get("warnings") or []:
        story.append(Paragraph(f"⚠ {w}", ParagraphStyle("Warn", parent=styles["Normal"], textColor=colors.HexColor("#9a5b00"), fontSize=8)))

    story.append(Spacer(1, 0.3 * inch))
    story.append(
        Paragraph(
            "Generated by OffmarketStream AI Real Estate Investment Analyzer · Demo / FYP report",
            ParagraphStyle("Foot", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
        )
    )

    doc.build(story)
    return buffer.getvalue()
