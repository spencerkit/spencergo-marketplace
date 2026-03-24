# File Structure

## 1. Goal

Use a stable, reusable project structure for every novel project.

The project should not exist only in chat output.  
It should exist as a clean local file tree that supports:
- planning
- drafting
- revision
- proofreading
- final delivery
- optional Feishu sync

---

## 2. Root project directory

Default root:

`/root/.openclaw/novels/[小说名称]/`

Use the confirmed novel title or a normalized project title as the project folder name.

Prefer a stable name once the title is confirmed.  
Avoid renaming the project directory repeatedly after downstream files already exist.

---

## 3. Canonical project layout

Use this layout by default:

```text
/root/.openclaw/novels/[小说名称]/
├── 00_选题报告.md
├── 01_想法.md
├── 02_大纲.md
├── 03_人物小传.md
├── 04_章节骨架.md
├── 05_前情回顾.md
├── 05_本轮章节规划.md
├── characters/
│   ├── [角色名].md
│   └── ...
└── manuscript/
    ├── [章节文件].md
    └── ...
```

Optional extra files may exist when needed, but do not break the core structure.

---

## 4. Required top-level files

### 4.1 `00_选题报告.md`
Purpose:
- store topic research
- store title recommendation logic
- store final title confirmation
- store audience and market positioning

### 4.2 `01_想法.md`
Purpose:
- store story concept expansion
- store core hook
- store premise and emotional promise
- store high-level story identity

### 4.3 `02_大纲.md`
Purpose:
- store outline structure
- store major arcs
- store turning points
- store suspense and climax design

### 4.4 `03_人物小传.md`
Purpose:
- store major character package summary
- may serve as an index or overview before detailed split files exist

### 4.5 `04_章节骨架.md`
Purpose:
- store chapter-level or batch-level structural planning
- store chapter progression notes
- store draft guidance

---

## 5. Character directory rules

Directory:

`characters/`

### 5.1 Purpose
Store detailed individual character files.

### 5.2 File granularity
Default: one important character per file.

Use separate files for:
- protagonist
- major supporting characters
- major antagonists
- structurally important recurring roles

### 5.3 Naming rules
Preferred:
- `[角色名].md`

Optional if ordering matters:
- `[编号]_[角色名].md`

Choose one style and keep it stable within the same project.

### 5.4 Content expectations
Each character file should ideally include:
- basic profile
- personality core
- motivation
- conflict
- growth arc
- relationships
- key plot function
- emotional or visual highlight potential

---

## 6. Manuscript directory rules

Directory:

`manuscript/`

### 6.1 Purpose
Store draft or refined chapter text.

### 6.2 Naming rules
Preferred:
- `第X章_[标题].md`

If one chapter is split into parts:
- `第X章_01_[标题].md`
- `第X章_02_[标题].md`

### 6.3 Stability rule
Do not rename chapter files casually after downstream review or sync has happened.

If chapter names must change, preserve numbering consistency.

### 6.4 Batch writing compatibility
This structure supports:
- one chapter per file
- one chapter split into multiple files
- multi-file batches

But the visible chapter order should still remain obvious from filenames.

---

## 7. Naming discipline

### 7.1 Be consistent
Use one naming convention for:
- character files
- chapter files
- top-level planning files

### 7.2 Avoid unstable filenames
Do not keep renaming files across stages unless the user explicitly changes structure.

### 7.3 Prefer readability
Names should be readable by humans and easy to map into Feishu Wiki.

---

## 8. Minimal file completeness standard

A project is minimally structured when it has:
- a root project directory
- `00_选题报告.md`
- `01_想法.md`
- `02_大纲.md`
- `characters/`
- `manuscript/`

A project is strongly structured when it also has:
- `03_人物小传.md`
- `04_章节骨架.md`
- major character files
- stable chapter files

---

## 9. Stage-to-file mapping

### Intake / topic stage
- populate `00_选题报告.md`

### Idea expansion stage
- populate `01_想法.md`

### Outline stage
- populate `02_大纲.md`
- optionally populate `04_章节骨架.md`

### Character stage
- populate `03_人物小传.md`
- populate `characters/*.md`

### Drafting stage
- populate `manuscript/*.md`

### Later stages
- revise existing files rather than fragmenting into many inconsistent duplicates

---

## 10. Revision discipline

When refining work:
- prefer updating canonical files
- avoid creating random suffix copies unless versioning is truly necessary

Avoid uncontrolled file sprawl such as:
- `大纲_最终版_再改版.md`
- `大纲_最终版2.md`
- `大纲_最终版2_真的最终.md`

---

## 11. Delivery discipline

At delivery time, the project should be:
- structurally complete
- navigable
- stable in naming
- ready for archive or Feishu sync

The file tree should tell the project story clearly even without chat history.
cessary

Avoid uncontrolled file sprawl such as:
- `大纲_最终版_再改版.md`
- `大纲_最终版2.md`
- `大纲_最终版2_真的最终.md`

---

## 11. Delivery discipline

At delivery time, the project should be:
- structurally complete
- navigable
- stable in naming
- ready for archive or Feishu sync

The file tree should tell the project story clearly even without chat history.
