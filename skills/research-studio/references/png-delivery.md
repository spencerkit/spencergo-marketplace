# PNG Delivery

## 1. Goal

After generating the SVG report, produce a PNG delivery artifact derived from that SVG for mobile-friendly sharing and preview.

---

## 2. Delivery rule

Default rich delivery pipeline:
1. generate structured JSON payload
2. render single-file SVG report
3. derive PNG output from the SVG
4. deliver Markdown alongside the rendered artifacts

The default artifact set is:
- `report.svg`
- `report.png`
- `report.md`
- structured JSON payload

The SVG is the primary rendered artifact.
The PNG is a derived artifact for quick viewing and messaging.
The Markdown report is a first-class companion artifact for reading, reuse, and versioning.

---

## 3. Width rule

The report canvas should be mobile-friendly.
Use a report width of 750px so the layout is suitable for phone browsing and PNG export.

---

## 4. Export rule

When exporting PNG:
- prefer a full-height render when the report is long
- keep text readable
- do not rely on external network assets
- ensure embedded images and SVG charts render correctly before export

---

## 5. Artifact rule

Prefer delivering the full default artifact set.
If only one rendered file can be shared immediately, use PNG for quick preview and keep SVG as the source render artifact.
