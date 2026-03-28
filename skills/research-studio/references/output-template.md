# Output Template

## 1. Default compact output

Unless the user asks for detail, prefer this structure:

### 研究问题
What exactly is being examined.

### 结论
One-line judgment.

### 核心依据
- strongest evidence / reasoning 1
- strongest evidence / reasoning 2
- strongest evidence / reasoning 3

### 多维度结果
- 维度A：结论
- 维度B：结论
- 维度C：结论

### 不确定性 / 反面因素
What weakens the conclusion or still needs caution.

### 理性建议
What should be done next, bounded by evidence strength.

### 信息缺口
What remains uncertain or weakly supported.
Missing data should be left blank or explicitly marked as 待补充, not guessed.

---

## 2. Expanded output

Use only when the user asks for more detail, or when the task itself is a substantive report that requires depth.

Suggested structure:
1. conclusion
2. key findings
3. dimension-by-dimension analysis
4. for major points: mechanism + case/example + operational path
5. source comparison or confidence notes where needed
6. opportunity and risk summary
7. open questions / missing evidence
8. recommended next steps

When delivering a formal report artifact, also use `component-layout-strategies.md` to choose the right component order for the report type instead of forcing one universal layout rhythm.

---

## 3. Style rules

- lead with the answer, not background framing
- keep wording concrete
- avoid generic phrases that could fit any topic
- do not hide uncertainty
- do not turn weak evidence into a strong recommendation
- do not reveal the full internal query list unless the user asks; use the query plan to improve research quality, not to clutter the report
- do not use ceremonial recommendation language with no analytical value
- make the reasoning path visible enough that the user can see why the conclusion was reached
- use `report-quality-benchmarks.md` as the quality bar before final delivery
