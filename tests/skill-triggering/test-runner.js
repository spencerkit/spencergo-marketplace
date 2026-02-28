#!/usr/bin/env node
/**
 * Test runner for spencergo skills
 * Runs test cases defined in JSON files
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execSync } = require("child_process");

const SCRIPT_DIR = process.argv[1] ? path.dirname(process.argv[1]) : __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, "../..");
const CASES_DIR = path.join(SCRIPT_DIR, "cases");
const PLUGIN_DIR = path.join(PROJECT_ROOT, ".claude-plugin");
const TEST_RESULTS_DIR = path.join(PROJECT_ROOT, "tests/test-results");

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

function runTestCase(skillName, testCase) {
  const testName = testCase.name;
  const prompt = testCase.prompt;
  const expectedContains = testCase.expected_contains || [];
  const notExpected = testCase.not_expected || [];
  const timeout = testCase.timeout || 60;

  totalTests++;

  console.log(`\n${BLUE}[${testName}]${NC}`);
  console.log(`Prompt: ${prompt}`);

  // Create test directory
  const timestamp = Date.now();
  const testDir = path.join(
    TEST_RESULTS_DIR,
    `${skillName}-${testName}-${timestamp}`,
  );
  ensureDir(testDir);

  const outputFile = path.join(testDir, "output.txt");

  try {
    // Run Claude - unset CLAUDECODE to allow nested sessions
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
        env: { ...process.env, CLAUDECODE: undefined },
      });
    } catch (e) {
      // Ignore timeout errors, continue to check session
    }

    // Write output (if any)
    if (fs.existsSync(outputFile)) {
      // Output already written by stdio
    }

    // Find session file - Claude encodes paths with leading hyphen
    const projectEscaped = "-" + testDir.replace(/\//g, "-");
    const sessionDir = path.join(
      os.homedir(),
      ".claude/projects",
      projectEscaped,
    );

    let sessionFile = "";
    if (fs.existsSync(sessionDir)) {
      const files = fs
        .readdirSync(sessionDir)
        .filter((f) => f.endsWith(".jsonl"))
        .sort()
        .reverse();
      if (files.length > 0) {
        sessionFile = path.join(sessionDir, files[0]);
      }
    }

    if (!sessionFile) {
      console.log(`${YELLOW}[SKIP]${NC} Could not find session file`);
      console.log(`  Results: ${testDir}`);
      skippedTests++;
      return;
    }

    // Copy session to test results
    fs.copyFileSync(sessionFile, path.join(testDir, "session.jsonl"));

    // Read session content
    const sessionContent = fs.readFileSync(sessionFile, "utf-8");

    // Check expected contains
    let allPassed = true;

    for (const expected of expectedContains) {
      if (!sessionContent.toLowerCase().includes(expected.toLowerCase())) {
        console.log(`${RED}  Missing expected: ${expected}${NC}`);
        allPassed = false;
      }
    }

    // Check not expected
    for (const unexpected of notExpected) {
      if (sessionContent.toLowerCase().includes(unexpected.toLowerCase())) {
        console.log(`${RED}  Found unexpected: ${unexpected}${NC}`);
        allPassed = false;
      }
    }

    if (allPassed) {
      console.log(`${GREEN}[PASS]${NC}`);
      passedTests++;
    } else {
      console.log(`${RED}[FAIL]${NC}`);
      failedTests++;
    }

    console.log(`  Results: ${testDir}`);
  } catch (error) {
    console.log(`${RED}[FAIL]${NC} Test error: ${error.message}`);
    console.log(`  Results: ${testDir}`);
    failedTests++;
  }
}

function runSkillTests(caseFile) {
  const skillName = path.basename(caseFile, ".json");
  printHeader(`Testing: ${skillName}`);

  const content = fs.readFileSync(caseFile, "utf-8");
  const data = JSON.parse(content);
  const testCases = data.test_cases || [];

  for (const testCase of testCases) {
    runTestCase(skillName, testCase);
  }
}

function main() {
  ensureDir(TEST_RESULTS_DIR);

  // Get all case files
  const caseFiles = fs
    .readdirSync(CASES_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => path.join(CASES_DIR, f));

  for (const caseFile of caseFiles) {
    runSkillTests(caseFile);
  }

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
