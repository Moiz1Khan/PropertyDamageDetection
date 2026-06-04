# SRS Diagrams — AI Real Estate Investment Analyzer

Draw.io (diagrams.net) XML files for FCCU COMP497A SRS (Traditional Projects).

## Files

| File | Diagram |
|------|---------|
| `01-system-context-diagram.drawio` | System context (actors + external systems) |
| `02-use-case-diagram.drawio` | Use cases with «include» relationships |
| `03-entity-relationship-diagram.drawio` | ERD (database entities) |
| `04-class-diagram.drawio` | UML class diagram (application layer) |
| `05-sequence-diagram-property-analysis.drawio` | Main analysis flow |
| `06-data-flow-diagram.drawio` | DFD Level 0 + Level 1 (two pages) |

## How to open

1. Go to [https://app.diagrams.net/](https://app.diagrams.net/) or open the Draw.io desktop app.
2. **File → Open from → Device** and select any `.drawio` file (close any old tab first, then reopen so you get the latest file).
3. Use **View → Fit Page** or **View → Zoom → 100%** if the canvas looks too small or cramped.
4. Use **Arrange → Layout** or drag shapes to fine-tune spacing.
5. Enable **View → Connection Arrows → Orthogonal** if you want straighter routing while editing.

**Note:** Diagrams use standard page size 1169×827. If draw.io shows “Failed” on cloud save, use **File → Save As** locally.

## Regenerate

```bash
python generate_diagrams.py
```

## Alignment with proposal

Diagrams match the FYP proposal modules: damage detection, rehab/ARV/rent estimation, comps, deal metrics, strategy, neighborhood analysis, ranking, and PDF reports.
