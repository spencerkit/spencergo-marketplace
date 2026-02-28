#!/usr/bin/env node
/**
 * Universal Skill Test Runner (V2)
 *
 * Dynamic testing approach:
 * - Reads SKILL.md to understand skill requirements
 * - Uses AI to determine next question based on skill flow
 * - Uses AI to determine if skill is complete
 *
 * Usage: node universal-test-runner.js [skills-dir] [--skill skill-name]
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execSync } = require("child_process");

// Configuration
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR);
const DEFAULT_SKILLS_DIR = path.join(PROJECT_ROOT, "skills");
const OUTPUT_FILE = path.join(PROJECT_ROOT, "tests-output.md");

// Check if running inside Claude Code
if (process.env.CLAUDECODE !== undefined) {
  console.log("\n⚠️  WARNING: Running inside Claude Code detected!");
  console.log("   Please run in a NORMAL TERMINAL:");
  console.log("   node universal-test-runner.js [skills-dir] [--skill name]");
  console.log("");
  process.exit(1);
}

// Colors
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const BLUE = "\x1b[34m";
const CYAN = "\x1b[36m";
const MAGENTA = "\x1b[35m";
const NC = "\x1b[0m";

// Test state
let results = [];

// Parse arguments
const args = process.argv.slice(2);
let skillsDir = DEFAULT_SKILLS_DIR;
let targetSkill = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--skill" && args[i + 1]) {
    targetSkill = args[i + 1];
    i++;
  } else if (!args[i].startsWith("--")) {
    skillsDir = path.isAbsolute(args[i]) ? args[i] : path.join(PROJECT_ROOT, args[i]);
  }
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function printHeader(text) {
  console.log(`\n${BLUE}========================================${NC}`);
  console.log(`${BLUE}${text}${NC}`);
  console.log(`${BLUE}========================================${NC}`);
}

// Discover all skills
function discoverSkills(dir) {
  const skills = [];
  if (!fs.existsSync(dir)) {
    console.log(`${RED}Error: Directory not found: ${dir}${NC}`);
    return skills;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.isDirectory()) {
      const skillPath = path.join(dir, entry.name);
      const skillMdPath = path.join(skillPath, "SKILL.md");
      if (fs.existsSync(skillMdPath)) {
        skills.push({ name: entry.name, path: skillPath, skillMdPath });
      }
    }
  }
  return skills;
}

// Read SKILL.md content
function readSkillContent(skillMdPath) {
  try {
    return fs.readFileSync(skillMdPath, "utf-8");
  } catch (e) {
    return "";
  }
}

// Run Claude
function runClaude(prompt, testDir, pluginDir = null) {
  const promptEscaped = prompt.replace(/'/g, "'\\''");
  let cmd = `env -u CLAUDECODE claude -p '${promptEscaped}' --permission-mode bypassPermissions --dangerously-skip-permissions`;

  if (pluginDir) {
    cmd += ` --add-dir '${testDir}' --plugin-dir '${pluginDir}'`;
  }

  try {
    return execSync(cmd, {
      cwd: testDir,
      timeout: 60000,
      encoding: "utf-8",
      env: { ...process.env, CLAUDECODE: undefined },
    });
  } catch (e) {
    return e.stdout || e.message || "";
  }
}

// Generate initial prompt using AI
function generateInitialPrompt(skillName, skillContent) {
  const prompt = `你是一个测试工程师。现在需要为一个 AI Skill 生成测试用的初始用户输入。

## Skill 信息
- **Skill 名称**: ${skillName}
- **SKILL.md 内容**:
${skillContent.slice(0, 3000)}

## 任务
根据 SKILL.md 内容，生成一个简短的用户输入（1-2句话），用于启动这个 skill 的测试。

要求：
1. 符合 skill 的使用场景
2. 足够简单，让 skill 能够开始工作
3. 只需要触发 skill，不需要完整信息

直接输出用户输入，不要有任何解释。`;

  const testDir = path.join(os.tmpdir(), `claude-gen-prompt-${Date.now()}`);
  ensureDir(testDir);
  const result = runClaude(prompt, testDir);
  fs.rmSync(testDir, { recursive: true, force: true });

  return result.split("\n").slice(0, 2).join(" ").trim() || `测试 ${skillName}`;
}

// Determine next question using AI
function determineNextQuestion(skillName, skillContent, conversationHistory) {
  const prompt = `你是一个测试工程师。你的任务是模拟用户与一个 AI Skill 对话。

## Skill 信息
- **Skill 名称**: ${skillName}
- **SKILL.md 内容** (理解 skill 需要什么信息):
${skillContent.slice(0, 4000)}

## 对话历史
${conversationHistory.map((msg, i) => `${i % 2 === 0 ? "User" : "Skill"}: ${msg}`).join("\n")}

## 任务
分析 Skill 最后一次回复，判断：
1. Skill 是否还在询问用户问题？
2. Skill 是否已经完成并给出了最终结果？

输出格式（直接输出，不要解释）:
---
NEXT_QUESTION: [如果还有问题，生成一个合理的用户回答]
STATUS: [IN_PROGRESS 或 COMPLETED]
---

如果 Skill 还在问问题，生成一个合理的用户回答继续对话。
如果 Skill 已经给出了最终结果/完成了任务，STATUS 设为 COMPLETED。`;

  const testDir = path.join(os.tmpdir(), `claude-next-q-${Date.now()}`);
  ensureDir(testDir);
  const result = runClaude(prompt, testDir);
  fs.rmSync(testDir, { recursive: true, force: true });

  // Parse result
  let nextQuestion = "继续";
  let status = "IN_PROGRESS";

  const lines = result.split("\n");
  for (const line of lines) {
    if (line.startsWith("NEXT_QUESTION:")) {
      nextQuestion = line.replace("NEXT_QUESTION:", "").trim();
    }
    if (line.startsWith("STATUS:")) {
      status = line.replace("STATUS:", "").trim();
    }
  }

  return { nextQuestion, status };
}

// Test a single skill
async function testSkill(skill, maxTurns = 20) {
  const { name: skillName, path: skillPath, skillMdPath } = skill;

  console.log(`\n${MAGENTA}[Testing: ${skillName}]${NC}`);

  // Read skill content
  const skillContent = readSkillContent(skillMdPath);
  console.log(`  ${CYAN}Reading SKILL.md...${NC}`);

  // Generate initial prompt
  console.log(`  ${CYAN}Generating initial prompt...${NC}`);
  const initialPrompt = generateInitialPrompt(skillName, skillContent);
  console.log(`  ${GREEN}Initial: ${initialPrompt}${NC}`);

  const messages = [];
  let currentPrompt = initialPrompt;
  let isCompleted = false;
  let fullOutput = "";

  for (let turn = 0; turn < maxTurns; turn++) {
    console.log(`\n  ${BLUE}Turn ${turn + 1}${NC}`);

    const testDir = path.join(os.tmpdir(), `skill-test-${Date.now()}-${turn}`);
    ensureDir(testDir);

    try {
      // Run skill (use PROJECT_ROOT as plugin-dir to find skills/)
      const output = runClaude(currentPrompt, testDir, PROJECT_ROOT);
      fullOutput += output + "\n\n";

      messages.push({ role: "user", content: currentPrompt });
      messages.push({ role: "assistant", content: output });

      // Preview
      const preview = output.split("\n").slice(0, 2).join(" ").slice(0, 80);
      console.log(`  ${CYAN}Skill: ${preview}...${NC}`);

      // Build conversation history for AI
      const conversationHistory = messages.map(m => m.content);

      // Ask AI to determine next step
      console.log(`  ${YELLOW}Determining next step...${NC}`);
      const { nextQuestion, status } = determineNextQuestion(skillName, skillContent, conversationHistory);

      if (status === "COMPLETED") {
        console.log(`  ${GREEN}✓ Skill completed!${NC}`);
        isCompleted = true;
        break;
      }

      // Continue with next question
      console.log(`  ${YELLOW}→ ${nextQuestion.slice(0, 50)}...${NC}`);
      currentPrompt = nextQuestion;

    } catch (e) {
      console.log(`  ${RED}Error: ${e.message}${NC}`);
      break;
    } finally {
      try { fs.rmSync(testDir, { recursive: true, force: true }); } catch (e) { }
    }
  }

  results.push({
    skill: skillName,
    initialPrompt,
    completed: isCompleted,
    turns: messages.length / 2,
    messages,
    fullOutput,
  });

  console.log(`\n  ${isCompleted ? GREEN + "✓ PASSED" : YELLOW + "⚠ INCOMPLETE"}${NC}`);
  return isCompleted;
}

// Save results
function saveOutput() {
  let md = `# Skill Test Results\n\n`;
  md += `Generated: ${new Date().toISOString()}\n\n`;
  md += `## Summary\n\n`;
  md += `- Total: ${results.length}\n`;
  md += `- Completed: ${results.filter(r => r.completed).length}\n`;
  md += `- Incomplete: ${results.filter(r => !r.completed).length}\n\n`;
  md += `---\n\n`;

  for (const r of results) {
    const icon = r.completed ? "✅" : "⚠️";
    md += `## ${icon} ${r.skill}\n\n`;
    md += `**Initial Prompt:** ${r.initialPrompt}\n\n`;
    md += `**Status:** ${r.completed ? "Completed" : "Incomplete"}\n\n`;
    md += `**Turns:** ${r.turns}\n\n`;
    md += `---\n\n`;
    md += `### Conversation\n\n`;

    for (const msg of r.messages) {
      const prefix = msg.role === "user" ? "👤 User" : "🤖 Skill";
      const content = msg.content.length > 600
        ? msg.content.substring(0, 600) + "\n[...truncated...]"
        : msg.content;
      md += `**${prefix}:**\n${content}\n\n---\n\n`;
    }
  }

  fs.writeFileSync(OUTPUT_FILE, md);
  console.log(`\n${GREEN}Results: ${OUTPUT_FILE}${NC}`);
}

// Main
async function main() {
  console.log(`${BLUE}========================================${NC}`);
  console.log(`${BLUE}Universal Skill Test Runner (V2)${NC}`);
  console.log(`${BLUE}========================================${NC}`);

  let skills = discoverSkills(skillsDir);

  if (targetSkill) {
    skills = skills.filter(s => s.name === targetSkill);
  }

  if (skills.length === 0) {
    console.log(`${RED}No skills found!${NC}`);
    process.exit(1);
  }

  console.log(`Found ${skills.length} skill(s): ${skills.map(s => s.name).join(", ")}`);

  for (const skill of skills) {
    await testSkill(skill);
  }

  saveOutput();

  const completed = results.filter(r => r.completed).length;
  const incomplete = results.filter(r => !r.completed).length;

  printHeader("Summary");
  console.log(`Total: ${results.length}`);
  console.log(`${GREEN}Completed: ${completed}${NC}`);
  console.log(`${YELLOW}Incomplete: ${incomplete}${NC}`);

  if (incomplete > 0) process.exit(1);
}

main().catch(e => {
  console.error(`${RED}Error: ${e.message}${NC}`);
  process.exit(1);
});
