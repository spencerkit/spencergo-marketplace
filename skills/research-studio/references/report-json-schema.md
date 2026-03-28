# Report JSON Schema

## 1. Goal

Define a stable structured payload for SVG-first report rendering so reports stay consistent and chart rendering is predictable across SVG, PNG, and Markdown delivery.

---

## 2. Required top-level fields

Use this shape:

```json
{
  "title": "研究报告标题",
  "subtitle": "副标题或时间信息",
  "executive_summary": "执行摘要",
  "research_question": "研究问题",
  "core_conclusion": "核心结论",
  "conclusion_badges": [],
  "key_evidence": [],
  "dimensions": [],
  "charts": [],
  "uncertainty": "不确定性说明",
  "gaps": [],
  "recommendations": "理性建议",
  "sources": [],
  "footer_note": "页脚说明",
  "render_mode": "svg-first",
  "artifacts": ["report.svg", "report.png", "report.md"]
}
```

---

## 3. Field rules

### title
Required. Short and specific.

### subtitle
Optional but recommended. Use for scope, date, topic type, or delivery note.

### executive_summary
Required. Short summary of what matters most.

### research_question
Required. State the exact research question, not a vague topic label.

### core_conclusion
Required. Main judgment with boundaries.

### conclusion_badges
Optional array.
Use compact status tags such as:
- 多来源支持
- 单一来源
- 待补充
- 证据较弱

Each item can be a string or an object:
```json
{"label": "多来源支持", "level": "ok"}
```

### key_evidence
Required array for substantive reports.
Each item:
```json
{
  "title": "依据标题",
  "body": "依据内容",
  "source": "来源情况",
  "status": "已有明确来源"
}
```

### dimensions
Optional but strongly recommended.
Each item:
```json
{
  "title": "维度名称",
  "body": "维度分析",
  "source": "来源情况",
  "status": "多来源支持"
}
```

### charts
Optional.
Each item should declare one rendering path:
- `type` + `data` for built-in SVG charts
- `image_path`
- `image_base64`
- `svg`

### uncertainty
Required for research-grade delivery.
State uncertainty explicitly.

### gaps
Optional array.
Use for missing data or pending verification items.

### recommendations
Required.
Bound recommendations to evidence strength.

### sources
Required for serious reports.
Each item:
```json
{
  "name": "来源名",
  "detail": "来源说明",
  "type": "官方/媒体/本地脚本/二手整理",
  "status": "已有明确来源"
}
```

### footer_note
Optional.

### render_mode
Optional but recommended.
Use delivery-oriented values such as `svg-first`.

### artifacts
Optional but recommended.
List the produced report artifacts. Default to:
- `report.svg`
- `report.png`
- `report.md`

---

## 4. Chart item schema

### Bar chart
```json
{
  "type": "bar",
  "title": "图表标题",
  "note": "图表说明",
  "source": "来源情况",
  "status": "待补充",
  "data": {
    "labels": ["A", "B", "C"],
    "values": [12, 18, 9]
  }
}
```

### Trend chart
```json
{
  "type": "trend",
  "title": "趋势图",
  "data": {
    "labels": ["Q1", "Q2", "Q3"],
    "values": [10, 14, 19]
  }
}
```

### Matrix chart
```json
{
  "type": "matrix",
  "title": "机会-风险矩阵",
  "data": {
    "points": [
      {"label": "方向A", "x": 0.8, "y": 0.4, "color": "#2f5bea"}
    ]
  }
}
```

### Source-strength chart
```json
{
  "type": "source-strength",
  "title": "来源强度分布",
  "data": {
    "items": [
      {"label": "Tier 1", "value": 4},
      {"label": "Tier 2", "value": 6}
    ]
  }
}
```

---

## 5. Missing-data rule

If data is missing, do not fake a complete payload.
Leave fields blank where appropriate or mark them as 待补充.

---

## 6. Delivery discipline

Use one stable JSON payload per report.
Do not mix raw prose, half-structured notes, and chart data in an ad hoc way.

For formal report artifacts, prefer including:
- `layout_type`
- `takeaways`
- `metrics` when relevant
- `decision_panel`
- `risk_block`
- `action_block`

Keep schema, template, and renderer behavior aligned without redesigning the core content fields.
