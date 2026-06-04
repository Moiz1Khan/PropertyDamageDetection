"""
Generate valid draw.io XML for FCCU SRS diagrams.
Run: python generate_diagrams.py
"""
from __future__ import annotations
import html
import uuid
from pathlib import Path

OUT = Path(__file__).parent
PAGE_STD = (1169, 827)
PAGE_WIDE = (1400, 1000)
PAGE_SEQ = (1300, 950)


def esc(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "&#xa;")
    return html.escape(text, quote=True)


def vertex(
    cid: str,
    value: str,
    style: str,
    x: float,
    y: float,
    w: float,
    h: float,
    parent: str = "1",
) -> str:
    v = esc(value) if value else ""
    val_attr = f' value="{v}"' if v else ""
    return (
        f'<mxCell id="{cid}" parent="{parent}" vertex="1"{val_attr} '
        f'style="{style}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        f"</mxCell>"
    )


def edge(
    eid: str,
    source: str,
    target: str,
    base_style: str,
    label: str = "",
    parent: str = "1",
    *,
    geo_y: float | None = None,
    points: list[tuple[float, float]] | None = None,
    exit_x: float | None = None,
    exit_y: float | None = None,
    entry_x: float | None = None,
    entry_y: float | None = None,
) -> str:
    style = base_style
    for key, val in [
        ("exitX", exit_x),
        ("exitY", exit_y),
        ("entryX", entry_x),
        ("entryY", entry_y),
    ]:
        if val is not None:
            style += f";{key}={val}"
    style += ";labelBackgroundColor=#ffffff;labelBorderColor=none;spacingTop=0"
    style = style.replace(";;", ";")
    lbl = f' value="{esc(label)}"' if label else ""
    if points:
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
        geo = (
            f"<mxGeometry relative=\"1\" as=\"geometry\">"
            f"<Array as=\"points\">{pts}</Array></mxGeometry>"
        )
    elif geo_y is not None:
        geo = f'<mxGeometry relative="1" as="geometry" y="{geo_y}"/>'
    else:
        geo = '<mxGeometry relative="1" as="geometry"/>'
    return (
        f'<mxCell id="{eid}" parent="{parent}" edge="1"{lbl} '
        f'style="{style}" source="{source}" target="{target}">{geo}</mxCell>'
    )


def wrap_diagram(name: str, cells: list[str], size: tuple[int, int] = PAGE_STD) -> str:
    pw, ph = size
    diagram_id = str(uuid.uuid4())
    body = "\n        ".join(cells)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="SRS Generator" version="22.1.0" type="device">
  <diagram id="{diagram_id}" name="{esc(name)}">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pw}" pageHeight="{ph}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""


def multi_page(pages: list[tuple[str, list[str], tuple[int, int]]]) -> str:
    parts = []
    for name, cells, (pw, ph) in pages:
        diagram_id = str(uuid.uuid4())
        body = "\n        ".join(cells)
        parts.append(f"""  <diagram id="{diagram_id}" name="{esc(name)}">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pw}" pageHeight="{ph}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {body}
      </root>
    </mxGraphModel>
  </diagram>""")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net" agent="SRS Generator" version="22.1.0" type="device">\n'
        + "\n".join(parts)
        + "\n</mxfile>"
    )


# Styles
ACTOR = (
    "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
    "outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;"
)
SYSTEM = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
    "fontStyle=1;fontSize=13;align=center;"
)
EXT = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
    "dashed=1;dashPattern=8 8;fontSize=11;align=center;"
)
BOUNDARY = (
    "rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 8;fillColor=none;"
    "strokeColor=#999999;verticalAlign=top;align=left;spacingLeft=10;fontStyle=1;fontSize=12;"
)
UC = "ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=10;align=center;"
ENTITY = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    "align=left;verticalAlign=top;spacingLeft=8;fontSize=10;"
)
CLASS_BOX = (
    "swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=26;"
    "fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;collapsible=0;"
)
CLASS_LINE = (
    "text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
    "spacingLeft=6;whiteSpace=wrap;html=1;fontSize=10;"
)
LIFE = (
    "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;"
    "container=1;collapsible=0;outlineConnect=0;fillColor=#dae8fc;"
    "strokeColor=#6c8ebf;size=36;fontSize=11;fontStyle=1;"
)
ACTIVATION = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;"
    "strokeWidth=1;"
)
DFD_P = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
    "fontSize=11;fontStyle=1;align=center;"
)
DFD_STORE = (
    "shape=partialRectangle;whiteSpace=wrap;html=1;top=0;left=0;fillColor=#fff2cc;"
    "strokeColor=#d6b656;bottom=0;right=0;size=12;fontSize=10;align=center;fontStyle=1;"
)
DFD_EXT = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#eeeeee;strokeColor=#333333;"
    "fontSize=11;fontStyle=1;align=center;"
)
E_SOLID = (
    "endArrow=block;html=1;rounded=0;orthogonal=1;jettySize=auto;"
    "strokeWidth=1.5;strokeColor=#333333;fontSize=10;"
)
E_UC = "endArrow=none;html=1;rounded=0;strokeColor=#333333;strokeWidth=1;orthogonal=1;"
E_INC = (
    "endArrow=open;dashed=1;html=1;rounded=0;strokeColor=#333333;fontSize=9;"
    "startArrow=diamondThin;startFill=1;startSize=12;endSize=8;orthogonal=1;"
)
E_MSG = (
    "endArrow=block;html=1;rounded=0;strokeWidth=1.5;strokeColor=#333333;"
    "fontSize=10;fontStyle=0;"
)
E_RET = (
    "endArrow=open;dashed=1;dashPattern=6 6;html=1;rounded=0;strokeWidth=1.5;"
    "strokeColor=#333333;fontSize=10;"
)
E_DFD = (
    "endArrow=classic;html=1;rounded=0;orthogonal=1;jettySize=auto;"
    "strokeWidth=1.5;strokeColor=#333333;fontSize=10;"
)
FRAME = (
    "shape=umlFrame;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;"
    "fontSize=10;align=left;verticalAlign=top;spacingLeft=6;"
)


def uml_class(cid: str, title: str, lines: list[str], x: float, y: float, w: float = 210) -> list[str]:
    cells = [vertex(cid, title, CLASS_BOX, x, y, w, 26 + len(lines) * 22 + 6)]
    for i, line in enumerate(lines):
        cells.append(vertex(f"{cid}_l{i}", line, CLASS_LINE, 0, 26 + i * 22, w, 22, parent=cid))
    return cells


def system_context() -> str:
    c = []
    c.append(vertex("sys", "AI Real Estate Investment Analyzer", SYSTEM, 480, 360, 340, 80))
    c.append(vertex("inv", "Property Investor (Primary)", ACTOR, 70, 280, 65, 115))
    c.append(vertex("agt", "Real Estate Agent (Primary)", ACTOR, 70, 500, 65, 115))
    c.append(vertex("adm", "System Administrator (Secondary)", ACTOR, 1080, 240, 65, 115))
    c.append(vertex("lnd", "Lender (Secondary)", ACTOR, 1080, 440, 65, 115))
    for eid, lbl, x, y in [
        ("db", "PostgreSQL Database", 220, 680),
        ("ml", "ML / CV Services", 480, 680),
        ("api", "Market Data API", 740, 680),
        ("rpt", "PDF Report Engine", 1000, 680),
    ]:
        c.append(vertex(eid, lbl, EXT, x, y, 190, 60))
    flows = [
        ("e1", "inv", "sys", "Submit property data", 1, 0.3, 0, 0.25),
        ("e1r", "sys", "inv", "Return analysis & rankings", 0, 0.45, 1, 0.55),
        ("e2", "agt", "sys", "Submit listing review", 1, 0.5, 0, 0.7),
        ("e2r", "sys", "agt", "Return comparison summary", 0, 0.8, 1, 0.45),
        ("e3", "adm", "sys", "Manage users & config", 0, 0.2, 1, 0.2),
        ("e4", "lnd", "sys", "Request risk report", 0, 0.5, 1, 0.5),
        ("e5", "sys", "db", "Read / write records", 0.25, 1, 0.5, 0),
        ("e6", "sys", "ml", "Run inference", 0.5, 1, 0.5, 0),
        ("e7", "sys", "api", "Fetch comps data", 0.75, 1, 0.5, 0),
        ("e8", "sys", "rpt", "Generate PDF", 1, 0.5, 0, 0.5),
    ]
    for item in flows:
        eid, s, t, lbl, ex, ey, enx, eny = item
        c.append(edge(eid, s, t, E_SOLID, lbl, exit_x=ex, exit_y=ey, entry_x=enx, entry_y=eny))
    return wrap_diagram("System Context Diagram", c, PAGE_STD)


def use_case() -> str:
    c = []
    c.append(vertex("bound", "AI Real Estate Investment Analyzer System", BOUNDARY, 220, 70, 780, 680))
    c.append(vertex("inv", "Property Investor", ACTOR, 50, 300, 60, 105))
    c.append(vertex("agt", "Real Estate Agent", ACTOR, 50, 500, 60, 105))
    c.append(vertex("adm", "System Administrator", ACTOR, 1040, 320, 60, 105))
    ucs = [
        ("uc01", "Register / Login", 50, 55, 155, 52),
        ("uc02", "Upload Property and Images", 240, 55, 175, 52),
        ("uc03", "Detect Property Damage", 470, 55, 165, 52),
        ("uc04", "Estimate Rehab Cost", 50, 175, 165, 52),
        ("uc05", "Predict ARV", 250, 175, 130, 52),
        ("uc06", "Estimate Rental Income", 420, 175, 175, 52),
        ("uc07", "Find Comparable Properties", 50, 295, 185, 52),
        ("uc08", "Calculate Profit and ROI", 270, 295, 170, 52),
        ("uc09", "Calculate Max Offer", 480, 295, 155, 52),
        ("uc10", "Recommend Strategy", 50, 415, 165, 52),
        ("uc11", "Analyze Neighborhood", 250, 415, 170, 52),
        ("uc12", "Compare and Rank Deals", 460, 415, 175, 52),
        ("uc13", "Generate Summary Report", 250, 535, 185, 52),
        ("uc14", "View Analysis Dashboard", 470, 535, 175, 52),
        ("uc15", "Manage Users and Settings", 620, 55, 185, 52),
    ]
    for uid, lbl, x, y, w, h in ucs:
        c.append(vertex(uid, lbl, UC, x, y, w, h, parent="bound"))
    inv_ucs = ["uc01", "uc02", "uc08", "uc12", "uc13", "uc14"]
    agt_ucs = ["uc01", "uc02", "uc07", "uc12", "uc14"]
    for i, u in enumerate(inv_ucs):
        ey = 0.15 + i * 0.12
        c.append(edge(f"li{i}", "inv", u, E_UC, exit_x=1, exit_y=ey, entry_x=0, entry_y=0.5))
    for i, u in enumerate(agt_ucs):
        ey = 0.2 + i * 0.14
        c.append(edge(f"la{i}", "agt", u, E_UC, exit_x=1, exit_y=ey, entry_x=0, entry_y=0.5))
    c.append(edge("lad0", "adm", "uc15", E_UC, exit_x=0, exit_y=0.5, entry_x=1, entry_y=0.5))
    includes = [
        ("uc02", "uc03"), ("uc03", "uc04"), ("uc04", "uc08"),
        ("uc05", "uc08"), ("uc07", "uc05"), ("uc08", "uc09"),
        ("uc08", "uc12"), ("uc11", "uc10"),
    ]
    for i, (a, b) in enumerate(includes):
        c.append(edge(f"inc{i}", a, b, E_INC, "<<include>>", exit_x=0.5, exit_y=1, entry_x=0.5, entry_y=0))
    return wrap_diagram("Use Case Diagram", c, PAGE_WIDE)


def erd() -> str:
    c = []
    ents = [
        ("USER", "USER\nPK: user_id\nemail, role", 50, 50, 155, 78),
        ("PROP", "PROPERTY\nPK: property_id | FK: user_id\naddress, type, price", 250, 50, 200, 88),
        ("IMG", "PROPERTY_IMAGE\nPK: image_id | FK: property_id\npath, room_type", 500, 50, 210, 78),
        ("DMG", "DAMAGE_DETECTION\nPK: detection_id | FK: image_id\ntype, severity, score", 760, 50, 220, 88),
        ("REHAB", "REHAB_ESTIMATE\nPK: rehab_id | FK: property_id\ntotal_cost", 50, 210, 185, 72),
        ("ARV", "ARV_ESTIMATE\nPK: arv_id | FK: property_id\nestimated_arv", 280, 210, 175, 72),
        ("RENT", "RENTAL_ESTIMATE\nPK: rent_id | FK: property_id\nmonthly_rent", 500, 210, 185, 72),
        ("COMP", "COMP_PROPERTY\nPK: comp_id | FK: property_id\nsale_price, distance", 720, 210, 200, 78),
        ("DEAL", "DEAL_ANALYSIS\nPK: deal_id | FK: property_id\nprofit, roi, max_offer", 50, 390, 210, 88),
        ("RPT", "PROPERTY_REPORT\nPK: report_id\nFK: property_id, deal_id", 310, 390, 200, 78),
        ("RANK", "DEAL_RANKING\nPK: ranking_id | FK: user_id\nscores", 550, 390, 190, 72),
        ("NEI", "NEIGHBORHOOD_DATA\nPK: neighborhood_id\nmedian_price, median_rent", 780, 390, 210, 78),
    ]
    for eid, lbl, x, y, w, h in ents:
        c.append(vertex(eid, lbl.replace("\n", "&#xa;"), ENTITY, x, y, w, h))
    rels = [
        ("USER", "PROP", "owns 1:N", 1, 0.5, 0, 0.5),
        ("PROP", "IMG", "has 1:N", 1, 0.35, 0, 0.5),
        ("IMG", "DMG", "produces 1:N", 1, 0.5, 0, 0.5),
        ("PROP", "REHAB", "has 1:1", 0.5, 1, 0.5, 0),
        ("PROP", "ARV", "has 1:1", 0.7, 1, 0.3, 0),
        ("PROP", "RENT", "has 1:1", 1, 0.6, 0, 0.4),
        ("PROP", "COMP", "refs 1:N", 1, 0.75, 0, 0.25),
        ("PROP", "DEAL", "1:1", 0.3, 1, 0.5, 0),
        ("DEAL", "RPT", "1:1", 1, 0.5, 0, 0.5),
        ("USER", "RANK", "creates 1:N", 0.5, 1, 0, 0.5),
        ("PROP", "NEI", "1:1", 0.8, 1, 0.2, 0),
    ]
    for i, (a, b, lbl, ex, ey, enx, eny) in enumerate(rels):
        c.append(edge(f"r{i}", a, b, E_SOLID, lbl, exit_x=ex, exit_y=ey, entry_x=enx, entry_y=eny))
    return wrap_diagram("Entity Relationship Diagram", c, PAGE_WIDE)


def class_diagram() -> str:
    c = []
    specs = [
        ("User", "User", ["- userId: UUID", "- email: String", "+ authenticate()"], 40, 40),
        ("Property", "Property", ["- propertyId: UUID", "- address: String", "+ addImage()"], 40, 210),
        ("Image", "PropertyImage", ["- imageId: UUID", "+ upload()"], 40, 380),
        ("Damage", "DamageDetection", ["+ analyze(image): List"], 300, 380),
        ("Rehab", "RehabEstimator", ["+ estimate(property)"], 300, 40),
        ("ARV", "ARVPredictor", ["+ predict(property)"], 300, 150),
        ("Rent", "RentalEstimator", ["+ estimate(property)"], 300, 260),
        ("Comp", "CompEngine", ["+ findComps(property)"], 560, 40),
        ("DealCalc", "DealCalculator", ["+ calculateROI()", "+ calculateMaxOffer()"], 560, 170),
        ("Strategy", "StrategyRecommender", ["+ recommend(deal)"], 560, 300),
        ("Rank", "DealRanker", ["+ rank(deals): List"], 560, 430),
        ("Report", "ReportGenerator", ["+ generatePDF(deal)"], 820, 40),
        ("Repo", "PropertyRepository", ["+ save()", "+ findById()"], 820, 170),
        ("Ctrl", "AnalysisController", ["+ runFullAnalysis(id)"], 820, 300),
        ("Deal", "DealAnalysis", ["- profit: Decimal", "- roi: Float"], 820, 430),
    ]
    for cid, title, lines, x, y in specs:
        c.extend(uml_class(cid, title, lines, x, y))
    links = [
        ("User", "Property", 1, 0.5, 0, 0.5),
        ("Property", "Image", 1, 0.6, 0, 0.4),
        ("Image", "Damage", 1, 0.5, 0, 0.5),
        ("Ctrl", "Rehab", 0, 0.3, 1, 0.5),
        ("Ctrl", "ARV", 0, 0.4, 1, 0.5),
        ("Ctrl", "Rent", 0, 0.5, 1, 0.5),
        ("Ctrl", "Comp", 0, 0.2, 1, 0.5),
        ("Ctrl", "DealCalc", 1, 0.5, 0, 0.5),
        ("DealCalc", "Deal", 1, 0.5, 0, 0.5),
        ("Deal", "Strategy", 0.5, 1, 0.5, 0),
        ("Deal", "Report", 1, 0.5, 0, 0.5),
        ("Repo", "Property", 0, 0.5, 1, 0.5),
        ("Ctrl", "Repo", 0.5, 0, 0.5, 1),
    ]
    for i, (a, b, ex, ey, enx, eny) in enumerate(links):
        c.append(edge(f"c{i}", a, b, E_SOLID, exit_x=ex, exit_y=ey, entry_x=enx, entry_y=eny))
    return wrap_diagram("Class Diagram", c, PAGE_WIDE)


def sequence() -> str:
    c = []
    actors = [
        ("inv", ":Investor", 40),
        ("ui", ":Web UI", 200),
        ("api", ":API Server", 380),
        ("cv", ":CV Service", 560),
        ("ml", ":ML Service", 740),
        ("db", ":Database", 920),
    ]
    for aid, name, x in actors:
        c.append(vertex(aid, name, LIFE, x, 50, 110, 720))
    # Activation bars on API and UI
    c.append(vertex("act_ui", "", ACTIVATION, 48, 90, 14, 380, parent="ui"))
    c.append(vertex("act_api", "", ACTIVATION, 48, 130, 14, 320, parent="api"))
    c.append(vertex("act_cv", "", ACTIVATION, 48, 200, 14, 50, parent="cv"))
    c.append(vertex("act_ml", "", ACTIVATION, 48, 280, 14, 50, parent="ml"))
    c.append(vertex("act_db", "", ACTIVATION, 48, 130, 14, 40, parent="db"))
    c.append(vertex("act_db2", "", ACTIVATION, 48, 330, 14, 40, parent="db"))

    c.append(vertex("frame", "alt [Report requested]", FRAME, 170, 470, 820, 200))
    msgs = [
        ("inv", "ui", "1. Upload property details and images", E_MSG, 70),
        ("ui", "api", "2. POST /api/properties/analyze", E_MSG, 110),
        ("api", "db", "3. Insert property and image metadata", E_MSG, 150),
        ("api", "cv", "4. Request computer-vision damage scan", E_MSG, 190),
        ("cv", "api", "5. Return damage regions and severity", E_RET, 230),
        ("api", "ml", "6. Request rehab, ARV, and rent models", E_MSG, 270),
        ("ml", "api", "7. Return prediction values", E_RET, 310),
        ("api", "db", "8. Save estimates and deal metrics", E_MSG, 350),
        ("api", "ui", "9. Return analysis JSON (ROI, rank)", E_MSG, 390),
        ("ui", "inv", "10. Render dashboard with deal summary", E_MSG, 430),
        ("inv", "ui", "11. Request PDF summary report", E_MSG, 510),
        ("ui", "api", "12. GET /api/reports/{dealId}", E_MSG, 550),
        ("api", "ui", "13. Return signed PDF download URL", E_RET, 590),
        ("ui", "inv", "14. Download investment report", E_MSG, 630),
    ]
    for i, (s, t, lbl, st, y) in enumerate(msgs):
        c.append(edge(f"m{i}", s, t, st, lbl, geo_y=y))
    c.append(
        vertex(
            "note",
            "Precondition: User is authenticated.&#xa;Postcondition: Deal analysis persisted and visible on dashboard.",
            "shape=note;whiteSpace=wrap;html=1;size=14;fillColor=#fff2cc;strokeColor=#d6b656;"
            "align=left;fontSize=10;spacingLeft=8;",
            40,
            680,
            420,
            55,
        )
    )
    return wrap_diagram("Sequence Diagram - Property Analysis", c, PAGE_SEQ)


def dfd_level0() -> list[str]:
    c = []
    # Center process
    c.append(
        vertex(
            "p0",
            "0\nAI Real Estate\nInvestment Analyzer",
            DFD_P,
            520,
            380,
            260,
            100,
        )
    )
    # External entities - cardinal positions
    c.append(vertex("inv", "Property Investor", DFD_EXT, 80, 280, 160, 55))
    c.append(vertex("agt", "Real Estate Agent", DFD_EXT, 80, 520, 160, 55))
    c.append(vertex("mkt", "Market Data Source", DFD_EXT, 520, 80, 180, 55))
    c.append(vertex("out", "Reports and Dashboard", DFD_EXT, 980, 380, 180, 55))
    # Separate arrows - no overlapping labels
    flows = [
        ("f1", "inv", "p0", "Property data and images", 1, 0.25, 0, 0.2),
        ("f2", "p0", "inv", "Analysis results and rankings", 0, 0.35, 1, 0.35),
        ("f3", "agt", "p0", "Listing search criteria", 1, 0.55, 0, 0.65),
        ("f4", "p0", "agt", "Deal comparison output", 0, 0.75, 1, 0.55),
        ("f5", "mkt", "p0", "Comps and neighborhood feeds", 0.5, 1, 0.5, 0),
        ("f6", "p0", "out", "PDF reports and metrics", 1, 0.5, 0, 0.5),
    ]
    for eid, s, t, lbl, ex, ey, enx, eny in flows:
        c.append(edge(eid, s, t, E_DFD, lbl, exit_x=ex, exit_y=ey, entry_x=enx, entry_y=eny))
    return c


def dfd_level1() -> list[str]:
    c = []
    c.append(vertex("inv", "Property Investor", DFD_EXT, 40, 320, 150, 50))
    c.append(vertex("agt", "Real Estate Agent", DFD_EXT, 40, 480, 150, 50))
    c.append(vertex("mkt", "Market Data API", DFD_EXT, 1180, 360, 150, 50))
    procs = [
        ("p1", "1.0\nAuthenticate User", 220, 100),
        ("p2", "2.0\nManage Property Data", 220, 280),
        ("p3", "3.0\nDetect Damage (CV)", 450, 100),
        ("p4", "4.0\nEstimate Rehab, ARV, Rent", 450, 280),
        ("p5", "5.0\nFind Comps and Area", 680, 280),
        ("p6", "6.0\nCalculate Deal Metrics", 910, 180),
        ("p7", "7.0\nRank Deals and Strategy", 910, 360),
        ("p8", "8.0\nGenerate PDF Report", 1140, 260),
    ]
    for pid, lbl, x, y in procs:
        c.append(vertex(pid, lbl, DFD_P, x, y, 150, 70))
    stores = [
        ("d1", "D1 User Accounts", 220, 600),
        ("d2", "D2 Property Records", 400, 600),
        ("d3", "D3 Detection Results", 600, 600),
        ("d4", "D4 Estimates and Deals", 820, 600),
        ("d5", "D5 Comps and Neighborhood", 1000, 600),
    ]
    for sid, lbl, x, y in stores:
        c.append(vertex(sid, lbl, DFD_STORE, x, y, 150, 50))
    flows = [
        ("e1", "inv", "p1", "login credentials", 1, 0.5, 0, 0.5),
        ("e2", "p1", "d1", "validated user", 0.5, 1, 0.5, 0),
        ("e3", "inv", "p2", "property input", 1, 0.4, 0, 0.5),
        ("e4", "p2", "d2", "saved property", 0.5, 1, 0.5, 0),
        ("e5", "d2", "p3", "image batch", 0.5, 0, 0.5, 1),
        ("e6", "p3", "d3", "damage records", 0.5, 1, 0.5, 0),
        ("e7", "d3", "p4", "damage features", 0.5, 0, 0.5, 1),
        ("e8", "p4", "d4", "ML estimates", 0.5, 1, 0.5, 0),
        ("e9", "mkt", "p5", "market feeds", 0, 0.5, 1, 0.5),
        ("e10", "agt", "p5", "search filters", 1, 0.5, 0, 0.5),
        ("e11", "p5", "d5", "comps dataset", 0.5, 1, 0.5, 0),
        ("e12", "d4", "p6", "value inputs", 0.5, 0, 0.5, 1),
        ("e13", "d5", "p6", "area context", 0, 0.5, 1, 0.5),
        ("e14", "p6", "d4", "ROI and max offer", 0.5, 1, 0.5, 0),
        ("e15", "d4", "p7", "deal metrics", 0.5, 0, 0.5, 1),
        ("e16", "p7", "inv", "ranked deal list", 0, 0.5, 1, 0.5),
        ("e17", "d4", "p8", "report payload", 0.5, 0, 0.5, 1),
        ("e18", "p8", "inv", "PDF report file", 0, 0.4, 1, 0.4),
    ]
    for eid, s, t, lbl, ex, ey, enx, eny in flows:
        c.append(edge(eid, s, t, E_DFD, lbl, exit_x=ex, exit_y=ey, entry_x=enx, entry_y=eny))
    return c


def main():
    files = {
        "01-system-context-diagram.drawio": system_context(),
        "02-use-case-diagram.drawio": use_case(),
        "03-entity-relationship-diagram.drawio": erd(),
        "04-class-diagram.drawio": class_diagram(),
        "05-sequence-diagram-property-analysis.drawio": sequence(),
        "06-data-flow-diagram.drawio": multi_page([
            ("DFD Level 0 - Context", dfd_level0(), PAGE_WIDE),
            ("DFD Level 1 - Decomposition", dfd_level1(), PAGE_WIDE),
        ]),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"Wrote {OUT / name}")


if __name__ == "__main__":
    main()
