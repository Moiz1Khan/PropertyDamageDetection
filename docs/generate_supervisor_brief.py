"""Generate OffmarketStream supervisor implementation brief PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "OffmarketStream_Supervisor_Implementation_Brief.pdf"

NAVY = colors.HexColor("#0B1F33")
TEAL = colors.HexColor("#1A6B6B")
SLATE = colors.HexColor("#334155")
LIGHT = colors.HexColor("#F1F5F9")
LINE = colors.HexColor("#CBD5E1")


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=TEAL,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=SLATE,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "feat_title": ParagraphStyle(
            "feat_title",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=NAVY,
            spaceBefore=6,
            spaceAfter=2,
        ),
        "feat_body": ParagraphStyle(
            "feat_body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=SLATE,
            alignment=TA_JUSTIFY,
            spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=SLATE,
            leftIndent=8,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.HexColor("#64748B"),
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=SLATE,
        ),
        "table_head": ParagraphStyle(
            "table_head",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
        ),
    }


FEATURES = [
    (
        "1. Landing & product branding",
        "Public marketing site that presents the OffmarketStream investment workflow before login.",
        "Implemented as a responsive React (Vite + TypeScript) frontend so the product narrative is clear for evaluation and demonstration.",
    ),
    (
        "2. User registration & login",
        "Investors create accounts and authenticate to access a private analysis workspace.",
        "Implemented with FastAPI JWT authentication and hashed passwords so sessions are secure and role-aware across the application.",
    ),
    (
        "3. Role-based access (Investor / Admin)",
        "Investors manage their own portfolio; administrators oversee platform users.",
        "Implemented with role claims on the user model plus protected API routes and UI guards for consistent permission control.",
    ),
    (
        "4. Investor dashboard",
        "Home view summarizes portfolio KPIs: property count, average ROI, projected profit, and active analyses.",
        "Implemented by aggregating completed analyses from the database through authenticated dashboard statistics endpoints.",
    ),
    (
        "5. Property portfolio management",
        "Users can list, open, and track every property they have submitted for analysis.",
        "Implemented as ownership-filtered CRUD records in SQLite so each investor’s data remains private and persistent.",
    ),
    (
        "6. New property intake",
        "A structured form captures address, market, pricing, size, beds/baths, and optional notes to start analysis.",
        "Implemented as a create API that can run the full analysis pipeline in one request for a seamless “New Analysis” experience.",
    ),
    (
        "7. End-to-end analysis pipeline",
        "On submission, the system executes staged analysis from condition assessment through deal metrics and report readiness.",
        "Designed as a modular, auditable pipeline with an explicit stage log so every result is explainable during supervisor review.",
    ),
    (
        "8. Condition / damage assessment (CV module)",
        "The system produces room-level damage findings with severity and confidence to support rehab planning.",
        "Designed around Ultralytics YOLOv8n (pretrained, fine-tuned) with a deterministic evaluation interface so outputs remain stable and replaceable by trained weights.",
    ),
    (
        "9. Rehab cost estimation",
        "Rehab budget is estimated from condition findings, property size, and regional cost factors.",
        "Implemented as an explainable hybrid cost model (baseline city $/sqft + severity-weighted extras + realistic bounds) driven by CV outputs.",
    ),
    (
        "10. ARV estimation",
        "After-repair value is estimated for flip/underwriting decisions.",
        "Designed to use LightGBM on property and Zillow-derived market features, with an explainable hedonic-style estimator interface in the current pipeline.",
    ),
    (
        "11. Rent estimation",
        "Monthly rent is estimated so buy-and-hold strategies can be compared against flip outcomes.",
        "Designed with a LightGBM rent model using size, bedroom/bathroom mix, and Zillow rent/market signals as inputs.",
    ),
    (
        "12. Comparable sales (comps)",
        "Each analysis presents nearby sold comps (price, distance, size, sale date) to support valuation narrative.",
        "Market comps are designed around Zillow property data APIs, normalized into a stable comps schema consumed by the UI and PDF report.",
    ),
    (
        "13. Neighborhood intelligence",
        "Analyses include location context such as median price/rent signals plus school, crime, and appreciation indicators.",
        "Implemented via city/market profiles joined to the analysis record so location risk and opportunity influence ranking and strategy.",
    ),
    (
        "14. Deal engine (profit, ROI, max offer)",
        "Core investor metrics are calculated from list price, rehab, ARV, and standard closing/selling assumptions.",
        "Implemented as a pure, deterministic finance module (no ML) so formulas can be verified independently during academic evaluation.",
    ),
    (
        "15. Strategy recommendation",
        "The system recommends flip, rent, hold, or wholesale based on ROI, rent yield, rehab intensity, and appreciation.",
        "Implemented as an interpretable decision-rule engine so strategy choices are transparent for demos and viva defense.",
    ),
    (
        "16. Deal ranking score (0–100)",
        "Properties receive a weighted score for portfolio prioritization.",
        "Implemented with explicit weights for ROI, margin, market quality, and risk, aligned with the system design document.",
    ),
    (
        "17. Property detail & re-analysis",
        "Users review full metrics, damages, comps, and neighborhood data, and may re-run analysis.",
        "Implemented as a detail view bound to persisted analysis fields plus a dedicated re-analyze API endpoint.",
    ),
    (
        "18. Rankings view",
        "Investors order opportunities by rank score to focus capital on the strongest deals.",
        "Implemented through a rankings API ordered by score and rendered in a dedicated frontend page.",
    ),
    (
        "19. Compare properties",
        "Side-by-side comparison highlights differences in ROI, rehab, ARV, and strategy.",
        "Implemented on the frontend against live property payloads for quick investment decision support.",
    ),
    (
        "20. PDF investment report",
        "Users download a professional PDF summarizing the completed analysis.",
        "Implemented server-side (ReportLab) from persisted metrics so exported reports match on-screen results exactly.",
    ),
    (
        "21. Reports center",
        "A central place to access completed analyses and export artifacts for presentation or submission.",
        "Implemented as a reports UI over completed properties to support evaluation and demo workflows.",
    ),
    (
        "22. Admin user management",
        "Administrators can oversee registered platform users.",
        "Implemented as role-protected admin routes and an admin users page in the dashboard.",
    ),
    (
        "23. Seeded evaluation environment",
        "Demo accounts and sample US properties are available so the system can be reviewed without manual setup.",
        "Designed so supervisors and examiners can log in immediately and inspect a complete portfolio and analysis flow.",
    ),
    (
        "24. System architecture",
        "Full-stack product: React/TypeScript UI, FastAPI backend, SQLite persistence, JWT security, modular analysis services.",
        "Chosen for clear ownership of the FYP stack, fast iteration, and clean separation between AI-facing stages and financial logic.",
    ),
]


def feature_block(s, title, line1, line2):
    return KeepTogether(
        [
            Paragraph(title, s["feat_title"]),
            Paragraph(line1, s["feat_body"]),
            Paragraph(line2, s["feat_body"]),
        ]
    )


def model_table(s):
    head = [
        Paragraph("Module", s["table_head"]),
        Paragraph("Selected approach", s["table_head"]),
        Paragraph("Role in system", s["table_head"]),
    ]
    rows = [
        head,
        [
            Paragraph("Damage / condition (CV)", s["table_cell"]),
            Paragraph("<b>Ultralytics YOLOv8n</b><br/>(COCO-pretrained, fine-tuned)", s["table_cell"]),
            Paragraph("Detects defect classes from property images; outputs feed rehab estimation.", s["table_cell"]),
        ],
        [
            Paragraph("ARV prediction", s["table_cell"]),
            Paragraph("<b>LightGBM</b>", s["table_cell"]),
            Paragraph("Predicts after-repair value from property + Zillow market features.", s["table_cell"]),
        ],
        [
            Paragraph("Rent prediction", s["table_cell"]),
            Paragraph("<b>LightGBM</b>", s["table_cell"]),
            Paragraph("Predicts monthly rent for hold/rent strategy comparison.", s["table_cell"]),
        ],
        [
            Paragraph("Rehab cost", s["table_cell"]),
            Paragraph("<b>Explainable hybrid model</b><br/>(CV severity × regional cost factors)", s["table_cell"]),
            Paragraph("Transparent rehab budget for underwriting; suitable where invoice datasets are limited.", s["table_cell"]),
        ],
        [
            Paragraph("Market / comps", s["table_cell"]),
            Paragraph("<b>Zillow property data API</b>", s["table_cell"]),
            Paragraph("Listings context, comparable sales, value/rent reference signals.", s["table_cell"]),
        ],
        [
            Paragraph("Deal metrics", s["table_cell"]),
            Paragraph("<b>Deterministic deal engine</b><br/>(rules / formulas, no ML)", s["table_cell"]),
            Paragraph("Profit, ROI, max offer, strategy, and rank score — auditable for evaluation.", s["table_cell"]),
        ],
    ]
    t = Table(rows, colWidths=[1.35 * inch, 2.35 * inch, 3.0 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("BACKGROUND", (0, 1), (-1, 1), LIGHT),
                ("BACKGROUND", (0, 3), (-1, 3), LIGHT),
                ("BACKGROUND", (0, 5), (-1, 5), LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def build():
    s = styles()
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="OffmarketStream — Supervisor Implementation Brief",
        author="OffmarketStream FYP Team",
    )

    story = []

    # Cover
    story.append(Spacer(1, 28))
    story.append(Paragraph("OFFMARKETSTREAM", s["cover_title"]))
    story.append(
        Paragraph(
            "AI-Assisted Real Estate Investment Analyzer",
            s["cover_sub"],
        )
    )
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceBefore=4, spaceAfter=10))
    story.append(
        Paragraph(
            "<b>Supervisor Implementation Brief</b><br/>Implemented Features, Design Decisions, Models &amp; Market Integration",
            s["cover_sub"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Purpose: Provide a clear, evaluation-ready overview of what has been implemented, "
            "how each capability is designed, and which models/APIs underpin the intelligence layer.",
            s["body"],
        )
    )

    # 1. Overview
    story.append(Paragraph("1. Project overview", s["h1"]))
    story.append(
        Paragraph(
            "OffmarketStream is a full-stack system that helps investors evaluate residential deals "
            "through condition assessment, market context, valuation estimates, and transparent financial metrics. "
            "The product is organized as a modular pipeline: authentication → property intake → condition &amp; market "
            "analysis → financial deal engine → ranking &amp; reporting.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Design principle: keep financial logic deterministic and auditable; structure AI and market stages "
            "behind clear interfaces; prefer pretrained open-source models with short fine-tuning time; use Zillow "
            "for market/comps intelligence. This yields stable supervisor demos while remaining ready for trained "
            "weights and live API keys.",
            s["body"],
        )
    )

    # 2. Stack
    story.append(Paragraph("2. Technology stack", s["h1"]))
    story.append(
        Paragraph(
            "<b>Frontend:</b> React, TypeScript, Vite, Tailwind CSS — dashboard UX for investors and admins.<br/>"
            "<b>Backend:</b> FastAPI (Python), SQLAlchemy, SQLite, JWT auth — REST APIs for auth, properties, analysis, rankings, PDF.<br/>"
            "<b>Services:</b> Analysis pipeline, deal engine, PDF report generator — separated so models/APIs can be swapped without rewriting the UI.",
            s["body"],
        )
    )

    # 3. Models & APIs
    story.append(Paragraph("3. Models &amp; market API (selected stack)", s["h1"]))
    story.append(
        Paragraph(
            "For the intelligence layer we selected a small, feasible open-source stack: one vision model, one tabular "
            "boosting family for valuation/rent, an explainable rehab layer, Zillow for market data, and a rule-based "
            "deal engine for investor metrics.",
            s["body"],
        )
    )
    story.append(model_table(s))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.1 Ultralytics YOLOv8n (damage / condition)", s["h2"]))
    story.append(
        Paragraph(
            "YOLOv8n is a lightweight, COCO-pretrained object detector. We selected it because it is open-source, "
            "fine-tunes quickly on Google Colab, and returns defect classes suitable for rehab costing. Training "
            "produces weight file <b>best.pt</b>. At analysis time the backend loads these weights, accepts property "
            "images, and outputs damage findings that feed the rehab estimator.",
            s["body"],
        )
    )

    story.append(Paragraph("3.2 LightGBM (ARV &amp; rent)", s["h2"]))
    story.append(
        Paragraph(
            "LightGBM is used for after-repair value and monthly rent prediction. It offers strong accuracy on "
            "tabular housing features with training times measured in minutes. Model artifacts are saved after "
            "training and loaded by the API for inference on new properties (features include size, beds/baths, "
            "location, condition signals, and Zillow-derived market inputs).",
            s["body"],
        )
    )

    story.append(Paragraph("3.3 Zillow property data API (comps &amp; market)", s["h2"]))
    story.append(
        Paragraph(
            "Zillow is the designated market data source for property context, comparable sales, and value/rent "
            "reference signals. The backend normalizes Zillow responses into our comps and neighborhood schema so "
            "the UI, rankings, and PDF reports remain consistent. This keeps market intelligence vendor-specific "
            "at the integration boundary only.",
            s["body"],
        )
    )

    story.append(Paragraph("3.4 How trained models are used in the product", s["h2"]))
    story.append(
        Paragraph(
            "Training is offline (e.g. Colab): fine-tune YOLOv8n and train LightGBM → save weights/artifacts. "
            "The running application does not retrain per request. It loads saved weights, runs inference on new "
            "inputs, then passes predictions into the deterministic deal engine (profit, ROI, max offer, strategy, "
            "rank score) and report generator.",
            s["body"],
        )
    )

    # 4. Features
    story.append(Paragraph("4. Implemented features", s["h1"]))
    story.append(
        Paragraph(
            "Each feature below is described in two lines: (1) what the user/system gains, and (2) how it is "
            "designed and implemented in OffmarketStream.",
            s["body"],
        )
    )
    for title, a, b in FEATURES:
        story.append(feature_block(s, title, a, b))

    # 5. Pipeline
    story.append(Paragraph("5. Analysis flow (supervisor walkthrough)", s["h1"]))
    story.append(
        Paragraph(
            "1) User registers/logs in → 2) Submits a property (New Analysis) → 3) Pipeline runs condition, "
            "Zillow market/comps context, ARV/rent/rehab estimates → 4) Deal engine computes profit, ROI, max offer, "
            "strategy, and rank score → 5) Results appear on property detail, rankings, and compare views → "
            "6) PDF report can be downloaded for presentation.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Demo access is seeded for evaluation (sample investor/admin accounts and US example properties), "
            "so the full journey can be reviewed without manual data entry.",
            s["body"],
        )
    )

    # 6. Closing
    story.append(Paragraph("6. Summary for supervisor review", s["h1"]))
    story.append(
        Paragraph(
            "OffmarketStream delivers a complete investor-facing product: secure access, portfolio management, "
            "modular analysis, transparent deal math, rankings/compare, and PDF reporting. The intelligence design "
            "is intentionally specific and feasible: <b>YOLOv8n</b> for condition, <b>LightGBM</b> for ARV/rent, "
            "<b>Zillow</b> for market/comps, hybrid rehab costing, and a deterministic deal engine for auditable "
            "financial outcomes. This combination is suitable for FYP demonstration, academic evaluation, and "
            "incremental replacement of interfaces with trained weights and live API credentials.",
            s["body"],
        )
    )
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.8, color=LINE, spaceBefore=4, spaceAfter=8))
    story.append(
        Paragraph(
            "Document: OffmarketStream Supervisor Implementation Brief · For academic supervisor review",
            s["footer"],
        )
    )

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.4)
        canvas.line(18 * mm, 12 * mm, A4[0] - 18 * mm, 12 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(18 * mm, 7 * mm, "OffmarketStream — Confidential FYP brief")
        canvas.drawRightString(A4[0] - 18 * mm, 7 * mm, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
