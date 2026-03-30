# Novel Opening Chen Ye Mainline Refocus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the opening engine of `武考第一夜，我被三个女人盯上了` so `查清陈野之死` becomes the reader-facing main line, while `武考第一 / 学院席位 / 守夜资格` remain the practical means 宁烬 must seize to keep investigating.

**Architecture:** First overwrite the active revision contract in the formal state files so the new pass is canonical. Then update the four story-structure files in dependency order from global main line to opening skeleton. Finally sync Chapter 1 through Chapter 5 manuscripts in place so every chapter has a clear immediate objective, a clear relation to 陈野旧案, and a clear chapter-end next step. Finish with a cross-file calibration pass and push the workflow back to `awaiting_revision_result_approval`.

**Tech Stack:** Markdown story docs, Markdown manuscript files, project-local JSON workflow state in `.novel-state.json`, approved spec `docs/superpowers/specs/2026-03-30-novel-opening-chenye-mainline-design.md`

---

## Planned File Map

**Create**
- `docs/superpowers/plans/2026-03-30-novel-opening-chenye-mainline-refocus.md`

**Modify**
- `novels/武考第一夜，我被三个女人盯上了/.novel-state.json`
- `novels/武考第一夜，我被三个女人盯上了/06_反馈与修订.md`
- `novels/武考第一夜，我被三个女人盯上了/01B_总主线与卷级推进.md`
- `novels/武考第一夜，我被三个女人盯上了/02_大纲.md`
- `novels/武考第一夜，我被三个女人盯上了/04A_开篇设计.md`
- `novels/武考第一夜，我被三个女人盯上了/04_章节骨架.md`
- `novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md`
- `novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md`
- `novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md`
- `novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md`
- `novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md`

**Read-Only Reference**
- `docs/superpowers/specs/2026-03-30-novel-opening-chenye-mainline-design.md`

## Task 1: Persist The New Revision Contract

**Files:**
- Modify: `novels/武考第一夜，我被三个女人盯上了/.novel-state.json`
- Modify: `novels/武考第一夜，我被三个女人盯上了/06_反馈与修订.md`

- [ ] **Step 1: Overwrite the active feedback summary**

Use this exact revision summary in both the state JSON summary fields and `06_反馈与修订.md`:

```md
前期目标感太弱；需要把“查清陈野之死”前置为卷一明线，把武考第一、学院席位、守夜资格统一改成宁烬为了继续查下去必须抢到手的刀和门票，避免事件先发生、动机后补。
```

- [ ] **Step 2: Overwrite the scope and conflict summaries**

Use these exact texts:

```md
范围说明：保留当前派系、事件顺序、前三十章基本资产和前五章已确认场面，不重做赛道、不推翻三女结构；本轮只重排前期发动机，把陈野旧案提为读者可见明线，并同步重写前五章的目标提示与章尾方向。

冲突说明：不把作品改成纯案件文，不削掉爽、狠、热血和后宫气质，不新增大段解释性设定，不改前五章已确认的爆点职责；所有改动都必须服务“宁烬为什么要查、现在为什么查不了、接下来必须先拿什么”。
```

- [ ] **Step 3: Overwrite the revision plan and pending result target**

Use this exact plan summary:

```md
修订计划：先改 01B 与 02 锁主线合同，再改 04A 与 04 锁开篇执行口径，最后回写第1章至第5章的内心驱动、查案钩子和章尾方向，并在统一校准后送入 awaiting_revision_result_approval。
```

- [ ] **Step 4: Verify the new contract is persisted**

Run:

```bash
rg -n "查清陈野之死|刀和门票|章尾方向" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/.novel-state.json" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/06_反馈与修订.md"
```

Expected: both files show the new feedback summary and plan summary.

- [ ] **Step 5: Commit the revision-contract update**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/.novel-state.json" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/06_反馈与修订.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: persist Chen Ye mainline revision contract"
```

Expected: one commit containing only workflow-state and revision-log updates.

## Task 2: Rewrite The Global Mainline Contract In `01B_总主线与卷级推进.md`

**Files:**
- Modify: `novels/武考第一夜，我被三个女人盯上了/01B_总主线与卷级推进.md`

- [ ] **Step 1: Replace the one-sentence mainline**

Revise the opening sentence-level contract so it follows this structure:

```md
宁烬为了查清陈野之死，先借武考第一撕开上升通道，再一路抢进学院核心与守夜体系；他在追查第一夜异常和旧案重叠的过程中，逐步撕开守夜局养灾控灾、筛样本和旧实验链的黑幕。
```

- [ ] **Step 2: Rewrite the volume-one engine hierarchy**

Replace the `卷一发动机` bullets so they explicitly read as:

```md
- 目标：查清陈野之死是否真是事故，并确认第一夜异常和旧案是不是同一套规则
- 手段：成为这座城里谁都绕不过去的人，抢到学院核心培养席位与守夜预备资格
- 收束：宁烬拿到第一份能指向守夜高层的铁证，同时确认自己继续查下去就等于踩进更大的筛人链
```

- [ ] **Step 3: Reorder the progression chains**

Update the `明线推进链` and `暗线推进链` so they read in this order:

```md
### 1. 明线推进链
- 陈野之死的疑点
- 武考夺魁
- 学院核心培养席位之争
- 守夜预备资格
- 第一夜与旧案模板重叠
- 城级危机里拿铁证

### 2. 暗线推进链
- 裂口任务安排异常
- 污染体投放有模板
- 守夜局分部在筛样本
- 更高层旧实验链浮出水面
```

- [ ] **Step 4: Reorder the protagonist drive contract**

Make `主角驱动力总合同` explicit in this order:

```md
### 1. 最表层驱动
- 查清陈野到底怎么死的

### 2. 现实手段驱动
- 变强
- 上位
- 抢资格

### 3. 更深层驱动
- 把把人命当材料的那套规则狠狠干烂
- 不让陈野式的死继续落到自己人头上
```

- [ ] **Step 5: Verify the global contract**

Run:

```bash
rg -n "查清陈野|手段：成为这座城里谁都绕不过去的人|第一夜与旧案模板重叠|抢资格" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/01B_总主线与卷级推进.md"
```

Expected: the mainline sentence, volume-one engine, chain order, and drive order all mention 陈野 first and upward access second.

- [ ] **Step 6: Commit the global-mainline rewrite**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/01B_总主线与卷级推进.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: refocus opening mainline on Chen Ye case"
```

Expected: one commit containing only the global mainline contract rewrite.

## Task 3: Rewrite The Volume-One Outline In `02_大纲.md`

**Files:**
- Modify: `novels/武考第一夜，我被三个女人盯上了/02_大纲.md`

- [ ] **Step 1: Rewrite the story summary paragraph**

Update the opening paragraph so it states that 武考第一 is the first step of investigation access, not the end in itself.

The paragraph must explicitly include these ideas:

```md
- 宁烬一直没放下陈野之死
- 武考第一给了他被看见、被忌惮、被纳入核心视线的门票
- 第一夜裂口让他怀疑陈野那次不是孤立事故
- 后续学院与守夜双线，都是他查案与被拦截同时发生的场域
```

- [ ] **Step 2: Swap the goal hierarchy so 明线 = 陈野旧案**

Revise `卷一总目标` to this structure:

```md
### 1. 明线目标
- 宁烬要查清陈野之死究竟是不是事故，以及它和武考第一夜异常是不是同一套规则
- 前二十章必须不断让读者看到：宁烬接下来是在顺着旧案往下追

### 2. 手段目标
- 宁烬必须在卷一内完成从“武考第一的风口人物”到“学院与守夜都不敢随手拿捏的危险核心”的身份跃迁
- 他要拿下学院核心培养席位与守夜预备资格，因为不抢到这些位置，他根本没有继续查下去的资格

### 3. 黑幕目标
- 卷一结尾必须拿到第一份能指向守夜局高层的铁证，但只撕开一角，不一次掀底
```

- [ ] **Step 3: Rewrite the story-bearing sections so the case line drives the surface line**

Update `表层故事 / 深层故事 / 故事推进节点 / 前三十章粗分配 / 三大 Turning Points` so they all reflect:

```md
- 表层故事不是“危险少年一路上位”，而是“危险少年为了查旧案，被逼着一边上位一边踩进更深的局”
- 第一幕除了点火，还必须立住“旧案重新活过来”
- 第二幕不是学院线和守夜线各跑各的，而是“白天抢接近真相的资格，夜里踩进和陈野相似的死路”
- Turning Point 2 必须从“发现任务有问题”改成“发现第一夜异常和陈野旧案不是两件事”
```

- [ ] **Step 4: Rewrite the 1-30 chapter allocation so every segment has a visible pursuit**

Use this directional contract:

```md
### 1-3 章
- 武考夺魁
- 第一夜裂口
- 陈野旧案的伤口被重新掀开

### 4-10 章
- 三女全部入场
- 学院特招与守夜观察同时开始
- 宁烬意识到自己现在还没有资格查，只能先抢名额、抢位置、抢入口

### 11-20 章
- 学院资源争夺
- 小型守夜任务
- 第一夜异常与旧案模板第一次明确重叠
- 宁烬决定顺着这条线继续查下去
```

- [ ] **Step 5: Verify the outline rewrite**

Run:

```bash
rg -n "明线目标|手段目标|陈野之死究竟是不是事故|没有继续查下去的资格|不是两件事|顺着这条线继续查下去" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/02_大纲.md"
```

Expected: the outline now treats 陈野旧案 as the visible line and upward growth as the required means.

- [ ] **Step 6: Commit the outline rewrite**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/02_大纲.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: reframe volume one around Chen Ye investigation"
```

Expected: one commit containing only the outline rewrite.

## Task 4: Rewrite The Opening Execution Contract In `04A_开篇设计.md` And `04_章节骨架.md`

**Files:**
- Modify: `novels/武考第一夜，我被三个女人盯上了/04A_开篇设计.md`
- Modify: `novels/武考第一夜，我被三个女人盯上了/04_章节骨架.md`

- [ ] **Step 1: Update the opening-gate goals in `04A_开篇设计.md`**

The top-level opening responsibilities must explicitly include:

```md
- 立目标：让读者知道宁烬想查清陈野之死
- 立限制：让读者知道他现在没资格直接查
- 立路径：让读者知道武考、学院、守夜三条线就是他抢资格、抢入口、抢真相的路
```

- [ ] **Step 2: Rewrite the chapter-task and responsibility sections in `04A_开篇设计.md`**

The `前三章设计` and `前十章责任分配` sections must include these directional rules:

```md
- 第1章：立住旧案伤口没过去
- 第2章：让第一夜异常第一次像旧案重演
- 第3章：让宁烬意识到“官方口径未必可信”
- 4-6章：让宁烬知道自己现在查不了，只能先拿资格
- 7-10章：让宁烬开始把“抢资格”和“查旧案”连成同一条线
```

- [ ] **Step 3: Rewrite the first-ten-chapter skeleton hooks in `04_章节骨架.md`**

Keep current chapter titles and broad event order, but change the `章节职责` and `结尾钩子` so they line up like this:

```md
第1章：职责 = 武考夺魁 + 切断旧关系 + 点出陈野伤口未愈；钩子 = 第一夜预警让旧案味道回来
第2章：职责 = 城市暗面掀开 + 名单开始挑人；钩子 = 宁烬意识到“今晚还会死人”
第3章：职责 = 残印点火 + 官方口径出现裂缝；钩子 = 他必须想办法摸到更核心的信息
第4章：职责 = 第一夜后果 + 低位者先填命模板成形；钩子 = 宁烬开始记路、记表、记谁在动名单
第5章：职责 = 苏清软公开站队 + 宁烬被逼下场；钩子 = 不是酷炫下场，而是他已经没有不下去的余地
第6-10章：每章都要把“抢资格”和“继续查”绑死，不允许只写冲突不写方向
```

- [ ] **Step 4: Verify the opening-execution rewrite**

Run:

```bash
rg -n "立目标：让读者知道宁烬想查清陈野之死|立限制：让读者知道他现在没资格直接查|今晚还会死人|记路、记表、记谁在动名单|抢资格" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04A_开篇设计.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04_章节骨架.md"
```

Expected: both files now define the opening as a directed pursuit, not a set of parallel incidents.

- [ ] **Step 5: Commit the opening-execution rewrite**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04A_开篇设计.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04_章节骨架.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: align opening execution with Chen Ye mainline"
```

Expected: one commit containing only the opening-design and skeleton rewrite.

## Task 5: Sync Chapter 1 And Chapter 2 Manuscripts To The New Mainline

**Files:**
- Modify: `novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md`
- Modify: `novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md`

- [ ] **Step 1: Rewrite Chapter 1 so 陈野 is an active wound and not passive background**

Chapter 1 must explicitly do all of the following:

```md
- 宁烬夺魁时，不只是想翻身，而是知道只有先爬上去，才有资格碰到更上层的记录和人
- 林可依相关段落要继续完成去舔狗化，但不能抢走陈野旧案作为更深层驱动
- 结尾预警出现后，宁烬要立刻把这股味道和陈野那一夜连起来
- 章尾不能只落在“今晚还没完”，要落在“他得盯住东三区接下来会怎么挑人”
```

- [ ] **Step 2: Rewrite Chapter 2 so the public stripping leads directly to the case line**

Chapter 2 must explicitly do all of the following:

```md
- 把前五十筛查写成“先分谁值钱、再分谁该去冒险”
- 苏清软的护盘要保留，但她的作用是让宁烬还能站着继续往前，不是替他解决问题
- 名单开始挑人时，宁烬心里必须明确：这和陈野那次的流程味道一样
- 章尾必须给出明确方向：先看东三区这份名单怎么走，先确认谁被当成垫命的人
```

- [ ] **Step 3: Verify the Chapter 1-2 sync**

Run:

```bash
rg -n "有资格碰到更上层的记录|陈野那一夜|盯住东三区|名单怎么走|垫命的人" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md"
```

Expected: both chapters carry explicit investigation intent and an immediate next-step direction.

- [ ] **Step 4: Commit the Chapter 1-2 sync**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: retarget chapters 1-2 toward Chen Ye case"
```

Expected: one commit containing only Chapter 1 and Chapter 2 manuscript changes.

## Task 6: Sync Chapter 3 Through Chapter 5 Manuscripts To The New Mainline

**Files:**
- Modify: `novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md`
- Modify: `novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md`
- Modify: `novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md`

- [ ] **Step 1: Rewrite Chapter 3 so official contradiction becomes a case clue**

Chapter 3 must explicitly do all of the following:

```md
- 让宁烬看清学院和守夜不是两条无关的线，而是同一套筛选结构的不同面
- 沈夜璃要代表更冷更硬的真相侧，不是新的流程噪音
- 宁烬在本章结尾必须形成一个明确念头：要想查陈野那条线，就得摸到更核心的记录、名单或任务口径
```

- [ ] **Step 2: Rewrite Chapter 4 so sacrificial structure becomes personal evidence**

Chapter 4 must explicitly do all of the following:

```md
- 岳昆、卢小满等人不只是烘托危险，而是让宁烬看见“低位者先填命”的模板
- 观察、顺物资、记路线这些动作，要明确变成宁烬在为后续追线和下场做准备
- 章尾必须给出清晰方向：他下一步要记住谁在动表、谁在改名单、谁在把人往前送
```

- [ ] **Step 3: Rewrite Chapter 5 so descent is both rescue pressure and investigative inevitability**

Chapter 5 must explicitly do all of the following:

```md
- 学院想把宁烬挂起来、切出去、当成高危资产暂存，这既是打压，也是切断他靠近真相的路
- 苏清软公开站队时，要同时放大社会代价和“宁烬不能继续站外面”的压力
- 被困者、儿童舱和三号舱危机，必须直接撞到宁烬对陈野旧案的伤口
- 章尾仍然停在第一次真正点火开始，但读者必须明白：他下去不只是为了救人，也是因为他终于踩进了陈野那条路当年的真实入口
```

- [ ] **Step 4: Verify the Chapter 3-5 sync**

Run:

```bash
rg -n "同一套筛选结构|更核心的记录|谁在动表|谁在改名单|真实入口" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md"
```

Expected: Chapters 3 through 5 now tie official contradiction, sacrificial structure, and forced descent back to the Chen Ye line.

- [ ] **Step 5: Commit the Chapter 3-5 sync**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: retarget chapters 3-5 toward Chen Ye mainline"
```

Expected: one commit containing only Chapter 3 through Chapter 5 manuscript changes.

## Task 7: Cross-File Calibration And Revision Handoff

**Files:**
- Modify if needed: all files above
- Modify: `novels/武考第一夜，我被三个女人盯上了/.novel-state.json`
- Modify: `novels/武考第一夜，我被三个女人盯上了/06_反馈与修订.md`

- [ ] **Step 1: Run the cross-file wording audit**

Run:

```bash
rg -n "查清陈野之死|刀和门票|继续查下去的资格|今晚还会死人|谁在动表|真实入口" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/01B_总主线与卷级推进.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/02_大纲.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04A_开篇设计.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04_章节骨架.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md"
```

Expected: the case line appears in global docs and opening manuscripts, not only in one layer.

- [ ] **Step 2: Manually skim the chapter endings**

Run:

```bash
for f in \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md"; do
  echo "=== ${f##*/}";
  tail -n 20 "$f";
done
```

Expected: every chapter end points to a next move, not just a mood.

- [ ] **Step 3: Write the final revision-result summaries and gate**

Use this exact result summary in both state and revision log:

```md
已按新合同重排开篇发动机：把“查清陈野之死”前置为卷一明线，把武考第一、学院席位、守夜资格统一收束为宁烬继续查下去必须抢到手的刀和门票，并同步回写前五章的查案驱动、章尾方向与下场动因。
```

Set the workflow back to:

```md
当前修订 gate：awaiting_revision_result_approval
```

- [ ] **Step 4: Final verification**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace diff --stat
git -C /home/spencer/workspace/spencergo-marketplace status --short
```

Expected: only the planned files are modified or committed; no stray staging or unrelated deletions.

- [ ] **Step 5: Commit the final calibrated pass**

Run:

```bash
git -C /home/spencer/workspace/spencergo-marketplace add \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/.novel-state.json" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/06_反馈与修订.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/01B_总主线与卷级推进.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/02_大纲.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04A_开篇设计.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/04_章节骨架.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第1章_武考第一，不给你当狗了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第2章_第一夜，城裂开了.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第3章_借残印，杀出去.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第4章_第一名成了危险样本.md" \
  "/home/spencer/workspace/spencergo-marketplace/novels/武考第一夜，我被三个女人盯上了/manuscript/第5章_苏家小姐站在了他那边.md"
git -C /home/spencer/workspace/spencergo-marketplace commit -m "docs: refocus novel opening on Chen Ye mainline"
```

Expected: one final commit that represents a clean, internally consistent refocus pass.
