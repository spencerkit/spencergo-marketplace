#!/usr/bin/env node
/**
 * Parse test cases from JSON files.
 * Usage: node parse-test-cases.js <json-file> [test-name]
 */

const fs = require('fs');

const args = process.argv.slice(2);
const jsonFile = args[0];
const testName = args[1];

if (!jsonFile) {
  console.error('Usage: node parse-test-cases.js <json-file> [test-name]');
  process.exit(1);
}

const content = fs.readFileSync(jsonFile, 'utf-8');
const data = JSON.parse(content);

const testCases = data.test_cases || [];

if (testName) {
  // Return specific test case
  const testCase = testCases.find(tc => tc.name === testName);
  if (testCase) {
    console.log(JSON.stringify(testCase));
  }
} else {
  // Return all test cases
  console.log(JSON.stringify(testCases));
}
