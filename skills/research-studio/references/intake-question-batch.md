# Intake Question Batch

## 1. Goal

Provide a strong one-shot intake batch for research tasks so the agent can clarify the right things early and then execute without mid-process interruption.

---

## 2. Core rule

Do not ask all of these every time.
Select the smallest set that resolves the real branching decisions.

But when a task is broad, high-stakes, or likely to cause rework, use a compact batch covering the most important categories below.

---

## 3. Recommended intake categories

### A. Report purpose
Ask:
- What decision should this report help you make?
- Is this for orientation, recommendation, or execution guidance?

Why it matters:
- this changes the analysis depth and conclusion style

Recommended default:
- if unclear, default to recommendation + execution guidance

---

### B. Audience
Ask:
- Who is the report for?
- Is it for yourself, a client, a team, or an external stakeholder?

Why it matters:
- this changes terminology, format, and explanation depth

Recommended default:
- if unclear, assume the user is the primary reader and optimize for decision usefulness

---

### C. Scope boundary
Ask:
- What is in scope?
- What should definitely not be included?

Why it matters:
- this prevents broad, bloated, half-useful reports

Recommended default:
- focus tightly on what affects the user's decision

---

### D. Depth target
Ask:
- Do you want a quick orientation, a substantive deep report, or a decision-ready document?

Why it matters:
- this changes source depth, case depth, and report size

Recommended default:
- if the task sounds strategic or expensive, lean deeper

---

### E. Output form
Ask:
- Do you want chat output only, or a deliverable artifact such as HTML / PNG?

Why it matters:
- this changes delivery pipeline and formatting work

Recommended default:
- if the user asks for a report, prefer structured report artifact delivery

---

### F. Evidence expectation
Ask:
- Do you want only strongly sourced claims, or do you also want clearly labeled tentative analysis?

Why it matters:
- this changes how aggressively inference is used

Recommended default:
- use sourced claims first, allow bounded inference only when clearly labeled

---

### G. Case-study expectation
Ask:
- Do you want concrete cases and examples, or only high-level analysis?

Why it matters:
- this changes how the report proves its points

Recommended default:
- include cases for major claims whenever possible

---

### H. Operational expectation
Ask:
- Do you want the report to stop at diagnosis, or also give actionable next steps?

Why it matters:
- this changes the final recommendation structure

Recommended default:
- include actionable next steps unless the user only wants diagnosis

---

### I. Failure condition
Ask:
- What would make this report unusable for you?

Why it matters:
- this surfaces hidden success criteria quickly

Recommended default:
- if unclear, avoid shallow summary, unsupported claims, and vague recommendations

---

## 4. Compact default batch

When a broad research task arrives and requirements are under-specified, a useful compact batch is:
1. What decision should this report help you make?
2. Who is the report for?
3. Do you want orientation, recommendation, or execution guidance?
4. Do you want a deep report or a lighter scan?
5. Do you want examples/cases and actionable recommendations included?
6. Do you want HTML/PNG deliverables?
7. What would make this report unusable for you?

---

## 5. Stop rule

Once the key branch questions are answered, stop asking and execute.
Do not keep nibbling at minor preferences during the main workflow.
