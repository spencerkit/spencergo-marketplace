#!/usr/bin/env python3
import argparse
import html
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


LAYOUT_LABELS = {
    "market": "Research Studio · Market Layout",
    "project": "Research Studio · Project Layout",
    "platform": "Research Studio · Platform Layout",
}

SVG_WIDTH = 750
SVG_HEIGHT = 1600
SVG_PADDING_X = 36
SECTION_WIDTH = SVG_WIDTH - SVG_PADDING_X * 2


@dataclass(frozen=True)
class SectionPlanItem:
    key: str


@dataclass(frozen=True)
class ParagraphBlockMeasurement:
    height: int


def _xml_escape(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def _markdown_escape(value):
    text = str(value if value is not None else "")
    return text.replace("\\", "\\\\").replace("#", "\\#")


def build_section_plan(payload):
    layout_type = str(payload.get("layout_type", "market"))
    if layout_type == "project":
        keys = [
            "executive_summary",
            "research_question",
            "core_conclusion",
            "risk_action",
            "key_evidence",
            "dimensions",
            "uncertainty",
            "sources",
        ]
    elif layout_type == "market":
        keys = [
            "executive_summary",
            "research_question",
            "core_conclusion",
            "metrics",
            "decision_panel",
            "key_evidence",
            "dimensions",
            "uncertainty",
            "sources",
        ]
    else:
        keys = [
            "executive_summary",
            "research_question",
            "core_conclusion",
            "key_evidence",
            "dimensions",
            "risk_action",
            "uncertainty",
            "sources",
        ]
    return [SectionPlanItem(key=key) for key in keys]


def wrap_text(text, max_chars):
    content = str(text or "").strip()
    if not content:
        return [""]
    if max_chars <= 0:
        return [content]

    words = content.split()
    if not words:
        return [content]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def measure_paragraph_block(text, width):
    max_chars = max(12, int(width / 8)) if width else 40
    line_count = max(1, len(wrap_text(text, max_chars)))
    return ParagraphBlockMeasurement(height=12 + line_count * 18)


def _render_chart(chart, x, y):
    chart_type = str(chart.get("type", ""))
    title = _xml_escape(chart.get("title", ""))
    data = chart.get("data", {}) if isinstance(chart.get("data", {}), dict) else {}

    if chart_type == "bar":
        labels = data.get("labels", [])
        values = data.get("values", [])
        text_parts = [
            f'<text x="{x}" y="{y}" font-size="20" font-weight="700" fill="#0f172a">',
            title,
            "</text>",
        ]
        for index, label in enumerate(labels):
            value = values[index] if index < len(values) else ""
            row_y = y + 30 + index * 24
            text_parts.extend(
                [
                    f'<text x="{x}" y="{row_y}" font-size="15" fill="#334155">',
                    _xml_escape(label),
                    "</text>",
                    f'<text x="{x + 180}" y="{row_y}" font-size="15" fill="#475569">',
                    _xml_escape(value),
                    "</text>",
                ]
            )
        return "".join(text_parts)

    return f'<text x="{x}" y="{y}" font-size="16" fill="#64748b">暂无可视化内容</text>'


def _join_items(items, formatter, empty_text="待补充"):
    valid_items = [item for item in items if isinstance(item, dict)]
    if not valid_items:
        return empty_text
    return " | ".join(formatter(item) for item in valid_items)


def _section_text(section_key, payload):
    if section_key == "executive_summary":
        return "执行摘要", str(payload.get("executive_summary", "")).strip() or "待补充"
    if section_key == "research_question":
        return "研究问题", str(payload.get("research_question", "")).strip() or "待补充"
    if section_key == "core_conclusion":
        return "核心结论", str(payload.get("core_conclusion", "")).strip() or "待补充"
    if section_key == "metrics":
        content = _join_items(
            payload.get("metrics", []),
            lambda item: f"{item.get('label', '未命名指标')}: {item.get('value', '待补充')}",
        )
        return "关键指标", content
    if section_key == "decision_panel":
        return "决策面板", str(payload.get("decision_panel", "")).strip() or "待补充"
    if section_key == "key_evidence":
        content = _join_items(
            payload.get("key_evidence", []),
            lambda item: f"{item.get('title', '未命名依据')}: {item.get('body', '')}",
        )
        return "核心依据", content
    if section_key == "dimensions":
        content = _join_items(
            payload.get("dimensions", []),
            lambda item: f"{item.get('title', '未命名维度')}: {item.get('body', '')}",
        )
        return "多维度分析", content
    if section_key == "risk_action":
        risk = str(payload.get("risk_block", "")).strip() or "待补充"
        action = str(payload.get("action_block", "")).strip() or "待补充"
        recommendation = str(payload.get("recommendations", "")).strip() or "待补充"
        content = f"关键风险: {risk} | 下一步动作: {action} | 理性建议: {recommendation}"
        return "风险与动作", content
    if section_key == "uncertainty":
        uncertainty = str(payload.get("uncertainty", "")).strip() or "待补充"
        gaps = payload.get("gaps", [])
        gap_text = " | ".join(str(gap).strip() for gap in gaps if str(gap).strip())
        if gap_text:
            uncertainty = f"{uncertainty} | 待补充: {gap_text}"
        return "不确定性与待补充", uncertainty
    if section_key == "sources":
        content = _join_items(
            payload.get("sources", []),
            lambda item: f"{item.get('name', '未命名来源')}: {item.get('detail', '')}",
        )
        return "来源说明", content
    return section_key, "待补充"


def _render_svg_text_block(label, content, x, y, width):
    max_chars = max(16, int(width / 9))
    label_lines = wrap_text(label, max_chars)
    content_lines = wrap_text(content, max_chars)
    parts = []
    current_y = y
    for line in label_lines:
        parts.append(
            f'<text x="{x}" y="{current_y}" font-size="18" font-weight="700" fill="#0f172a">{_xml_escape(line)}</text>'
        )
        current_y += 24
    for line in content_lines:
        parts.append(
            f'<text x="{x}" y="{current_y}" font-size="15" fill="#334155">{_xml_escape(line)}</text>'
        )
        current_y += 21
    return "".join(parts), current_y + 10


def render_svg_report(payload):
    title = _xml_escape(payload.get("title", "Untitled Report"))
    layout_type = str(payload.get("layout_type", "market"))
    layout_label = _xml_escape(LAYOUT_LABELS.get(layout_type, LAYOUT_LABELS["market"]))
    charts = payload.get("charts", [])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        f'<rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="#f8fafc"/>',
        f'<rect x="18" y="18" width="{SVG_WIDTH - 36}" height="{SVG_HEIGHT - 36}" rx="20" fill="#ffffff" stroke="#dbe3ee"/>',
        f'<text x="{SVG_PADDING_X}" y="64" font-size="20" fill="#475569">{layout_label}</text>',
        f'<text x="{SVG_PADDING_X}" y="108" font-size="30" font-weight="700" fill="#0f172a">{title}</text>',
    ]

    current_y = 146
    if charts:
        parts.append(_render_chart(charts[0], SVG_PADDING_X, current_y))
        chart_rows = max(1, len(charts[0].get("data", {}).get("labels", [])))
        current_y += 52 + chart_rows * 24
    else:
        parts.append(
            f'<text x="{SVG_PADDING_X}" y="{current_y}" font-size="16" fill="#64748b">暂无可视化内容</text>'
        )
        current_y += 36

    for section in build_section_plan(payload):
        label, content = _section_text(section.key, payload)
        block_markup, current_y = _render_svg_text_block(
            label,
            content,
            SVG_PADDING_X,
            current_y,
            SECTION_WIDTH,
        )
        parts.append(block_markup)

    parts.append("</svg>")
    return "".join(parts)


def render_markdown_report(payload):
    title = _markdown_escape(payload.get("title", "Untitled Report"))
    summary = str(payload.get("executive_summary", "")).strip() or "待补充"
    research_question = str(payload.get("research_question", "")).strip() or "待补充"
    core_conclusion = str(payload.get("core_conclusion", "")).strip() or "待补充"
    key_evidence = payload.get("key_evidence", [])
    dimensions = payload.get("dimensions", [])
    uncertainty = str(payload.get("uncertainty", "")).strip() or "待补充"
    gaps = payload.get("gaps", [])
    risk_block = str(payload.get("risk_block", "")).strip() or "待补充"
    action_block = str(payload.get("action_block", "")).strip() or "待补充"
    recommendations = str(payload.get("recommendations", "")).strip() or "待补充"
    sources = payload.get("sources", [])

    lines = [
        f"# {title}",
        "",
        "## 执行摘要",
        _markdown_escape(summary),
        "",
        "## 研究问题",
        _markdown_escape(research_question),
        "",
        "## 核心结论",
        _markdown_escape(core_conclusion),
        "",
        "## 核心依据",
    ]
    if key_evidence:
        lines.extend(
            f"- {_markdown_escape(item.get('title', '未命名依据'))}: {_markdown_escape(item.get('body', ''))}"
            for item in key_evidence
            if isinstance(item, dict)
        )
    else:
        lines.append("- 待补充")

    lines.extend(["", "## 多维度分析"])
    if dimensions:
        lines.extend(
            f"- {_markdown_escape(item.get('title', '未命名维度'))}: {_markdown_escape(item.get('body', ''))}"
            for item in dimensions
            if isinstance(item, dict)
        )
    else:
        lines.append("- 待补充")

    lines.extend(["", "## 不确定性与待补充", _markdown_escape(uncertainty)])
    if gaps:
        lines.extend(f"- {_markdown_escape(gap)}" for gap in gaps)

    lines.extend([
        "",
        "## 关键风险",
        _markdown_escape(risk_block),
        "",
        "## 下一步动作",
        _markdown_escape(action_block),
        "",
        "## 理性建议",
        _markdown_escape(recommendations),
        "",
        "## 来源说明",
    ])
    if sources:
        lines.extend(
            f"- {_markdown_escape(source.get('name', '未命名来源'))}"
            for source in sources
            if isinstance(source, dict)
        )
    else:
        lines.append("- 待补充")
    return "\n".join(lines) + "\n"


def build_png_export_command(svg_path, png_path):
    return ["resvg", str(svg_path), str(png_path)]


def export_png(svg_path, png_path):
    subprocess.run(build_png_export_command(svg_path, png_path), check=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("output_svg")
    parser.add_argument("--markdown-output")
    parser.add_argument("--png-output")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    svg_output = Path(args.output_svg)
    svg_output.write_text(render_svg_report(payload), encoding="utf-8")
    if args.markdown_output:
        Path(args.markdown_output).write_text(
            render_markdown_report(payload),
            encoding="utf-8",
        )
    if args.png_output:
        export_png(svg_output, Path(args.png_output))


if __name__ == "__main__":
    main()
