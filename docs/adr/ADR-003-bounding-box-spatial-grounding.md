# ADR-003: 2D Bounding Box Spatial Grounding

## Status
Accepted

## Context
Enterprise accounting teams require explainability and visual proof for extracted values before approving financial transactions. Text-only extraction forces reviewers to manually search complex invoices for numbers.

## Decision
We implemented a 2D bounding box spatial grounding pipeline:
- Coordinates are normalized into standard integer [0, 1000] space `[ymin, xmin, ymax, xmax]` representing percentages of document width and height.
- Coordinates undergo geometric sanitation: clamping to bounds, repairing reversed min/max coordinates, and filtering degenerate zero-area boxes.
- The frontend renders responsive SVG/HTML overlays that scale dynamically with zoom, pan, and rotation.

## Consequences
- Bi-directional hover linking: hovering an extracted field in the sidebar highlights the source document text, and hovering a document bounding box focuses the field.
- High reviewer confidence and accelerated review turnaround.
