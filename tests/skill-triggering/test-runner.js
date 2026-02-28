#!/usr/bin/env node
/**
 * Test runner for spencergo skills
 * Runs test cases and saves results to output.md with full conversation
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execSync } = require("child_process");

const SCRIPT_DIR = process.argv[1] ? path.dirname(process.argv[1]) : __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, "../..");
const CASES_DIR = path.join(SCRIPT_DIR, "cases");
const PLUGIN_DIR = path.join(PROJECT_ROOT, ".claude-plugin");
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

function extractConversation(sessionContent) {
  // Extract text from JSONL session
  const lines = sessionContent.split('\n').filter(l => l.trim());
  let conversation = [];

  for (const line of lines) {
    try {
      const msg = JSON.parse(line);
      if (msg.type === 'user') {
        // User message
        const content = msg.message?.content;
        if (Array.isArray(content)) {
          for (const c of content) {
            if (c.type === 'text') {
              conversation.push({ role: 'user', text: c.text });
            }
          }
        }
      } else if (msg.type === 'assistant') {
        // Assistant message
        const content = msg.message?.content;
        if (Array.isArray(content)) {
          let text = '';
          for (const c of content) {
            if (c.type === 'text') {
              text += c.text;
            }
          }
          if (text) {
            conversation.push({ role: 'assistant', text: text.substring(0, 2000) });
          }
        }
      }
    } catch (e) {}
  }

  return conversation;
}

function formatConversation(conversation) {
  let text = '';
  for (const msg of conversation) {
    const prefix = msg.role === 'user' ? '👤 User' : '🤖 Assistant';
    text += `${prefix}:\n${msg.text}\n\n`;
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
    conversation
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

    const statusIcon = r.status === "PASS" ? "✅" : r.status === "FAIL" ? "❌" : "⏭️";
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

function runTestCase(skillName, testCase) {
  const testName = testCase.name;
  const prompt = testCase.prompt;
  const expectedContains = testCase.expected_contains || [];
  const notExpected = testCase.not_expected || [];
  const timeout = testCase.timeout || 60;

  totalTests++;

  console.log(`\n${BLUE}[${testName}]${NC}`);
  console.log(`Prompt: ${prompt}`);

  // Create temp directory
  const timestamp = Date.now();
  const testDir = path.join(os.tmpdir(), `claude-test-${timestamp}`);
  ensureDir(testDir);

  let conversation = [];

  try {
    // Run Claude
    const promptEscaped = escapeShell(prompt);
    const cmd = `env -u CLAUDECODE claude -p '${promptEscaped}' \
      --permission-mode bypassPermissions \
      --add-dir '${testDir}' \
      --plugin-dir '${PLUGIN_DIR}' \
      --dangerously-skip-permissions`;

    try {
      execSync(cmd, {
        cwd: testDir,
        timeout: timeout * 1000,
        stdio: "pipe",
        env: { ...process.env, CLAUDECODE: undefined }
      });
    } catch (e) {
      // Ignore timeout/error, continue
    }

    // Find session file
    const projectEscaped = testDir.replace(/\//g, "-").replace(/^-/, "-");
    const sessionDir = path.join(os.homedir(), ".claude/projects", projectEscaped);

    let sessionContent = "";

    if (fs.existsSync(sessionDir)) {
      const files = fs.readdirSync(sessionDir)
        .filter(f => f.endsWith(".jsonl"))
        .sort()
        .reverse();
      if (files.length > 0) {
        sessionContent = fs.readFileSync(path.join(sessionDir, files[0]), "utf-8");
        conversation = extractConversation(sessionContent);
      }
    }

    if (!sessionContent) {
      console.log(`${YELLOW}[SKIP]${NC} Could not find session`);
      skippedTests++;
      addResult(skillName, testName, "SKIP", prompt, "Session file not found", []);
      return;
    }

    // Check expected contains
    let allPassed = true;
    let details = "";

    for (const expected of expectedContains) {
      if (!sessionContent.toLowerCase().includes(expected.toLowerCase())) {
        details += `Missing expected: ${expected}\n`;
        allPassed = false;
      }
    }

    for (const unexpected of notExpected) {
      if (sessionContent.toLowerCase().includes(unexpected.toLowerCase())) {
        details += `Found unexpected: ${unexpected}\n`;
        allPassed = false;
      }
    }

    if (allPassed) {
      console.log(`${GREEN}[PASS]${NC}`);
      passedTests++;
      addResult(skillName, testName, "PASS", prompt, "", conversation);
    } else {
      console.log(`${RED}[FAIL]${NC}`);
      console.log(details);
      failedTests++;
      addResult(skillName, testName, "FAIL", prompt, details, conversation);
    }

  } catch (error) {
    console.log(`${RED}[FAIL]${NC} Error: ${error.message}`);
    failedTests++;
    addResult(skillName, testName, "FAIL", prompt, error.message, conversation);
  } finally {
    // Cleanup
    try {
      fs.rmSync(testDir, { recursive: true, force: true });
    } catch (e) {}
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
  console.log(`${BLUE}spencergo Skills Test Suite${NC}`);
  console.log(`${BLUE}========================================${NC}`);

  // Check prerequisites
  if (!fs.existsSync(CASES_DIR)) {
    console.log(`${RED}Error: cases directory not found: ${CASES_DIR}${NC}`);
    process.exit(1);
  }

  // Get all case files
  const caseFiles = fs.readdirSync(CASES_DIR)
    .filter(f => f.endsWith(".json"))
    .map(f => path.join(CASES_DIR, f));

  for (const caseFile of caseFiles) {
    const skillName = path.basename(caseFile, ".json");
    printHeader(`Testing: ${skillName}`);
    runSkillTests(caseFile);
  }

  // Save output.md
  saveOutputMd();

  // Print summary
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
