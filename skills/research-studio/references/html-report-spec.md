# SVG Report Spec

## 1. Goal

Deliver research results as a polished single-file SVG report that is readable, structured, and suitable for sharing or archiving, with companion PNG and Markdown artifacts when needed.

---

## 2. Report structure

Recommended sections:
1. cover / title block
2. executive summary
3. research question
4. core conclusion
5. key evidence
6. dimension-based analysis
7. uncertainty / missing evidence
8. rational recommendations
9. source notes

---

## 3. Delivery rule

Default delivery should be:
- a short chat summary when needed
- plus the default artifact set:
  - `report.svg`
  - `report.png`
  - `report.md`
  - structured JSON payload

Do not dump large raw SVG or JSON into the normal chat reply unless the user explicitly asks for the source.

---

## 4. Single-file rule

Prefer a single self-contained SVG file.
If images are needed, embed them inline with base64 when practical.
Avoid external CSS, JS, fonts, or image dependencies when possible.

## 4.5 Width rule

Use a report width of 750px so the report is easier to browse on mobile and easier to export as PNG.

---

## 5. Visual principle

The report should feel:
- professional
- clear
- evidence-aware
- readable
- not flashy for its own sake

The page should support long-form reading without turning into a decorative landing page.
