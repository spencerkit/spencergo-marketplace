#!/usr/bin/env node
/**
 * Test runner for spencergo skills
 * Supports multi-turn conversation with auto-answer
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execSync } = require("child_process");

const SCRIPT_DIR = process.argv[1] ? path.dirname(process.argv[1]) : __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, "../..");
const CASES_DIR = path.join(SCRIPT_DIR, "cases");
const PLUGIN_DIR = PROJECT_ROOT; // skills are in root/skills/
const OUTPUT_FILE = path.join(PROJECT_ROOT, "tests/output.md");

// Colors
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const BLUE = "\x1b[34m";
const NC = "\x1b[0m";

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
let skippedTests = 0;
let results = [];

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function escapeShell(str) {
  return str.replace(/'/g, "'\\''");
}

function printHeader(text) {
  console.log(`\n${BLUE}========================================${NC}`);
  console.log(`${BLUE}${text}${NC}`);
  console.log(`${BLUE}========================================${NC}`);
}

function formatConversation(messages) {
  let text = "";
  for (const msg of messages) {
    const prefix = msg.role === "user" ? "👤 User" : "🤖 Claude";
    const content =
      msg.content.length > 1500
        ? msg.content.substring(0, 1500) + "\n[...truncated...]"
        : msg.content;
    text += `${prefix}:\n${content}\n\n`;
    text += "---\n\n";
  }
  return text;
}

function addResult(skillName, testName, status, prompt, details, conversation) {
  results.push({
    skill: skillName,
    test: testName,
    status,
    prompt,
    details,
    conversation,
  });
}

function saveOutputMd() {
  let md = `# Test Results\n\n`;
  md += `Generated: ${new Date().toISOString()}\n\n`;
  md += `## Summary\n\n`;
  md += `- Total: ${totalTests}\n`;
  md += `- Passed: ${passedTests}\n`;
  md += `- Failed: ${failedTests}\n`;
  md += `- Skipped: ${skippedTests}\n\n`;
  md += `---\n\n`;

  let currentSkill = "";
  for (const r of results) {
    if (r.skill !== currentSkill) {
      currentSkill = r.skill;
      md += `## ${r.skill}\n\n`;
    }

    const statusIcon =
      r.status === "PASS" ? "✅" : r.status === "FAIL" ? "❌" : "⏭️";
    md += `### ${statusIcon} ${r.test}\n\n`;
    md += `**Prompt:** ${r.prompt}\n\n`;
    md += `**Status:** ${r.status}\n\n`;
    if (r.details) {
      md += `**Details:**\n\`\`\`\n${r.details}\n\`\`\`\n\n`;
    }
    if (r.conversation && r.conversation.length > 0) {
      md += `**Conversation:**\n\n`;
      md += formatConversation(r.conversation);
    }
    md += `---\n\n`;
  }

  fs.writeFileSync(OUTPUT_FILE, md);
  console.log(`\n${GREEN}Results saved to: ${OUTPUT_FILE}${NC}`);
}

// Check if response is asking a question (needs follow-up)
function isAskingQuestion(text) {
  const questionIndicators = [
    /\?$/m, // ends with ?
    /问题：/i, // question:
    /请问/i, // please tell me
    /是什么？/i, // what is?
    /怎么样？/i, // how is?
    /为什么？/i, // why?
    /可以告诉我/i, // can you tell me
    /需要先/i, // need to first
    /请先/i, // please first
    /先问/i, // first ask
    /\n\d+\./, // numbered list (likely questions)
  ];

  for (const pattern of questionIndicators) {
    if (pattern.test(text)) {
      return true;
    }
  }
  return false;
}

// Generate auto-answer based on question content
function generateAutoAnswer(questionText) {
  // Common patterns for naming questions
  if (
    questionText.includes("核心功能") ||
    questionText.includes("功能是什么")
  ) {
    return "是一个AI助手，帮助开发者提高效率";
  }
  if (questionText.includes("目标用户") || questionText.includes("用户是谁")) {
    return "开发者和技术团队";
  }
  if (questionText.includes("风格") || questionText.includes("想要什么风格")) {
    return "科技感、简洁、英文";
  }
  if (questionText.includes("关键词")) {
    return "AI、效率、代码";
  }
  if (questionText.includes("语言") || questionText.includes("中英")) {
    return "英文";
  }
  if (
    questionText.includes("宠物") ||
    questionText.includes("猫") ||
    questionText.includes("狗")
  ) {
    return "猫";
  }
  if (questionText.includes("公众号") || questionText.includes("文章")) {
    return "关于AI技术趋势的内容";
  }
  if (questionText.includes("占卜") || questionText.includes("卦")) {
    return "我的事业发展如何";
  }

  // Default answer
  return "继续";
}

function runMultiTurnTest(prompt, maxTurns = 5) {
  const messages = [];
  let currentPrompt = prompt;
  let fullOutput = "";

  for (let turn = 0; turn < maxTurns; turn++) {
    console.log(`  Turn ${turn + 1}...`);

    // Create temp directory for each turn
    const timestamp = Date.now() + turn;
    const testDir = path.join(os.tmpdir(), `claude-test-${timestamp}`);
    ensureDir(testDir);

    let output = "";
    try {
      const promptEscaped = escapeShell(currentPrompt);
      const cmd = `env -u CLAUDECODE claude -p '${promptEscaped}' \
        --permission-mode bypassPermissions \
        --add-dir '${testDir}' \
        --plugin-dir '${PLUGIN_DIR}' \
        --dangerously-skip-permissions`;

      output = execSync(cmd, {
        cwd: testDir,
        timeout: 30000,
        encoding: "utf-8",
        env: { ...process.env, CLAUDECODE: undefined },
      });
    } catch (e) {
      output = e.stdout || e.message || "";
    }

    // Cleanup
    try {
      fs.rmSync(testDir, { recursive: true, force: true });
    } catch (e) {}

    fullOutput += output + "\n\n";
    messages.push({ role: "user", content: currentPrompt });
    messages.push({ role: "assistant", content: output });

    // Check if AI is asking a question
    if (!isAskingQuestion(output) || turn >= maxTurns - 1) {
      // Done - either no more questions or reached max turns
      break;
    }

    // Generate auto-answer and continue
    currentPrompt = generateAutoAnswer(output);
    console.log(`    Auto-answer: ${currentPrompt}`);
  }

  return { fullOutput, messages };
}

function runTestCase(skillName, testCase) {
  const testName = testCase.name;
  const prompt = testCase.prompt;
  const expectedContains = testCase.expected_contains || [];
  const notExpected = testCase.not_expected || [];
  const maxTurns = testCase.max_turns || 5;

  totalTests++;

  console.log(`\n${BLUE}[${testName}]${NC}`);
  console.log(`Prompt: ${prompt}`);

  try {
    const { fullOutput, messages } = runMultiTurnTest(prompt, maxTurns);

    // Check expected contains
    let allPassed = true;
    let details = "";
    const checkContent = fullOutput.toLowerCase();

    for (const expected of expectedContains) {
      if (!checkContent.includes(expected.toLowerCase())) {
        details += `Missing expected: ${expected}\n`;
        allPassed = false;
      }
    }

    for (const unexpected of notExpected) {
      if (checkContent.includes(unexpected.toLowerCase())) {
        details += `Found unexpected: ${unexpected}\n`;
        allPassed = false;
      }
    }

    if (allPassed) {
      console.log(`${GREEN}[PASS]${NC}`);
      passedTests++;
      addResult(skillName, testName, "PASS", prompt, "", messages);
    } else {
      console.log(`${RED}[FAIL]${NC}`);
      console.log(details);
      failedTests++;
      addResult(skillName, testName, "FAIL", prompt, details, messages);
    }
  } catch (error) {
    console.log(`${RED}[FAIL]${NC} Error: ${error.message}`);
    failedTests++;
    addResult(skillName, testName, "FAIL", prompt, error.message, []);
  }
}

function runSkillTests(caseFile) {
  const skillName = path.basename(caseFile, ".json");

  const content = fs.readFileSync(caseFile, "utf-8");
  const data = JSON.parse(content);
  const testCases = data.test_cases || [];

  for (const testCase of testCases) {
    runTestCase(skillName, testCase);
  }
}

function main() {
  console.log(`${BLUE}========================================${NC}`);
  console.log(`${BLUE}spencergo Skills Test Suite (Multi-turn)${NC}`);
  console.log(`${BLUE}========================================${NC}`);

  if (!fs.existsSync(CASES_DIR)) {
    console.log(`${RED}Error: cases directory not found: ${CASES_DIR}${NC}`);
    process.exit(1);
  }

  const caseFiles = fs
    .readdirSync(CASES_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => path.join(CASES_DIR, f));

  for (const caseFile of caseFiles) {
    const skillName = path.basename(caseFile, ".json");
    printHeader(`Testing: ${skillName}`);
    runSkillTests(caseFile);
  }

  saveOutputMd();

  printHeader("Test Summary");
  console.log(`Total:  ${totalTests}`);
  console.log(`${GREEN}Passed: ${passedTests}${NC}`);
  console.log(`${RED}Failed: ${failedTests}${NC}`);
  console.log(`${YELLOW}Skipped: ${skippedTests}${NC}`);

  if (failedTests > 0) {
    process.exit(1);
  }
}

main();
